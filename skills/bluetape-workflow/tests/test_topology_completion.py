import copy
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


class TopologyCompletionTest(unittest.TestCase):
    def setUp(self):
        self.runtime = importlib.import_module("bluetape_runtime")
        self.coordinator = importlib.import_module("bluetape_coordinator")
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state_root = root / ".bluetape"
        self.repo_root = root / "repo"
        self.repo_root.mkdir()
        self.owner = self.state_root / "handles" / "topology.owner"
        initialized = self.runtime.initialize_run(
            self.state_root,
            workflow_type="A",
            repo_root=self.repo_root,
            component_ids=["runtime", "guidance"],
            owner_file=self.owner,
            manifest_path=MANIFEST_PATH,
        )
        self.run_dir = self.state_root / "runs" / initialized["run_id"]
        self.coordinator.approve_run(
            self.run_dir,
            self.owner,
            "2026-07-14T03:00:00Z",
            [{"kind": "approval", "summary": "approved"}],
        )
        self.coordinator.start_run(
            self.run_dir,
            self.owner,
            "2026-07-14T03:00:01Z",
            [{"kind": "plan", "summary": "started"}],
        )
        for lane_id in ("build", "docs"):
            self.coordinator.create_lane(
                self.run_dir,
                lane_id,
                lane_id + "-agent",
                self.owner,
                "Complete " + lane_id,
                [],
                "main session",
                "2026-07-14T03:00:02Z",
                "2026-07-14T03:01:00Z",
                "2026-07-14T03:10:00Z",
                [{"kind": "plan", "summary": lane_id + " assigned"}],
            )
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id,
                lane_id + "-agent",
                self.owner,
                "start",
                "2026-07-14T03:00:03Z",
                [{"kind": "dispatch", "summary": lane_id + " spawned"}],
            )
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id,
                lane_id + "-agent",
                self.owner,
                "ack",
                "2026-07-14T03:00:04Z",
                [{"kind": "ack", "summary": lane_id + " ready"}],
            )

    def tearDown(self):
        self.temp.cleanup()

    @property
    def receipt(self):
        return self.run_dir / "receipt.jsonl"

    def components(self):
        return [
            {
                "id": "runtime",
                "required": True,
                "description": "Coordinator runtime behavior",
                "owner_lane": "build",
                "required_checks": ["unit"],
                "dependencies": [],
                "evidence_refs": [],
                "coverage_state": "missing",
            },
            {
                "id": "guidance",
                "required": True,
                "description": "Main-session operating contract",
                "owner_lane": "docs",
                "required_checks": ["contract"],
                "dependencies": ["runtime"],
                "evidence_refs": [],
                "coverage_state": "missing",
            },
        ]

    def register(self):
        return self.coordinator.register_topology(
            self.run_dir,
            owner_handle=self.owner,
            components=self.components(),
            evidence_refs=[{"kind": "plan", "summary": "approved component map"}],
        )

    def test_registers_complete_dag_and_rejects_weak_snapshots_without_mutation(self):
        registered = self.register()
        self.assertEqual(["guidance", "runtime"], sorted(registered))

        invalid_snapshots = []
        invalid_snapshots.append(self.components()[:1])
        duplicate = self.components()
        duplicate[1]["id"] = "runtime"
        invalid_snapshots.append(duplicate)
        cycle = self.components()
        cycle[0]["dependencies"] = ["guidance"]
        invalid_snapshots.append(cycle)
        unknown_owner = self.components()
        unknown_owner[0]["owner_lane"] = "missing"
        invalid_snapshots.append(unknown_owner)
        injected = self.components()
        injected[0]["coverage_state"] = "covered"
        injected[0]["evidence_refs"] = [{"kind": "caller", "summary": "fake"}]
        invalid_snapshots.append(injected)

        for components in invalid_snapshots:
            with self.subTest(components=components):
                before = self.receipt.read_bytes()
                with self.assertRaises(ValueError):
                    self.coordinator.register_topology(
                        self.run_dir,
                        self.owner,
                        components,
                        [{"kind": "plan", "summary": "invalid"}],
                    )
                self.assertEqual(before, self.receipt.read_bytes())

    def test_maximum_deep_dag_is_valid_but_limit_plus_one_is_rejected(self):
        limits = self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"][
            "resource_limits"
        ]
        maximum = limits["max_components"]
        components = []
        for index in range(maximum):
            component_id = "c" + str(index)
            components.append(
                {
                    "id": component_id,
                    "required": True,
                    "description": component_id,
                    "owner_lane": "lane" + str(index),
                    "required_checks": [],
                    "dependencies": [] if index == 0 else ["c" + str(index - 1)],
                    "evidence_refs": [],
                    "coverage_state": "missing",
                }
            )
        validated = self.coordinator.validate_topology(
            components,
            {"lane" + str(index) for index in range(maximum)},
            {"c" + str(index) for index in range(maximum)},
            limits,
        )
        self.assertEqual(maximum, len(validated))
        with self.assertRaises(ValueError):
            self.coordinator.validate_topology(
                components + [copy.deepcopy(components[-1])],
                {"lane" + str(index) for index in range(maximum)},
                {"c" + str(index) for index in range(maximum)},
                limits,
            )

    def test_check_history_is_last_write_wins_and_requires_fresh_recovery(self):
        self.register()
        first = [{"kind": "test", "summary": "unit passed", "checksum": "a" * 64}]
        self.assertTrue(
            self.coordinator.record_check_result(
                self.run_dir, self.owner, "runtime", "unit", True, first
            )
        )
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.record_check_result(
                self.run_dir, self.owner, "runtime", "unit", True, first
            )
        self.assertEqual(before, self.receipt.read_bytes())
        self.assertFalse(
            self.coordinator.record_check_result(
                self.run_dir,
                self.owner,
                "runtime",
                "unit",
                False,
                [{"kind": "test", "summary": "regression", "checksum": "b" * 64}],
                reason="regression detected",
            )
        )
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.record_check_result(
                self.run_dir,
                self.owner,
                "runtime",
                "unit",
                True,
                [{"kind": "test", "summary": "rerun", "checksum": "c" * 64}],
            )
        self.assertTrue(
            self.coordinator.record_check_result(
                self.run_dir,
                self.owner,
                "runtime",
                "unit",
                True,
                [{"kind": "test", "summary": "fixed", "checksum": "c" * 64}],
                reason="fresh rerun passed",
            )
        )
        state = self.coordinator.load_coordinator_state(self.run_dir)[1]
        self.assertEqual(3, len(state["check_history"]["runtime"]["unit"]))
        self.register()
        replayed = self.coordinator.load_coordinator_state(self.run_dir)[1]
        self.assertTrue(replayed["checks"]["runtime"]["unit"])

    def test_completion_is_atomic_and_blocked_until_every_required_result(self):
        self.register()
        self.coordinator.record_check_result(
            self.run_dir,
            self.owner,
            "runtime",
            "unit",
            True,
            [{"kind": "test", "summary": "unit passed"}],
        )
        self.coordinator.record_check_result(
            self.run_dir,
            self.owner,
            "guidance",
            "contract",
            True,
            [{"kind": "test", "summary": "contract passed"}],
        )
        for lane_id in ("build", "docs"):
            self.coordinator.transition_lane(
                self.run_dir,
                lane_id,
                lane_id + "-agent",
                self.owner,
                "complete",
                "2026-07-14T03:05:00Z",
                [{"kind": "result", "summary": lane_id + " complete"}],
                metadata={"changed_paths": []},
            )
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CompletionBlocked) as blocked:
            self.coordinator.complete_run(
                self.run_dir,
                self.owner,
                [{"kind": "main", "summary": "reviewed"}],
            )
        self.assertEqual(["guidance", "runtime"], blocked.exception.details["missing_components"])
        self.assertEqual(before, self.receipt.read_bytes())

        for component_id in ("runtime", "guidance"):
            covered = self.coordinator.attach_component_evidence(
                self.run_dir,
                self.owner,
                component_id,
                [{"kind": "result", "summary": component_id + " covered"}],
            )
            self.assertEqual("covered", covered["coverage_state"])
        preserved = self.register()
        self.assertEqual("covered", preserved["runtime"]["coverage_state"])
        self.assertTrue(preserved["runtime"]["evidence_refs"])
        completed = self.coordinator.complete_run(
            self.run_dir,
            self.owner,
            [{"kind": "main", "summary": "all evidence reviewed"}],
        )
        self.assertEqual("completed", completed["run_state"])
        self.assertTrue(completed["main_verified"])
        self.assertEqual("transaction_committed", completed["last_event_type"])

    def test_component_evidence_requires_owner_success_and_required_checks(self):
        self.register()
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.attach_component_evidence(
                self.run_dir,
                self.owner,
                "runtime",
                [{"kind": "result", "summary": "too early"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())

    def test_explicit_removal_requires_reason_and_still_blocks_completion(self):
        self.register()
        before = self.receipt.read_bytes()
        with self.assertRaises(self.coordinator.CoordinatorConflict):
            self.coordinator.remove_topology_component(
                self.run_dir,
                self.owner,
                "runtime",
                [{"kind": "approval", "summary": "remove runtime"}],
                reason="dependency still exists",
            )
        self.assertEqual(before, self.receipt.read_bytes())
        with self.assertRaises(ValueError):
            self.coordinator.remove_topology_component(
                self.run_dir,
                self.owner,
                "guidance",
                [{"kind": "approval", "summary": "remove guidance"}],
            )
        self.assertEqual(before, self.receipt.read_bytes())
        remaining = self.coordinator.remove_topology_component(
            self.run_dir,
            self.owner,
            "guidance",
            [{"kind": "approval", "summary": "remove guidance"}],
            reason="approved scope reduction",
        )
        self.assertNotIn("guidance", remaining)
        state = self.coordinator.load_coordinator_state(self.run_dir)[1]
        evaluation = self.coordinator.evaluate_run_completion(
            state,
            self.runtime.load_run_manifest_snapshot(self.run_dir)["manifest"],
        )
        self.assertIn("guidance", evaluation["missing_components"])


if __name__ == "__main__":
    unittest.main()
