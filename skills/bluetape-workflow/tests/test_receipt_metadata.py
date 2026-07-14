import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
RUNTIME_PATH = SKILL_ROOT / "scripts" / "bluetape_runtime.py"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"


def load_runtime():
    spec = importlib.util.spec_from_file_location(
        "bluetape_runtime_receipt_metadata", RUNTIME_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ReceiptMetadataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()

    def phase1_event(self):
        event = {
            "schema_version": 1,
            "run_id": "run-1",
            "lane_id": None,
            "agent_id": None,
            "sequence": 1,
            "event_type": "run_created",
            "from_state": None,
            "to_state": "planned",
            "timestamp": "2026-07-14T00:00:00Z",
            "owner_token": "legacy-owner",
            "manifest_hash": "a" * 64,
            "previous_checksum": "",
            "checksum": "",
            "evidence_refs": [],
            "reason": None,
        }
        event["checksum"] = self.runtime._event_checksum(event)
        return event

    def make_phase1_run(self, parent):
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest["manifest_version"] = "1.0.0"
        manifest["receipt"]["event_types"] = list(
            self.runtime.PHASE1_EVENT_TYPES
        )
        manifest.pop("resource_limits", None)
        run_dir = Path(parent) / "run-1"
        run_dir.mkdir(mode=0o700)
        (run_dir / "manifest.json").write_text(
            self.runtime.canonical_json(manifest) + "\n", encoding="utf-8"
        )
        return run_dir, self.runtime.manifest_hash(manifest)

    def test_phase1_event_without_metadata_remains_valid(self):
        event = self.phase1_event()
        self.runtime._validate_receipt_event_contract(
            event, manifest_version="1.0"
        )
        self.assertNotIn("metadata", event)

    def test_metadata_rejects_unknown_and_raw_output_fields(self):
        for metadata in ({"unknown": "x"}, {"raw_output": "secret"}):
            with self.subTest(metadata=metadata):
                with self.assertRaisesRegex(ValueError, "unsupported metadata"):
                    self.runtime._validate_event_metadata(
                        "lane_created",
                        metadata,
                        manifest_version="1.1",
                        current_owner_epoch=1,
                    )

    def test_new_event_is_rejected_by_old_manifest_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir, manifest_hash = self.make_phase1_run(temp_dir)
            with self.assertRaisesRegex(
                ValueError, "run manifest does not allow event"
            ):
                self.runtime.append_receipt_event(
                    run_dir,
                    "run_resumed",
                    owner_token="legacy-owner",
                    manifest_hash=manifest_hash,
                    evidence_refs=[
                        {"kind": "approval", "summary": "resume approved"}
                    ],
                    metadata={
                        "new_owner_fingerprint": "b" * 64,
                        "owner_epoch": 2,
                    },
                )

    def test_transaction_rejects_reversed_or_nested_intents(self):
        heartbeat = {
            "event_type": "heartbeat_observed",
            "timestamp": "2026-07-14T00:00:00Z",
            "owner_epoch": 1,
            "from_state": "running",
            "to_state": "running",
            "lane_id": "lane-1",
            "agent_id": "agent-1",
            "reason": None,
            "evidence_refs": [{"kind": "artifact", "summary": "fresh"}],
            "metadata": {"owner_epoch": 1, "evidence_digest": "a" * 64},
        }
        lease = {
            **heartbeat,
            "event_type": "lease_renewed",
            "metadata": {
                "owner_epoch": 1,
                "silence_lease_deadline": "2026-07-14T00:10:00Z",
                "evidence_digest": "a" * 64,
            },
        }
        with self.assertRaisesRegex(ValueError, "transaction intent pair"):
            self.runtime._validate_event_metadata(
                "transaction_committed",
                {"owner_epoch": 1, "intents": [lease, heartbeat]},
                manifest_version="1.1",
                current_owner_epoch=1,
            )
        nested = dict(heartbeat)
        nested["event_type"] = "transaction_committed"
        with self.assertRaisesRegex(ValueError, "transaction intent"):
            self.runtime._validate_event_metadata(
                "transaction_committed",
                {"owner_epoch": 1, "intents": [nested, lease]},
                manifest_version="1.1",
                current_owner_epoch=1,
            )

    def test_evidence_limits_and_digest_are_deterministic(self):
        evidence = [{"kind": "artifact", "summary": "bounded"}]
        self.assertEqual(
            self.runtime.evidence_digest(evidence),
            self.runtime.evidence_digest(list(evidence)),
        )
        with self.assertRaisesRegex(ValueError, "at most 8"):
            self.runtime.evidence_digest(evidence * 9)

    def test_encoded_line_limit_rejects_before_receipt_mutation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            state_root = root / ".bluetape"
            repo_root = root / "repo"
            repo_root.mkdir()
            manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
            manifest["resource_limits"]["max_receipt_line_bytes"] = 1024
            manifest_path = root / "small-manifest.json"
            manifest_path.write_text(
                self.runtime.canonical_json(manifest) + "\n", encoding="utf-8"
            )
            owner_file = state_root / "handles" / "phase2.owner"
            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["runtime"],
                owner_file=owner_file,
                manifest_path=manifest_path,
            )
            run_dir = state_root / "runs" / initialized["run_id"]
            receipt_path = run_dir / "receipt.jsonl"
            original = receipt_path.read_bytes()

            with self.assertRaisesRegex(
                ValueError, "max_receipt_line_bytes"
            ):
                self.runtime.append_receipt_event(
                    run_dir,
                    "run_started",
                    owner_handle=owner_file,
                    manifest_hash=initialized["manifest_hash"],
                    evidence_refs=[
                        {
                            "kind": "artifact",
                            "summary": "x" * 256,
                            "path": "p" * 256,
                            "checksum": "a" * 64,
                        }
                        for _ in range(8)
                    ],
                    from_state="approved",
                    to_state="running",
                    timestamp="2026-07-14T00:01:00Z",
                    metadata={"owner_epoch": 1},
                )

            self.assertEqual(original, receipt_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
