import importlib.util
import json
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "bluetape_runtime.py"
COORDINATOR_PATH = SKILL_ROOT / "scripts" / "bluetape_coordinator.py"
CODEX_SOURCE = SKILL_ROOT.parents[1]
COMMON_GATES_PATH = SKILL_ROOT / "references" / "common-gates.md"


def load_runtime():
    spec = importlib.util.spec_from_file_location("bluetape_runtime", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_coordinator():
    spec = importlib.util.spec_from_file_location(
        "bluetape_coordinator_manifest", COORDINATOR_PATH
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class ManifestContractTest(unittest.TestCase):
    def setUp(self):
        self.runtime = load_runtime()
        self.manifest_path = SKILL_ROOT / "references" / "workflow-manifest.json"
        self.schema_path = SKILL_ROOT / "references" / "receipt-schema.json"

    def test_canonical_manifest_is_valid(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.runtime.validate_manifest(manifest)
        self.assertEqual(
            ["A", "B", "C", "D", "E", "P", "F"], manifest["workflow_types"]
        )
        self.assertEqual(
            ["bluetape-full-feature"], manifest["workflow_routes"]["A"]
        )
        self.assertEqual(
            [
                "WF-01",
                "WF-02",
                "WF-03",
                "WF-04",
                "WF-04A",
                "WF-05",
                "WF-06",
            ],
            manifest["router_checklist_ids"],
        )
        self.assertEqual(30, manifest["liveness"]["monitor_interval_seconds"])
        self.assertEqual(60, manifest["liveness"]["max_native_wait_seconds"])
        self.assertEqual(
            300, manifest["liveness"]["consecutive_wait_timeout_seconds"]
        )
        self.assertEqual(
            900, manifest["liveness"]["absolute_delegation_deadline_seconds"]
        )
        self.assertEqual(600, manifest["liveness"]["max_silence_lease_seconds"])
        self.assertEqual(1, manifest["liveness"]["max_replacements"])
        self.assertIn("required", manifest["topology"]["component_required_fields"])
        self.assertFalse(manifest["token_audit"]["hard_limit"])

    def test_pre_resolution_phase2_snapshot_remains_valid(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest.pop("failure_resolution")
        self.runtime.validate_manifest(manifest)
        self.assertIn("candidate_validated", manifest["receipt"]["event_types"])

    def test_transition_to_unknown_state_is_rejected(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["run_transitions"]["running"].append("unknown")
        with self.assertRaisesRegex(ValueError, "unknown run transition"):
            self.runtime.validate_manifest(manifest)

    def test_manifest_transition_edges_match_reducer_edges(self):
        coordinator = load_coordinator()
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))

        run_edges = {
            source: set(targets)
            for source, targets in manifest["run_transitions"].items()
        }
        reducer_run_edges = {state: set() for state in manifest["run_states"]}
        for allowed, target in coordinator.RUN_EVENT_TRANSITIONS.values():
            for source in allowed - {None}:
                if source != target:
                    reducer_run_edges[source].add(target)
        self.assertEqual(run_edges, reducer_run_edges)

        lane_edges = {
            source: set(targets)
            for source, targets in manifest["lane_transitions"].items()
        }
        reducer_lane_edges = {state: set() for state in manifest["lane_states"]}
        for allowed, target in coordinator.LANE_EVENT_TRANSITIONS.values():
            for source in allowed:
                if source != target:
                    reducer_lane_edges[source].add(target)
        self.assertEqual(lane_edges, reducer_lane_edges)

    def test_transition_policy_covers_every_reachable_target(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        del manifest["transition_policy"]["lane"]["evidence_by_target"]["recovering"]
        with self.assertRaisesRegex(ValueError, "lane transition policy coverage"):
            self.runtime.validate_manifest(manifest)

    def test_identifier_limit_must_match_pinned_receipt_schema(self):
        manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        manifest["resource_limits"]["max_identifier_chars"] = 64

        with self.assertRaisesRegex(ValueError, "receipt schema contract"):
            self.runtime.validate_manifest(manifest)

    def test_receipt_schema_requires_checksum_chain(self):
        schema = json.loads(self.schema_path.read_text(encoding="utf-8"))
        required = set(schema["required"])
        self.assertTrue({"sequence", "previous_checksum", "checksum"} <= required)

    def test_restart_guidance_preserves_current_codex_process(self):
        agents_path = CODEX_SOURCE / "AGENTS.md"
        skills_dir = (
            CODEX_SOURCE / "private_skills"
            if (CODEX_SOURCE / "private_skills").is_dir()
            else CODEX_SOURCE / "skills"
        )
        doctor_path = skills_dir / "doctor" / "SKILL.md"
        if not agents_path.is_file() or not doctor_path.is_file():
            self.skipTest(
                "source-only AGENTS.md and doctor skill are outside the public bundle"
            )

        agents = agents_path.read_text(encoding="utf-8")
        doctor = doctor_path.read_text(encoding="utf-8")
        self.assertIn("Keep the current Codex process open", agents)
        self.assertIn("launch a separate Codex process", agents)
        self.assertNotIn("Restart Codex CLI", doctor)
        self.assertIn("launch a separate Codex process", doctor)

    def test_cg02_requires_useful_query_and_collection_fallbacks(self):
        common_gates = COMMON_GATES_PATH.read_text(encoding="utf-8")

        self.assertIn("no decisive result", common_gates)
        self.assertIn("reformulate", common_gates)
        self.assertIn("another relevant collection", common_gates)
        self.assertIn("direct live evidence", common_gates)

    def test_cg03_requires_isolated_mutation_worktree(self):
        common_gates = COMMON_GATES_PATH.read_text(encoding="utf-8")

        self.assertIn("isolated worktree", common_gates)
        self.assertIn("integration/default branch", common_gates)
        self.assertIn("explicitly authorized integration sync or merge", common_gates)


if __name__ == "__main__":
    unittest.main()
