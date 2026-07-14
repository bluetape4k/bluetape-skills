import importlib
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class RecoveryLineageTest(unittest.TestCase):
    def setUp(self):
        self.runtime = importlib.import_module("bluetape_runtime")
        self.coordinator = importlib.import_module("bluetape_coordinator")
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state_root = root / ".bluetape"
        self.repo_root = root / "repo"
        self.repo_root.mkdir()
        self.owner_file = self.state_root / "handles" / "recovery.owner"
        initialized = self.runtime.initialize_run(
            self.state_root,
            workflow_type="A",
            repo_root=self.repo_root,
            component_ids=["runtime"],
            owner_file=self.owner_file,
            manifest_path=MANIFEST_PATH,
        )
        self.initialized = initialized
        self.run_dir = self.state_root / "runs" / initialized["run_id"]
        self.coordinator.approve_run(
            self.run_dir,
            self.owner_file,
            "2026-07-14T01:00:00Z",
            [{"kind": "approval", "summary": "approved"}],
        )
        self.coordinator.start_run(
            self.run_dir,
            self.owner_file,
            "2026-07-14T01:00:01Z",
            [{"kind": "plan", "summary": "started"}],
        )
        self.coordinator.create_lane(
            self.run_dir,
            "worker",
            "agent-1",
            self.owner_file,
            "Build and test Phase 2",
            [],
            "main session",
            "2026-07-14T01:00:02Z",
            "2026-07-14T01:00:30Z",
            "2026-07-14T01:10:00Z",
            [{"kind": "plan", "summary": "worker assigned"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            "worker",
            "agent-1",
            self.owner_file,
            "start",
            "2026-07-14T01:00:03Z",
            [{"kind": "dispatch", "summary": "spawned"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            "worker",
            "agent-1",
            self.owner_file,
            "ack",
            "2026-07-14T01:00:04Z",
            [{"kind": "ack", "summary": "ready"}],
        )

    def tearDown(self):
        self.temp.cleanup()

    @property
    def receipt(self):
        return self.run_dir / "receipt.jsonl"

    def test_resume_diagnosis_observes_sibling_lock_initializer(self):
        initializer = self.run_dir / "locks" / ".receipt.initializing.json"
        initializer.write_text(
            json.dumps({"pid": os.getpid(), "token": "initializing"}),
            encoding="utf-8",
        )
        os.chmod(initializer, 0o600)

        diagnosis = self.coordinator.inspect_resume(self.run_dir)

        self.assertEqual("locked_initializing", diagnosis["lock_owner_status"])

    def prepare_suspected(self):
        manifest, state = self.coordinator.load_coordinator_state(self.run_dir)
        decision = self.coordinator.evaluate_lane_liveness(
            state["lanes"]["worker"],
            manifest["manifest"],
            "2026-07-14T01:02:05Z",
        )
        checksum = self.coordinator.liveness_decision_checksum(decision)
        return self.coordinator.record_stall(
            self.run_dir,
            "worker",
            "agent-1",
            self.owner_file,
            "2026-07-14T01:02:05Z",
            decision,
            [
                {
                    "kind": "decision",
                    "summary": "liveness decision",
                    "checksum": checksum,
                }
            ],
            decision["reason"],
        )

    def prepare_interrupted(self):
        self.prepare_suspected()
        self.coordinator.record_probe_sent(
            self.run_dir,
            lane_id="worker",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:02:05Z",
            probe_deadline="2026-07-14T01:03:05Z",
            evidence_refs=[{"kind": "tool", "summary": "message sent to agent-1"}],
        )
        return self.coordinator.record_interrupt_result(
            self.run_dir,
            lane_id="worker",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:10:00Z",
            evidence_refs=[{"kind": "tool", "summary": "agent-1 interrupted"}],
        )

    def reassign(self, **overrides):
        arguments = {
            "run_dir": self.run_dir,
            "lane_id": "worker",
            "replacement_lane_id": "worker-r1",
            "replacement_agent_id": "agent-2",
            "owner_handle": self.owner_file,
            "decided_at": "2026-07-14T01:10:01Z",
            "replacement_assignment": "Resume from checkpoint 12 and verify cases 13-20",
            "replacement_write_scope": [],
            "replacement_startup_ack_deadline": "2026-07-14T01:10:31Z",
            "replacement_command_deadline": "2026-07-14T01:20:00Z",
            "evidence_refs": [
                {"kind": "recovery", "summary": "checkpoint 12 recovered"}
            ],
        }
        arguments.update(overrides)
        return self.coordinator.reassign_lane(**arguments)

    def test_probe_interrupt_and_reassignment_are_lineage_atomic(self):
        interrupted = self.prepare_interrupted()
        self.assertEqual("recovering", interrupted["state"])
        before_count = len(self.runtime.verify_receipt(self.run_dir))

        replacement = self.reassign()

        events = self.runtime.verify_receipt(self.run_dir)
        self.assertEqual(before_count + 1, len(events))
        self.assertEqual("transaction_committed", events[-1]["event_type"])
        self.assertEqual("replaced", replacement["original"]["state"])
        self.assertEqual("pending", replacement["replacement"]["state"])
        self.assertEqual(
            "worker", replacement["replacement"]["parent_lane_id"]
        )
        self.assertEqual([], replacement["incomplete_replacements"])

        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.transition_lane(
                self.run_dir,
                "worker",
                "agent-1",
                self.owner_file,
                "complete",
                "2026-07-14T01:10:02Z",
                [{"kind": "result", "summary": "late result"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_reassignment_requires_interrupt_and_checkpoint_proof(self):
        self.prepare_suspected()
        self.coordinator.record_probe_sent(
            self.run_dir,
            "worker",
            "agent-1",
            self.owner_file,
            "2026-07-14T01:02:00Z",
            "2026-07-14T01:03:00Z",
            [{"kind": "tool", "summary": "probe sent"}],
        )
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.reassign()
        self.assertEqual(before, self.receipt.read_bytes())

        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.record_interrupt_result(
                self.run_dir,
                "worker",
                "agent-1",
                self.owner_file,
                "2026-07-14T01:09:59Z",
                [{"kind": "tool", "summary": "agent interrupt too early"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_invalid_replacement_arguments_leave_receipt_unchanged(self):
        self.prepare_interrupted()
        invalid = (
            {"replacement_lane_id": "worker"},
            {"replacement_agent_id": "agent-1"},
            {"replacement_assignment": "Build and test Phase 2"},
            {"replacement_write_scope": ["expanded"]},
            {"replacement_startup_ack_deadline": "2026-07-14T01:10:01Z"},
            {"evidence_refs": []},
            {"evidence_refs": [{"kind": "test", "summary": "no checkpoint"}]},
        )
        for overrides in invalid:
            with self.subTest(overrides=overrides):
                before = self.receipt.read_bytes()
                with self.assertRaises((ValueError, self.coordinator.CoordinatorConflict)):
                    self.reassign(**overrides)
                self.assertEqual(before, self.receipt.read_bytes())

    def test_terminal_replacement_closes_original_lineage(self):
        self.prepare_interrupted()
        self.reassign()
        self.coordinator.transition_lane(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "start",
            "2026-07-14T01:10:02Z",
            [{"kind": "dispatch", "summary": "replacement spawned"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "ack",
            "2026-07-14T01:10:03Z",
            [{"kind": "ack", "summary": "replacement ready"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "complete",
            "2026-07-14T01:11:00Z",
            [{"kind": "result", "summary": "cases 13-20 verified"}],
            metadata={"changed_paths": []},
        )

        closed = self.coordinator.close_replacement_lineage(
            self.run_dir,
            lane_id="worker",
            replacement_lane_id="worker-r1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:11:01Z",
            evidence_refs=[{"kind": "recovery", "summary": "replacement completed"}],
        )
        self.assertEqual("completed", closed["state"])

    def test_cancelled_replacement_closes_original_lineage(self):
        self.prepare_interrupted()
        self.reassign()
        self.coordinator.transition_lane(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "cancel",
            "2026-07-14T01:10:02Z",
            [{"kind": "recovery", "summary": "replacement cancelled"}],
        )

        closed = self.coordinator.close_replacement_lineage(
            self.run_dir,
            lane_id="worker",
            replacement_lane_id="worker-r1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:10:03Z",
            evidence_refs=[
                {"kind": "recovery", "summary": "cancelled lineage closed"}
            ],
        )

        self.assertEqual("cancelled", closed["state"])

    def test_second_replacement_is_rejected_at_manifest_limit(self):
        self.prepare_interrupted()
        self.reassign()
        for intent, at, evidence in (
            ("start", "2026-07-14T01:10:02Z", "replacement spawned"),
            ("ack", "2026-07-14T01:10:03Z", "replacement ready"),
        ):
            self.coordinator.transition_lane(
                self.run_dir,
                "worker-r1",
                "agent-2",
                self.owner_file,
                intent,
                at,
                [{"kind": "test", "summary": evidence}],
            )
        manifest, state = self.coordinator.load_coordinator_state(self.run_dir)
        decision = self.coordinator.evaluate_lane_liveness(
            state["lanes"]["worker-r1"],
            manifest["manifest"],
            "2026-07-14T01:12:04Z",
        )
        checksum = self.coordinator.liveness_decision_checksum(decision)
        self.coordinator.record_stall(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "2026-07-14T01:12:04Z",
            decision,
            [{"kind": "decision", "summary": "stalled", "checksum": checksum}],
            decision["reason"],
        )
        self.coordinator.record_probe_sent(
            self.run_dir,
            "worker-r1",
            "agent-2",
            self.owner_file,
            "2026-07-14T01:12:04Z",
            "2026-07-14T01:13:04Z",
            [{"kind": "tool", "summary": "probe sent"}],
        )
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.record_interrupt_result(
                self.run_dir,
                "worker-r1",
                "agent-2",
                self.owner_file,
                "2026-07-14T01:30:00Z",
                [{"kind": "tool", "summary": "agent-2 interrupted"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_legacy_incomplete_reservation_requires_explicit_block(self):
        self.prepare_interrupted()
        self.runtime.append_receipt_event(
            self.run_dir,
            "lane_reassigned",
            owner_handle=self.owner_file,
            manifest_hash=self.initialized["manifest_hash"],
            lane_id="worker",
            agent_id="agent-1",
            from_state="recovering",
            to_state="replaced",
            timestamp="2026-07-14T01:10:01Z",
            evidence_refs=[
                {"kind": "recovery", "summary": "checkpoint reservation"}
            ],
            metadata={
                "owner_epoch": 1,
                "replacement_count": 1,
                "previous_agent_id": "agent-1",
                "replacement_lane_id": "worker-r1",
            },
        )
        state = self.coordinator.load_coordinator_state(self.run_dir)[1]
        self.assertEqual(["worker"], state["incomplete_replacements"])

        blocked = self.coordinator.block_incomplete_replacement(
            self.run_dir,
            lane_id="worker",
            replacement_lane_id="worker-r1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:10:02Z",
            evidence_refs=[
                {"kind": "operator", "summary": "exact child proof unavailable"}
            ],
        )
        self.assertEqual("blocked", blocked["state"])

    def test_exact_incomplete_reservation_can_be_repaired_once(self):
        self.prepare_interrupted()
        checkpoint = [
            {"kind": "recovery", "summary": "checkpoint 12 reserved"}
        ]
        checkpoint_digest = self.runtime.evidence_digest(checkpoint)
        self.runtime.append_receipt_event(
            self.run_dir,
            "lane_reassigned",
            owner_handle=self.owner_file,
            manifest_hash=self.initialized["manifest_hash"],
            lane_id="worker",
            agent_id="agent-1",
            from_state="recovering",
            to_state="replaced",
            timestamp="2026-07-14T01:10:01Z",
            evidence_refs=checkpoint,
            metadata={
                "owner_epoch": 1,
                "replacement_count": 1,
                "previous_agent_id": "agent-1",
                "replacement_lane_id": "worker-r1",
                "replacement_agent_id": "agent-2",
                "replacement_assignment": "Resume from checkpoint 12",
                "replacement_write_scope": [],
                "replacement_fallback": "main session",
                "replacement_startup_ack_deadline": "2026-07-14T01:10:31Z",
                "replacement_command_deadline": "2026-07-14T01:20:00Z",
                "checkpoint_digest": checkpoint_digest,
            },
        )
        before = self.receipt.read_bytes()
        with self.assertRaises(ValueError):
            self.coordinator.repair_replacement(
                self.run_dir,
                "worker",
                "worker-r1",
                self.owner_file,
                "2026-07-14T01:10:02Z",
                [
                    {
                        "kind": "recovery",
                        "summary": "wrong checkpoint",
                        "checksum": "f" * 64,
                    }
                ],
            )
        self.assertEqual(before, self.receipt.read_bytes())

        repaired = self.coordinator.repair_replacement(
            self.run_dir,
            "worker",
            "worker-r1",
            self.owner_file,
            "2026-07-14T01:10:02Z",
            [
                {
                    "kind": "recovery",
                    "summary": "checkpoint verified",
                    "checksum": checkpoint_digest,
                }
            ],
        )
        self.assertEqual("pending", repaired["state"])
        self.assertEqual("agent-2", repaired["agent_id"])
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.repair_replacement(
                self.run_dir,
                "worker",
                "worker-r1",
                self.owner_file,
                "2026-07-14T01:10:03Z",
                [
                    {
                        "kind": "recovery",
                        "summary": "checkpoint verified",
                        "checksum": checkpoint_digest,
                    }
                ],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_resume_inspection_and_owner_transfer_fence_old_handle(self):
        inspection = self.coordinator.inspect_resume(self.run_dir)
        self.assertEqual(1, inspection["owner_epoch"])
        self.assertRegex(inspection["owner_fingerprint"], "^[0-9a-f]{64}$")
        self.assertEqual(["worker"], inspection["lanes_requiring_observation"])
        self.assertEqual([], inspection["incomplete_replacements"])
        before_receipt = self.receipt.read_bytes()
        old_payload = self.owner_file.read_bytes()
        new_owner = self.state_root / "handles" / "resumed.owner"

        resumed = self.coordinator.transfer_run_owner(
            self.run_dir,
            current_owner_handle=self.owner_file,
            new_owner_handle=new_owner,
            evidence_refs=[
                {"kind": "resume", "summary": "receipt and lanes verified"}
            ],
        )

        self.assertEqual(2, resumed["owner_epoch"])
        self.assertFalse(self.owner_file.exists())
        self.assertTrue(new_owner.is_file())
        self.assertNotEqual(before_receipt, self.receipt.read_bytes())
        stale = self.state_root / "handles" / "stale.owner"
        stale.write_bytes(old_payload)
        os.chmod(stale, 0o600)
        before = self.receipt.read_bytes()
        with self.assertRaises(self.runtime.StateLockBusy):
            self.coordinator.start_recovery(
                self.run_dir,
                stale,
                "2026-07-14T02:00:00Z",
                [{"kind": "resume", "summary": "stale writer"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())
        recovered = self.coordinator.start_recovery(
            self.run_dir,
            new_owner,
            "2026-07-14T02:00:00Z",
            [{"kind": "resume", "summary": "new owner verified"}],
        )
        self.assertEqual("recovering", recovered["run_state"])

    def test_terminal_run_rejects_owner_transfer_without_orphan(self):
        self.coordinator.terminate_run(
            self.run_dir,
            self.owner_file,
            "block",
            "2026-07-14T02:00:00Z",
            [{"kind": "operator", "summary": "blocked"}],
        )
        new_owner = self.state_root / "handles" / "terminal.owner"
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                [{"kind": "resume", "summary": "must fail"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())
        self.assertFalse(new_owner.exists())

    def test_wrong_mode_or_missing_current_owner_rejects_transfer(self):
        new_owner = self.state_root / "handles" / "must-not-exist.owner"
        os.chmod(self.owner_file, 0o644)
        with self.assertRaises(ValueError):
            self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                [{"kind": "resume", "summary": "wrong mode"}],
            )
        self.assertFalse(new_owner.exists())
        os.chmod(self.owner_file, 0o600)
        self.owner_file.unlink()
        with self.assertRaises(FileNotFoundError):
            self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                [{"kind": "resume", "summary": "missing owner"}],
            )
        self.assertFalse(new_owner.exists())

    def test_corrupt_receipt_rejects_owner_transfer_without_orphan(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        new_owner = self.state_root / "handles" / "corrupt.owner"
        before = self.receipt.read_bytes()
        with self.assertRaises(self.runtime.ReceiptCorrupt):
            self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                [{"kind": "resume", "summary": "corrupt chain"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())
        self.assertFalse(new_owner.exists())

    def test_owner_transfer_survives_post_commit_cache_failure(self):
        new_owner = self.state_root / "handles" / "cache-failure.owner"
        evidence = [{"kind": "resume", "summary": "cache can rebuild"}]
        original_write = self.runtime._write_json_atomic

        def fail_run_cache(path, value):
            if Path(path) == self.run_dir / "run.json":
                raise OSError("cache write failed")
            return original_write(path, value)

        with mock.patch.object(
            self.runtime,
            "_write_json_atomic",
            side_effect=fail_run_cache,
        ):
            resumed = self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                evidence,
            )

        self.assertEqual(2, resumed["owner_epoch"])
        self.assertTrue(new_owner.is_file())
        self.assertFalse(self.owner_file.exists())
        self.assertEqual("run_resumed", self.runtime.verify_receipt(self.run_dir)[-1]["event_type"])

    def test_incomplete_replacement_rejects_owner_transfer_without_orphan(self):
        self.prepare_interrupted()
        self.runtime.append_receipt_event(
            self.run_dir,
            "lane_reassigned",
            owner_handle=self.owner_file,
            manifest_hash=self.initialized["manifest_hash"],
            lane_id="worker",
            agent_id="agent-1",
            from_state="recovering",
            to_state="replaced",
            timestamp="2026-07-14T01:10:01Z",
            evidence_refs=[{"kind": "recovery", "summary": "reserved"}],
            metadata={
                "owner_epoch": 1,
                "replacement_count": 1,
                "previous_agent_id": "agent-1",
                "replacement_lane_id": "worker-r1",
            },
        )
        new_owner = self.state_root / "handles" / "incomplete.owner"
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.transfer_run_owner(
                self.run_dir,
                self.owner_file,
                new_owner,
                [{"kind": "resume", "summary": "incomplete replacement"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())
        self.assertFalse(new_owner.exists())

    def test_corrupt_receipt_diagnosis_is_read_only_and_recovery_is_new_run(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        damaged_receipt = self.receipt.read_bytes()
        cache_path = self.run_dir / "run.json"
        damaged_cache = cache_path.read_bytes()

        diagnosis = self.coordinator.inspect_resume(self.run_dir)

        self.assertEqual("blocked", diagnosis["effective_state"])
        self.assertEqual(7, diagnosis["first_bad_sequence"])
        self.assertEqual(6, diagnosis["last_trusted_sequence"])
        self.assertEqual(damaged_receipt, self.receipt.read_bytes())
        self.assertEqual(damaged_cache, cache_path.read_bytes())
        diagnose_checksum = self.coordinator.diagnosis_checksum(diagnosis)
        recovery_owner = self.state_root / "handles" / "recovery-run.owner"

        recovered = self.coordinator.create_recovery_run(
            self.run_dir,
            diagnosis=diagnosis,
            diagnosis_checksum=diagnose_checksum,
            new_owner_handle=recovery_owner,
            approval_evidence=[
                {"kind": "approval", "summary": "create separate recovery run"}
            ],
        )

        self.assertNotEqual(self.run_dir.name, recovered["new_run_id"])
        new_run = self.state_root / "runs" / recovered["new_run_id"]
        first_event = self.runtime.verify_receipt(new_run)[0]
        self.assertEqual("run_created", first_event["event_type"])
        self.assertEqual(
            self.run_dir.name,
            first_event["metadata"]["recovery_original_run_id"],
        )
        self.assertEqual(diagnose_checksum, first_event["metadata"]["recovery_diagnose_checksum"])
        self.assertEqual(
            [{"kind": "approval", "summary": "create separate recovery run"}],
            first_event["evidence_refs"],
        )
        self.assertEqual(damaged_receipt, self.receipt.read_bytes())
        quarantine = self.state_root / recovered["quarantine_path"]
        self.assertEqual(damaged_receipt, quarantine.read_bytes())
        self.assertEqual(0o600, stat.S_IMODE(quarantine.stat().st_mode))
        self.assertEqual("planned", self.coordinator.inspect_resume(new_run)["run_state"])

    def test_recovery_retry_reuses_matching_quarantine_after_crash(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        diagnosis = self.coordinator.inspect_resume(self.run_dir)
        checksum = self.coordinator.diagnosis_checksum(diagnosis)
        recovery_owner = self.state_root / "handles" / "retry.owner"
        evidence = [{"kind": "approval", "summary": "retry recovery"}]

        with mock.patch.object(
            self.runtime,
            "initialize_run",
            side_effect=RuntimeError("crash after quarantine"),
        ):
            with self.assertRaisesRegex(RuntimeError, "crash after quarantine"):
                self.coordinator.create_recovery_run(
                    self.run_dir,
                    diagnosis,
                    checksum,
                    recovery_owner,
                    evidence,
                )

        recovered = self.coordinator.create_recovery_run(
            self.run_dir,
            diagnosis,
            checksum,
            recovery_owner,
            evidence,
        )
        quarantine = self.state_root / recovered["quarantine_path"]
        self.assertTrue(quarantine.is_file())
        self.assertEqual(diagnosis["receipt_hash"], self.runtime.file_sha256(quarantine))

    def test_recovery_retry_reuses_run_after_initialize_response_is_lost(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        diagnosis = self.coordinator.inspect_resume(self.run_dir)
        checksum = self.coordinator.diagnosis_checksum(diagnosis)
        recovery_owner = self.state_root / "handles" / "lost-response.owner"
        evidence = [{"kind": "approval", "summary": "retry lost response"}]
        initialize_run = self.runtime.initialize_run

        def initialize_then_lose_response(*args, **kwargs):
            initialize_run(*args, **kwargs)
            raise RuntimeError("response lost after recovery initialization")

        with mock.patch.object(
            self.runtime,
            "initialize_run",
            side_effect=initialize_then_lose_response,
        ):
            with self.assertRaisesRegex(RuntimeError, "response lost"):
                self.coordinator.create_recovery_run(
                    self.run_dir,
                    diagnosis,
                    checksum,
                    recovery_owner,
                    evidence,
                )

        owner_payload = json.loads(
            recovery_owner.read_text(encoding="utf-8")
        )
        runs_after_lost_response = set((self.state_root / "runs").iterdir())
        with mock.patch.object(
            self.runtime,
            "verify_receipt",
            side_effect=AssertionError("recovery retry must stream"),
        ):
            recovered = self.coordinator.create_recovery_run(
                self.run_dir,
                diagnosis,
                checksum,
                recovery_owner,
                evidence,
            )

        self.assertEqual(owner_payload["run_id"], recovered["new_run_id"])
        self.assertEqual(
            runs_after_lost_response, set((self.state_root / "runs").iterdir())
        )

    def test_recovery_retry_after_manifest_write_failure_cleans_partial_init(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        diagnosis = self.coordinator.inspect_resume(self.run_dir)
        checksum = self.coordinator.diagnosis_checksum(diagnosis)
        recovery_owner = self.state_root / "handles" / "manifest-retry.owner"
        evidence = [{"kind": "approval", "summary": "retry manifest failure"}]
        original_write = self.runtime._write_json_atomic
        injected = {"done": False}

        def fail_recovery_manifest(path, value):
            target = Path(path)
            if (
                not injected["done"]
                and target.name == "manifest.json"
                and target.parent != self.run_dir
            ):
                injected["done"] = True
                raise OSError("manifest fsync failed")
            return original_write(path, value)

        with mock.patch.object(
            self.runtime, "_write_json_atomic", side_effect=fail_recovery_manifest
        ):
            with self.assertRaisesRegex(OSError, "manifest fsync failed"):
                self.coordinator.create_recovery_run(
                    self.run_dir,
                    diagnosis,
                    checksum,
                    recovery_owner,
                    evidence,
                )

        self.assertFalse(recovery_owner.exists())
        self.assertEqual({self.run_dir}, set((self.state_root / "runs").iterdir()))
        self.assertEqual(
            {self.owner_file}, set((self.state_root / "handles").iterdir())
        )

        recovered = self.coordinator.create_recovery_run(
            self.run_dir,
            diagnosis,
            checksum,
            recovery_owner,
            evidence,
        )
        self.assertTrue(
            (self.state_root / "runs" / recovered["new_run_id"]).is_dir()
        )

    def test_recovery_run_rejects_mismatched_diagnosis_without_artifacts(self):
        with self.receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        diagnosis = self.coordinator.inspect_resume(self.run_dir)
        recovery_owner = self.state_root / "handles" / "rejected.owner"
        before_quarantine = set((self.state_root / "quarantine").iterdir())

        with self.assertRaises(ValueError):
            self.coordinator.create_recovery_run(
                self.run_dir,
                diagnosis=diagnosis,
                diagnosis_checksum="f" * 64,
                new_owner_handle=recovery_owner,
                approval_evidence=[{"kind": "approval", "summary": "recovery"}],
            )

        self.assertFalse(recovery_owner.exists())
        self.assertEqual(before_quarantine, set((self.state_root / "quarantine").iterdir()))


if __name__ == "__main__":
    unittest.main()
