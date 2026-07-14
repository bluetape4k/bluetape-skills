import importlib
import sys
import tempfile
import tracemalloc
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class CoordinatorScaleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.runtime = importlib.import_module("bluetape_runtime")
        cls.coordinator = importlib.import_module("bluetape_coordinator")

    def make_receipt(self, root, event_count):
        state_root = root / ("state-" + str(event_count))
        repo_root = root / ("repo-" + str(event_count))
        repo_root.mkdir()
        owner_file = state_root / "handles" / "scale.owner"
        initialized = self.runtime.initialize_run(
            state_root,
            workflow_type="A",
            repo_root=repo_root,
            component_ids=["runtime"],
            owner_file=owner_file,
            manifest_path=MANIFEST_PATH,
        )
        run_dir = state_root / "runs" / initialized["run_id"]
        manifest = self.runtime.load_run_manifest_snapshot(run_dir)
        fingerprint = manifest["run"]["owner_fingerprint"]
        events = self.runtime.verify_receipt(run_dir)
        previous = events[-1]["checksum"]
        sequence = 2
        templates = [
            ("plan_approved", None, None, "planned", "approved", {"owner_epoch": 1}),
            ("run_started", None, None, "approved", "running", {"owner_epoch": 1}),
            (
                "lane_created", "scale", "agent-1", None, "pending",
                {
                    "owner_epoch": 1,
                    "assignment": "scale replay",
                    "write_scope": [],
                    "fallback": "main session",
                    "startup_ack_deadline": "2026-07-14T00:01:00Z",
                    "command_deadline": "2026-07-14T01:00:00Z",
                    "parent_lane_id": None,
                    "replacement_count": 0,
                },
            ),
            ("lane_started", "scale", "agent-1", "pending", "starting", {"owner_epoch": 1}),
            ("startup_ack", "scale", "agent-1", "starting", "running", {"owner_epoch": 1}),
        ]
        receipt = run_dir / "receipt.jsonl"
        with receipt.open("a", encoding="utf-8") as stream:
            for event_type, lane_id, agent_id, source, target, metadata in templates:
                event = {
                    "schema_version": 1,
                    "run_id": run_dir.name,
                    "lane_id": lane_id,
                    "agent_id": agent_id,
                    "sequence": sequence,
                    "event_type": event_type,
                    "from_state": source,
                    "to_state": target,
                    "timestamp": "2026-07-14T00:00:00Z",
                    "owner_token": fingerprint,
                    "manifest_hash": initialized["manifest_hash"],
                    "previous_checksum": previous,
                    "checksum": "",
                    "evidence_refs": [{"kind": "test", "summary": event_type}],
                    "reason": None,
                    "metadata": metadata,
                }
                event["checksum"] = self.runtime._event_checksum(event)
                stream.write(self.runtime.canonical_json(event) + "\n")
                previous = event["checksum"]
                sequence += 1
            while sequence <= event_count:
                event = {
                    "schema_version": 1,
                    "run_id": run_dir.name,
                    "lane_id": "scale",
                    "agent_id": "agent-1",
                    "sequence": sequence,
                    "event_type": "heartbeat_observed",
                    "from_state": "running",
                    "to_state": "running",
                    "timestamp": "2026-07-14T00:00:00Z",
                    "owner_token": fingerprint,
                    "manifest_hash": initialized["manifest_hash"],
                    "previous_checksum": previous,
                    "checksum": "",
                    "evidence_refs": [{"kind": "test", "summary": "fresh"}],
                    "reason": None,
                    "metadata": {"owner_epoch": 1, "evidence_digest": "a" * 64},
                }
                event["checksum"] = self.runtime._event_checksum(event)
                stream.write(self.runtime.canonical_json(event) + "\n")
                previous = event["checksum"]
                sequence += 1
        return run_dir, previous

    def replay_peak(self, run_dir):
        snapshot = self.runtime.load_run_manifest_snapshot(run_dir)
        tracemalloc.start()
        state = self.coordinator.replay_coordinator_state(
            self.runtime.iter_verified_receipt(run_dir), snapshot
        )
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return state, peak

    def test_streams_ten_and_twenty_thousand_events_with_linear_memory(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            ten_dir, ten_checksum = self.make_receipt(root, 10000)
            twenty_dir, twenty_checksum = self.make_receipt(root, 20000)

            ten_state, ten_peak = self.replay_peak(ten_dir)
            twenty_state, twenty_peak = self.replay_peak(twenty_dir)

            self.assertEqual(10000, ten_state["last_sequence"])
            self.assertEqual(ten_checksum, ten_state["last_checksum"])
            self.assertEqual(20000, twenty_state["last_sequence"])
            self.assertEqual(twenty_checksum, twenty_state["last_checksum"])
            self.assertLessEqual(twenty_peak, ten_peak * 2.5)

    def test_oversized_line_fails_before_json_decode(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir, _ = self.make_receipt(root, 6)
            receipt = run_dir / "receipt.jsonl"
            with receipt.open("ab") as stream:
                stream.write(b"{" + b"x" * 65536 + b"}\n")
            with self.assertRaisesRegex(
                self.runtime.ReceiptCorrupt, "sequence 7: event too large"
            ):
                list(self.runtime.iter_verified_receipt(run_dir))

    def test_transaction_append_faults_never_apply_a_partial_intent(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir, old_checksum = self.make_receipt(root, 6)
            manifest = self.runtime.load_run_manifest_snapshot(run_dir)
            old_bytes = (run_dir / "receipt.jsonl").read_bytes()
            owner_file = root / "state-6" / "handles" / "scale.owner"
            self.runtime.mutate_receipt(
                run_dir,
                owner_file,
                lambda _state: [
                    {
                        "event_type": "heartbeat_observed",
                        "lane_id": "scale",
                        "agent_id": "agent-1",
                        "from_state": "running",
                        "to_state": "running",
                        "evidence_refs": [{"kind": "test", "summary": "heartbeat"}],
                        "metadata": {"owner_epoch": 1, "evidence_digest": "b" * 64},
                    },
                    {
                        "event_type": "lease_renewed",
                        "lane_id": "scale",
                        "agent_id": "agent-1",
                        "from_state": "running",
                        "to_state": "running",
                        "evidence_refs": [{"kind": "test", "summary": "lease"}],
                        "metadata": {
                            "owner_epoch": 1,
                            "silence_lease_deadline": "2026-07-14T02:00:00Z",
                            "evidence_digest": "b" * 64,
                        },
                    },
                ],
                expected_head=old_checksum,
            )
            complete_bytes = (run_dir / "receipt.jsonl").read_bytes()
            envelope = complete_bytes[len(old_bytes) :]
            receipt = run_dir / "receipt.jsonl"

            for offset in range(len(envelope) + 1):
                receipt.write_bytes(old_bytes + envelope[:offset])
                if offset == 0:
                    state = self.coordinator.replay_coordinator_state(
                        self.runtime.iter_verified_receipt(run_dir), manifest
                    )
                    self.assertIsNone(
                        state["lanes"]["scale"]["silence_lease_deadline"]
                    )
                elif offset < len(envelope):
                    with self.assertRaises(self.runtime.ReceiptCorrupt) as raised:
                        list(self.runtime.iter_verified_receipt(run_dir))
                    self.assertEqual(6, raised.exception.last_trusted_sequence)
                    self.assertEqual(
                        old_checksum, raised.exception.last_trusted_checksum
                    )
                else:
                    state = self.coordinator.replay_coordinator_state(
                        self.runtime.iter_verified_receipt(run_dir), manifest
                    )
                    self.assertEqual(
                        "2026-07-14T02:00:00Z",
                        state["lanes"]["scale"]["silence_lease_deadline"],
                    )

    def test_read_and_mutations_each_stream_once_and_write_changed_cache_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            run_dir, head = self.make_receipt(root, 6)
            owner_file = root / "state-6" / "handles" / "scale.owner"
            original_public_iter = self.runtime.iter_verified_receipt
            public_scans = []

            def counted_public_iter(selected_run_dir):
                public_scans.append(Path(selected_run_dir))
                return original_public_iter(selected_run_dir)

            self.runtime.iter_verified_receipt = counted_public_iter
            try:
                self.coordinator.load_coordinator_state(run_dir)
            finally:
                self.runtime.iter_verified_receipt = original_public_iter
            self.assertEqual([run_dir], public_scans)

            original_iter = self.runtime._iter_verified_receipt
            scans = []

            def counted_iter(run_path, manifest_snapshot):
                scans.append(Path(run_path).resolve())
                return original_iter(run_path, manifest_snapshot)

            self.runtime._iter_verified_receipt = counted_iter
            try:
                state = self.runtime.mutate_receipt(
                    run_dir,
                    owner_file,
                    lambda _state: [
                        {
                            "event_type": "candidate_proposed",
                            "evidence_refs": [
                                {"kind": "test", "summary": "ordinary event"}
                            ],
                        }
                    ],
                    expected_head=head,
                )
            finally:
                self.runtime._iter_verified_receipt = original_iter
            self.assertEqual([run_dir.resolve()], scans)

            original_write = self.runtime._write_json_atomic
            writes = []

            def counted_write(path, value):
                writes.append(Path(path))
                return original_write(path, value)

            scans.clear()
            self.runtime._iter_verified_receipt = counted_iter
            self.runtime._write_json_atomic = counted_write
            try:
                self.runtime.mutate_receipt(
                    run_dir,
                    owner_file,
                    lambda _state: [
                        {
                            "event_type": "heartbeat_observed",
                            "lane_id": "scale",
                            "agent_id": "agent-1",
                            "from_state": "running",
                            "to_state": "running",
                            "evidence_refs": [
                                {"kind": "test", "summary": "heartbeat"}
                            ],
                            "metadata": {
                                "owner_epoch": 1,
                                "evidence_digest": "c" * 64,
                            },
                        },
                        {
                            "event_type": "lease_renewed",
                            "lane_id": "scale",
                            "agent_id": "agent-1",
                            "from_state": "running",
                            "to_state": "running",
                            "evidence_refs": [
                                {"kind": "test", "summary": "lease"}
                            ],
                            "metadata": {
                                "owner_epoch": 1,
                                "silence_lease_deadline": "2026-07-14T03:00:00Z",
                                "evidence_digest": "c" * 64,
                            },
                        },
                    ],
                    expected_head=state["last_checksum"],
                )
            finally:
                self.runtime._iter_verified_receipt = original_iter
                self.runtime._write_json_atomic = original_write
            self.assertEqual([run_dir.resolve()], scans)
            cache_writes = [
                path.name for path in writes if path.parent.name != "receipt"
            ]
            self.assertEqual(
                ["run.json", "scale.json"],
                [name for name in cache_writes if name != "owner.json"],
            )


if __name__ == "__main__":
    unittest.main()
