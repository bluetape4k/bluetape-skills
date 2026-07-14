import importlib
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
MANIFEST_PATH = SKILL_ROOT / "references" / "workflow-manifest.json"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))


class LivenessTest(unittest.TestCase):
    def setUp(self):
        self.runtime = importlib.import_module("bluetape_runtime")
        self.coordinator = importlib.import_module("bluetape_coordinator")
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state_root = root / ".bluetape"
        self.repo_root = root / "repo"
        self.repo_root.mkdir()
        self.owner_file = self.state_root / "handles" / "liveness.owner"
        initialized = self.runtime.initialize_run(
            self.state_root,
            workflow_type="A",
            repo_root=self.repo_root,
            component_ids=["runtime"],
            owner_file=self.owner_file,
            manifest_path=MANIFEST_PATH,
        )
        self.run_dir = self.state_root / "runs" / initialized["run_id"]
        self.coordinator.approve_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:00Z",
            evidence_refs=[{"kind": "approval", "summary": "approved"}],
        )
        self.coordinator.start_run(
            self.run_dir,
            self.owner_file,
            decided_at="2026-07-14T01:00:01Z",
            evidence_refs=[{"kind": "plan", "summary": "started"}],
        )
        self.coordinator.create_lane(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            assignment="Build and test Phase 2",
            write_scope=[],
            fallback="main session",
            observed_at="2026-07-14T01:00:02Z",
            startup_ack_deadline="2026-07-14T01:00:30Z",
            command_deadline="2026-07-14T01:20:00Z",
            evidence_refs=[{"kind": "plan", "summary": "lane assigned"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="start",
            decided_at="2026-07-14T01:00:03Z",
            evidence_refs=[{"kind": "dispatch", "summary": "agent spawned"}],
        )
        self.coordinator.transition_lane(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            intent="ack",
            decided_at="2026-07-14T01:00:04Z",
            evidence_refs=[{"kind": "ack", "summary": "agent ready"}],
        )

    def tearDown(self):
        self.temp.cleanup()

    @property
    def receipt(self):
        return self.run_dir / "receipt.jsonl"

    def heartbeat(self, **overrides):
        arguments = {
            "run_dir": self.run_dir,
            "lane_id": "build",
            "agent_id": "agent-1",
            "owner_handle": self.owner_file,
            "observed_at": "2026-07-14T01:01:00Z",
            "silence_lease_deadline": "2026-07-14T01:03:00Z",
            "evidence_refs": [
                {
                    "kind": "session",
                    "summary": "test process reached case 12",
                    "checksum": "a" * 64,
                }
            ],
            "reason": "fresh test progress",
        }
        arguments.update(overrides)
        return self.coordinator.record_heartbeat(**arguments)

    def test_fresh_heartbeat_renews_lease_in_one_envelope(self):
        before_lane = self.coordinator.load_coordinator_state(self.run_dir)[1][
            "lanes"
        ]["build"]
        before_count = len(self.runtime.verify_receipt(self.run_dir))

        heartbeat = self.heartbeat()

        events = self.runtime.verify_receipt(self.run_dir)
        self.assertEqual("running", heartbeat["state"])
        self.assertEqual("2026-07-14T01:03:00Z", heartbeat["silence_lease_deadline"])
        self.assertEqual(before_count + 1, len(events))
        self.assertEqual("transaction_committed", events[-1]["event_type"])
        self.assertEqual(2, len(events[-1]["metadata"]["intents"]))
        self.assertEqual(before_lane["evidence_refs"], heartbeat["evidence_refs"])
        self.assertEqual(
            "test process reached case 12",
            heartbeat["liveness_evidence_refs"][0]["summary"],
        )

    def test_fake_or_unbounded_heartbeat_never_changes_receipt(self):
        self.heartbeat()
        for name, overrides, error_type in (
            ("empty", {"evidence_refs": []}, ValueError),
            ("same", {}, ValueError),
            (
                "too-long",
                {"silence_lease_deadline": "2026-07-14T01:11:01Z"},
                ValueError,
            ),
            (
                "after-command",
                {
                    "observed_at": "2026-07-14T01:20:00Z",
                    "silence_lease_deadline": "2026-07-14T01:20:01Z",
                },
                ValueError,
            ),
            ("old-agent", {"agent_id": "agent-old"}, self.coordinator.CoordinatorConflict),
        ):
            with self.subTest(name=name):
                before = self.receipt.read_bytes()
                with self.assertRaises(error_type):
                    self.heartbeat(**overrides)
                self.assertEqual(before, self.receipt.read_bytes())

    def test_heartbeat_evidence_cannot_be_reused_to_complete_lane(self):
        heartbeat = self.heartbeat()
        before = self.receipt.read_bytes()
        with self.assertRaises(ValueError):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id="build",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                intent="complete",
                decided_at="2026-07-14T01:01:01Z",
                evidence_refs=heartbeat["liveness_evidence_refs"],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_liveness_decision_checksum_drives_stall_and_fresh_clear(self):
        self.heartbeat()
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        lane = self.coordinator.load_coordinator_state(self.run_dir)[1]["lanes"][
            "build"
        ]
        before = self.receipt.read_bytes()
        decision = self.coordinator.evaluate_lane_liveness(
            lane, manifest, "2026-07-14T01:03:00Z", command_alive=None
        )
        self.assertEqual("suspect_stall", decision["action"])
        self.assertEqual(before, self.receipt.read_bytes())
        checksum = self.coordinator.liveness_decision_checksum(decision)
        with self.assertRaises(ValueError):
            self.coordinator.record_stall(
                self.run_dir,
                lane_id="build",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                decided_at="2026-07-14T01:03:00Z",
                decision=decision,
                evidence_refs=[
                    {
                        "kind": "decision",
                        "summary": "wrong decision binding",
                        "checksum": "d" * 64,
                    }
                ],
                reason=decision["reason"],
            )
        self.assertEqual(before, self.receipt.read_bytes())

        suspected = self.coordinator.record_stall(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:03:00Z",
            decision=decision,
            evidence_refs=[
                {
                    "kind": "decision",
                    "summary": "read-only liveness result",
                    "checksum": checksum,
                }
            ],
            reason=decision["reason"],
        )
        self.assertEqual("suspected_stall", suspected["state"])
        cleared = self.coordinator.clear_stall(
            self.run_dir,
            lane_id="build",
            agent_id="agent-1",
            owner_handle=self.owner_file,
            decided_at="2026-07-14T01:03:01Z",
            evidence_refs=[
                {
                    "kind": "session",
                    "summary": "case 13 completed",
                    "checksum": "e" * 64,
                }
            ],
            reason="new test progress",
        )
        self.assertEqual("running", cleared["state"])

    def test_stall_rejects_a_bound_continue_decision(self):
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        lane = self.coordinator.load_coordinator_state(self.run_dir)[1]["lanes"][
            "build"
        ]
        decision = self.coordinator.evaluate_lane_liveness(
            lane, manifest, "2026-07-14T01:01:00Z"
        )
        self.assertEqual("continue", decision["action"])
        checksum = self.coordinator.liveness_decision_checksum(decision)
        before = self.receipt.read_bytes()

        with self.assertRaisesRegex(ValueError, "suspect_stall"):
            self.coordinator.record_stall(
                self.run_dir,
                lane_id="build",
                agent_id="agent-1",
                owner_handle=self.owner_file,
                decided_at="2026-07-14T01:01:00Z",
                decision=decision,
                evidence_refs=[
                    {
                        "kind": "decision",
                        "summary": "continue decision",
                        "checksum": checksum,
                    }
                ],
                reason=decision["reason"],
            )

        self.assertEqual(before, self.receipt.read_bytes())

    def test_probe_deadline_uses_manifest_grace_after_command_deadline(self):
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        lane = self.coordinator.load_coordinator_state(self.run_dir)[1]["lanes"][
            "build"
        ]
        decision = self.coordinator.evaluate_lane_liveness(
            lane, manifest, "2026-07-14T01:20:01Z"
        )
        checksum = self.coordinator.liveness_decision_checksum(decision)
        self.coordinator.record_stall(
            self.run_dir,
            "build",
            "agent-1",
            self.owner_file,
            "2026-07-14T01:20:01Z",
            decision,
            [{"kind": "decision", "summary": "stalled", "checksum": checksum}],
            decision["reason"],
        )

        probe = self.coordinator.record_probe_sent(
            self.run_dir,
            "build",
            "agent-1",
            self.owner_file,
            "2026-07-14T01:20:01Z",
            "2026-07-14T01:21:01Z",
            [{"kind": "tool", "summary": "probe sent"}],
        )
        self.assertEqual("2026-07-14T01:21:01Z", probe["probe_deadline"])

    def test_manifest_maximum_lease_is_inclusive(self):
        heartbeat = self.heartbeat(
            silence_lease_deadline="2026-07-14T01:11:00Z"
        )
        self.assertEqual("2026-07-14T01:11:00Z", heartbeat["silence_lease_deadline"])

    def test_liveness_decision_matrix_is_pure_and_boundary_explicit(self):
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        base = {
            "state": "running",
            "startup_ack_deadline": "2026-07-14T01:00:30Z",
            "silence_lease_deadline": "2026-07-14T01:03:00Z",
            "command_deadline": "2026-07-14T01:10:00Z",
            "probe_deadline": None,
            "replacement_count": 0,
        }
        cases = [
            ("terminal", {**base, "state": "completed"}, "2026-07-14T02:00:00Z", None, "none"),
            ("ack-before", {**base, "state": "starting"}, "2026-07-14T01:00:29Z", None, "continue"),
            ("ack-equal", {**base, "state": "starting"}, "2026-07-14T01:00:30Z", None, "suspect_stall"),
            ("lease-before", base, "2026-07-14T01:02:59Z", None, "continue"),
            ("lease-equal-live", base, "2026-07-14T01:03:00Z", True, "observe_command"),
            ("lease-equal-unknown", base, "2026-07-14T01:03:00Z", None, "suspect_stall"),
            ("suspected", {**base, "state": "suspected_stall"}, "2026-07-14T01:03:00Z", None, "send_probe"),
        ]
        before = self.receipt.read_bytes()
        for name, lane, now, command_alive, action in cases:
            with self.subTest(name=name):
                decision = self.coordinator.evaluate_lane_liveness(
                    lane, manifest, now, command_alive=command_alive
                )
                self.assertEqual(action, decision["action"])
        self.assertEqual(before, self.receipt.read_bytes())

    def test_running_lane_without_lease_uses_manifest_silence_threshold(self):
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        lane = self.coordinator.load_coordinator_state(self.run_dir)[1]["lanes"][
            "build"
        ]

        before = self.receipt.read_bytes()
        self.assertEqual(
            "continue",
            self.coordinator.evaluate_lane_liveness(
                lane, manifest, "2026-07-14T01:02:03Z"
            )["action"],
        )
        self.assertEqual(
            "suspect_stall",
            self.coordinator.evaluate_lane_liveness(
                lane, manifest, "2026-07-14T01:02:04Z"
            )["action"],
        )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_recovery_deadline_matrix_requires_both_deadlines(self):
        manifest = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"]
        now = "2026-07-14T01:03:00Z"
        base = {
            "state": "recovering",
            "startup_ack_deadline": "2026-07-14T01:00:30Z",
            "silence_lease_deadline": "2026-07-14T01:01:00Z",
            "replacement_count": 0,
        }
        for name, probe, command, alive, expected in (
            ("both-future", "2026-07-14T01:04:00Z", "2026-07-14T01:05:00Z", None, "await_probe"),
            ("probe-equal", now, "2026-07-14T01:05:00Z", None, "await_probe"),
            ("command-equal", "2026-07-14T01:04:00Z", now, None, "await_probe"),
            ("both-equal", now, now, False, "interrupt"),
            ("both-past-unknown", "2026-07-14T01:02:00Z", "2026-07-14T01:02:00Z", None, "observe_command"),
            ("probe-past-command-live", "2026-07-14T01:02:00Z", "2026-07-14T01:05:00Z", True, "await_probe"),
        ):
            with self.subTest(name=name):
                lane = {**base, "probe_deadline": probe, "command_deadline": command}
                decision = self.coordinator.evaluate_lane_liveness(
                    lane, manifest, now, command_alive=alive
                )
                self.assertEqual(expected, decision["action"])

        limited = {
            **base,
            "probe_deadline": now,
            "command_deadline": now,
            "replacement_count": manifest["liveness"]["max_replacements"],
        }
        self.assertEqual(
            "main_takeover",
            self.coordinator.evaluate_lane_liveness(
                limited, manifest, now, command_alive=None
            )["action"],
        )


if __name__ == "__main__":
    unittest.main()
