import importlib.util
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RUNTIME_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "bluetape_runtime.py"
)
MANIFEST_PATH = (
    Path(__file__).resolve().parents[1] / "references" / "workflow-manifest.json"
)


def load_runtime():
    spec = importlib.util.spec_from_file_location(
        "bluetape_runtime_receipt", RUNTIME_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReceiptTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = load_runtime()
        canonical = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        cls.manifest = copy.deepcopy(canonical)
        cls.manifest["manifest_version"] = "1.0.0"
        cls.manifest["receipt"]["event_types"] = list(
            cls.runtime.PHASE1_EVENT_TYPES
        )
        cls.manifest.pop("compatible_manifest_versions", None)
        cls.manifest.pop("resource_limits", None)
        cls.manifest_hash = cls.runtime.manifest_hash(cls.manifest)

    def make_run_dir(self, parent, name="run-1"):
        run_dir = Path(parent) / name
        run_dir.mkdir()
        (run_dir / "manifest.json").write_text(
            self.runtime.canonical_json(self.manifest) + "\n", encoding="utf-8"
        )
        return run_dir

    def append_two_events(self, run_dir):
        first = self.runtime.append_receipt_event(
            run_dir,
            "run_created",
            owner_token="owner-1",
            manifest_hash=self.manifest_hash,
            evidence_refs=[],
            to_state="planned",
            timestamp="2026-07-14T00:00:00Z",
        )
        second = self.runtime.append_receipt_event(
            run_dir,
            "run_started",
            owner_token="owner-1",
            manifest_hash=self.manifest_hash,
            evidence_refs=[{"kind": "inspection", "summary": "approved"}],
            from_state="approved",
            to_state="running",
            timestamp="2026-07-14T00:01:00Z",
        )
        return first, second

    def test_append_builds_a_verifiable_checksum_chain(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run_dir(temp_dir)
            first, second = self.append_two_events(run_dir)

            self.assertEqual(1, first["sequence"])
            self.assertEqual(first["checksum"], second["previous_checksum"])
            self.assertEqual([first, second], self.runtime.verify_receipt(run_dir))

    def test_append_retries_short_os_writes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "receipt.jsonl"
            original_write = self.runtime.os.write

            def short_write(descriptor, payload):
                return original_write(descriptor, payload[: max(1, len(payload) // 3)])

            with mock.patch.object(self.runtime.os, "write", side_effect=short_write):
                self.runtime._append_json_line(target, {"event": "complete"})

            self.assertEqual(
                self.runtime.canonical_json({"event": "complete"}) + "\n",
                target.read_text(encoding="utf-8"),
            )

    def test_corruption_names_the_first_bad_sequence(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run_dir(temp_dir)
            self.append_two_events(run_dir)
            receipt_path = run_dir / "receipt.jsonl"
            events = [
                json.loads(line)
                for line in receipt_path.read_text(encoding="utf-8").splitlines()
            ]
            events[0]["reason"] = "mutated"
            receipt_path.write_text(
                "\n".join(self.runtime.canonical_json(event) for event in events)
                + "\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(
                self.runtime.ReceiptCorrupt, "sequence 1"
            ):
                self.runtime.verify_receipt(run_dir)

    def test_rebuild_restores_the_latest_snapshot(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run_dir(temp_dir)
            _, second = self.append_two_events(run_dir)
            (run_dir / "run.json").unlink()

            snapshot = self.runtime.rebuild_run_snapshot(run_dir)

            self.assertEqual("run_started", snapshot["last_event_type"])
            self.assertEqual(2, snapshot["last_sequence"])
            self.assertEqual(second["checksum"], snapshot["last_checksum"])
            self.assertEqual("running", snapshot["state"])
            self.assertEqual(
                snapshot,
                json.loads((run_dir / "run.json").read_text(encoding="utf-8")),
            )

    def test_rejects_raw_output_before_mutating_the_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run_dir(temp_dir)
            self.append_two_events(run_dir)
            receipt_path = run_dir / "receipt.jsonl"
            original = receipt_path.read_bytes()

            with self.assertRaises(ValueError):
                self.runtime.append_receipt_event(
                    run_dir,
                    "evidence_attached",
                    owner_token="owner-1",
                    manifest_hash=self.manifest_hash,
                    evidence_refs=[
                        {
                            "kind": "command",
                            "summary": "targeted test",
                            "raw_output": "must not be persisted",
                        }
                    ],
                )

            self.assertEqual(original, receipt_path.read_bytes())

    def test_rejects_oversized_summary_before_mutating_the_receipt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_dir = self.make_run_dir(temp_dir)
            self.append_two_events(run_dir)
            receipt_path = run_dir / "receipt.jsonl"
            original = receipt_path.read_bytes()

            with self.assertRaises(ValueError):
                self.runtime.append_receipt_event(
                    run_dir,
                    "evidence_attached",
                    owner_token="owner-1",
                    manifest_hash=self.manifest_hash,
                    evidence_refs=[{"kind": "command", "summary": "x" * 501}],
                )

            self.assertEqual(original, receipt_path.read_bytes())

    def test_verify_rejects_identity_changes_even_with_valid_checksums(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for field, value in (
                ("run_id", "other-run"),
                ("manifest_hash", "b" * 64),
            ):
                with self.subTest(field=field):
                    run_dir = self.make_run_dir(temp_dir, name="run-" + field)
                    first, second = self.append_two_events(run_dir)
                    second[field] = value
                    second["checksum"] = self.runtime._event_checksum(second)
                    (run_dir / "receipt.jsonl").write_text(
                        self.runtime.canonical_json(first)
                        + "\n"
                        + self.runtime.canonical_json(second)
                        + "\n",
                        encoding="utf-8",
                    )

                    with self.assertRaisesRegex(
                        self.runtime.ReceiptCorrupt, "sequence 2"
                    ):
                        self.runtime.verify_receipt(run_dir)

    def test_verify_rejects_schema_drift_even_with_valid_checksums(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            for name, mutate in (
                (
                    "event-type",
                    lambda event: event.update({"event_type": "unregistered_event"}),
                ),
                (
                    "additional-field",
                    lambda event: event.update({"raw_output": "forbidden"}),
                ),
            ):
                with self.subTest(name=name):
                    run_dir = self.make_run_dir(temp_dir, name="run-" + name)
                    first, second = self.append_two_events(run_dir)
                    mutate(second)
                    second["checksum"] = self.runtime._event_checksum(second)
                    (run_dir / "receipt.jsonl").write_text(
                        self.runtime.canonical_json(first)
                        + "\n"
                        + self.runtime.canonical_json(second)
                        + "\n",
                        encoding="utf-8",
                    )

                    with self.assertRaisesRegex(
                        self.runtime.ReceiptCorrupt, "sequence 2"
                    ):
                        self.runtime.verify_receipt(run_dir)

    def test_initialize_run_creates_a_complete_workspace_run(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_root = Path(temp_dir) / ".bluetape"
            repo_root = Path(temp_dir) / "repo"
            repo_root.mkdir()
            owner_file = state_root / "handles" / "phase2.owner"

            initialized = self.runtime.initialize_run(
                state_root,
                workflow_type="A",
                repo_root=repo_root,
                component_ids=["manifest", "receipt", "manifest"],
                owner_file=owner_file,
                manifest_path=MANIFEST_PATH,
            )
            run_dir = state_root / "runs" / initialized["run_id"]

            self.assertTrue((state_root / "config.json").is_file())
            self.assertTrue((run_dir / "manifest.json").is_file())
            self.assertTrue((run_dir / "run.json").is_file())
            self.assertTrue((run_dir / "receipt.jsonl").is_file())
            self.assertTrue((run_dir / "lanes").is_dir())
            self.assertTrue((run_dir / "heartbeats").is_dir())
            snapshot = json.loads(
                (run_dir / "manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual("A", snapshot["_run"]["workflow_type"])
            self.assertEqual(
                ["manifest", "receipt"], snapshot["_run"]["component_ids"]
            )
            self.assertEqual(str(repo_root.resolve()), snapshot["_run"]["repo_root"])
            self.assertNotIn("owner_token", snapshot["_run"])
            self.assertEqual(1, snapshot["_run"]["owner_epoch"])
            events = self.runtime.verify_receipt(run_dir)
            self.assertEqual("run_created", events[0]["event_type"])

    def test_initialize_run_rejects_unknown_workflow_and_empty_component(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_root = Path(temp_dir) / ".bluetape"
            owner_file = state_root / "handles" / "phase2.owner"

            with self.assertRaises(ValueError):
                self.runtime.initialize_run(
                    state_root,
                    workflow_type="Z",
                    repo_root=temp_dir,
                    component_ids=["manifest"],
                    owner_file=owner_file,
                    manifest_path=MANIFEST_PATH,
                )
            with self.assertRaises(ValueError):
                self.runtime.initialize_run(
                    state_root,
                    workflow_type="A",
                    repo_root=temp_dir,
                    component_ids=["manifest", ""],
                    owner_file=owner_file,
                    manifest_path=MANIFEST_PATH,
                )

    def test_incompatible_manifest_is_never_rewritten(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_root = Path(temp_dir) / ".bluetape"
            for field, value in (
                ("schema_version", 2),
                ("manifest_version", "2.0.0"),
            ):
                with self.subTest(field=field):
                    owner_file = state_root / "handles" / (field + ".owner")
                    initialized = self.runtime.initialize_run(
                        state_root,
                        workflow_type="A",
                        repo_root=temp_dir,
                        component_ids=[field],
                        owner_file=owner_file,
                        manifest_path=MANIFEST_PATH,
                    )
                    run_dir = state_root / "runs" / initialized["run_id"]
                    manifest_path = run_dir / "manifest.json"
                    snapshot = json.loads(manifest_path.read_text(encoding="utf-8"))
                    snapshot[field] = value
                    manifest_path.write_text(
                        self.runtime.canonical_json(snapshot) + "\n",
                        encoding="utf-8",
                    )
                    incompatible_bytes = manifest_path.read_bytes()

                    for operation in (
                        self.runtime.verify_receipt,
                        self.runtime.rebuild_run_snapshot,
                    ):
                        with self.assertRaises(self.runtime.IncompatibleManifest):
                            operation(run_dir)
                    self.assertEqual(incompatible_bytes, manifest_path.read_bytes())


if __name__ == "__main__":
    unittest.main()
