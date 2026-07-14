import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]


def resolve_flow(skill_root):
    candidates = (
        Path(skill_root) / "scripts" / "executable_bluetape-flow.py",
        Path(skill_root) / "scripts" / "bluetape-flow.py",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


FLOW = resolve_flow(SKILL_ROOT)

COMMANDS = {
    "run-approve", "run-start", "run-recovery-start", "run-recovery-finish",
    "run-fail", "run-block", "run-cancel", "lane-create", "lane-start",
    "startup-ack", "stall-record", "stall-clear", "probe-ack", "lane-complete",
    "lane-fail", "lane-block", "lane-cancel", "heartbeat", "liveness-check",
    "probe-sent", "interrupt-result", "lane-reassign", "replacement-repair",
    "replacement-block", "replacement-close", "resume-check", "resume",
    "receipt-diagnose", "recovery-run-create", "handoff-create",
    "live-report-create", "topology-register", "topology-remove", "check-result",
    "component-evidence", "completion-check", "complete",
}
READ_ONLY_COMMANDS = {
    "resume-check", "receipt-diagnose", "liveness-check", "completion-check",
}
COMMAND_CONTRACT = {
    command: {
        "argparse_signature": "explicit-subparser",
        "required_capability": "manifest-1.1",
        "event_or_result": command,
        "input_schema": "fixed-json-or-scalar",
        "success_schema": ("ok", "run_id", "sequence", "checksum"),
        "typed_errors": (2, 3, 4, 5, 6, 7),
        "mutation": command not in READ_ONLY_COMMANDS,
        "next_command": "resume-check" if command not in READ_ONLY_COMMANDS else None,
    }
    for command in COMMANDS
}


class FlowCliTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.state = root / ".bluetape"
        self.repo = root / "repo"
        self.repo.mkdir()
        self.owner = self.state / "handles" / "cli.owner"

    def tearDown(self):
        self.temp.cleanup()

    def write_json(self, name, value):
        path = Path(self.temp.name) / name
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    def invoke(self, *args, expected=0):
        completed = subprocess.run(
            [sys.executable, str(FLOW), "--state-root", str(self.state), *map(str, args)],
            cwd=SKILL_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(expected, completed.returncode, completed.stderr)
        stream = completed.stdout if expected == 0 else completed.stderr
        payload = json.loads(stream)
        self.assertEqual(expected == 0, payload["ok"])
        return payload, completed

    def init(self):
        payload, completed = self.invoke(
            "init", "--workflow-type", "A", "--repo-root", self.repo,
            "--owner-file", self.owner, "--component", "runtime",
        )
        owner_payload = json.loads(self.owner.read_text(encoding="utf-8"))
        self.assertNotIn(owner_payload["token"], completed.stdout)
        return payload["run_id"]

    def test_help_lists_every_phase2_command(self):
        completed = subprocess.run(
            [sys.executable, str(FLOW), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode)
        for command in COMMANDS:
            self.assertIn(command, completed.stdout)
        self.assertEqual(COMMANDS, set(COMMAND_CONTRACT))
        self.assertFalse(COMMAND_CONTRACT["completion-check"]["mutation"])
        self.assertTrue(COMMAND_CONTRACT["complete"]["mutation"])

    def test_command_help_names_capability_safe_next_and_migration_boundary(self):
        for command in COMMANDS:
            with self.subTest(command=command):
                completed = subprocess.run(
                    [sys.executable, str(FLOW), command, "--help"],
                    text=True,
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(0, completed.returncode, completed.stderr)
                help_text = " ".join(completed.stdout.split())
                self.assertIn("Capability:", help_text)
                self.assertIn("Safe next:", help_text)
                self.assertIn("In-place migration is unavailable.", help_text)

        completed = subprocess.run(
            [sys.executable, str(FLOW), "--help"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertIn("UTC timestamps end in Z.", completed.stdout)
        self.assertIn("Phase 1 supports only", completed.stdout)

    def test_full_subprocess_path_completes_without_manifest_reads(self):
        run_id = self.init()
        approval = self.write_json("approval.json", [{"kind": "approval", "summary": "approved"}])
        start = self.write_json("start.json", [{"kind": "plan", "summary": "started"}])
        assignment = self.write_json("assignment.json", [{"kind": "plan", "summary": "assigned"}])
        lane = self.write_json("lane.json", {
            "lane_id": "build", "agent_id": "agent-1", "assignment": "Build runtime",
            "write_scope": ["scripts"], "fallback": "main session",
            "observed_at": "2026-07-14T01:00:00Z",
            "startup_ack_deadline": "2026-07-14T01:00:30Z",
            "command_deadline": "2026-07-14T01:10:00Z",
        })
        topology = self.write_json("topology.json", [{
            "id": "runtime", "required": True, "description": "Runtime",
            "owner_lane": "build", "required_checks": ["unit"], "dependencies": [],
            "evidence_refs": [], "coverage_state": "missing",
        }])
        topology_evidence = self.write_json("topology-evidence.json", [{"kind": "plan", "summary": "topology"}])
        lifecycle = self.write_json("lifecycle.json", [{"kind": "result", "summary": "lifecycle"}])
        changed = self.write_json("changed.json", ["scripts/runtime.py"])
        check_input = self.write_json("check.json", {"component_id": "runtime", "check_id": "unit", "passed": True})
        check_evidence = self.write_json("check-evidence.json", [{"kind": "test", "summary": "passed"}])
        component = self.write_json("component.json", {"component_id": "runtime"})
        component_evidence = self.write_json("component-evidence.json", [{"kind": "result", "summary": "covered"}])
        main_evidence = self.write_json("main.json", [{"kind": "main", "summary": "verified"}])
        common = ("--run-id", run_id, "--owner-file", self.owner)

        self.invoke("run-approve", *common, "--evidence", approval, "--at", "2026-07-14T01:00:00Z")
        self.invoke("run-start", *common, "--evidence", start, "--at", "2026-07-14T01:00:01Z")
        self.invoke("lane-create", *common, "--input", lane, "--evidence", assignment)
        self.invoke("topology-register", *common, "--input", topology, "--evidence", topology_evidence)
        for command, at in (("lane-start", "2026-07-14T01:00:02Z"), ("startup-ack", "2026-07-14T01:00:03Z")):
            self.invoke(command, *common, "--lane-id", "build", "--agent-id", "agent-1", "--at", at, "--evidence", lifecycle)
        self.invoke("lane-complete", *common, "--lane-id", "build", "--agent-id", "agent-1", "--at", "2026-07-14T01:00:04Z", "--changed-paths", changed, "--evidence", lifecycle)
        self.invoke("check-result", *common, "--input", check_input, "--evidence", check_evidence)
        self.invoke("component-evidence", *common, "--input", component, "--evidence", component_evidence)
        check, _ = self.invoke("completion-check", "--run-id", run_id)
        self.assertTrue(check["missing_main_verification"])
        completed, _ = self.invoke("complete", *common, "--evidence", main_evidence)
        self.assertEqual("completed", completed["run_state"])
        inspection, _ = self.invoke("resume-check", "--run-id", run_id)
        live_report = self.write_json("live-report.json", {
            "canonical_sha": "a" * 64,
            "agents_hash": "b" * 64,
            "skill_hash": "c" * 64,
            "manifest_hash": inspection["manifest_hash"],
            "run_id": run_id,
            "owner_epoch": inspection["owner_epoch"],
            "receipt_head": inspection["last_checksum"],
            "target_hashes": {"private_dot_codex": "d" * 64},
            "command_ids": ["chezmoi-diff"],
            "timestamps": ["2026-07-14T01:00:05Z"],
            "exit_status": 0,
            "source_hash": "e" * 64,
            "rendered_hash": "f" * 64,
            "live_hash": "1" * 64,
            "evidence_refs": [{"kind": "command", "summary": "verified"}],
        })
        live, _ = self.invoke(
            "live-report-create", "--run-id", run_id,
            "--owner-file", self.owner, "--input", live_report,
        )
        self.assertEqual("completed", live["run_state"])
        error, _ = self.invoke("complete", *common, "--evidence", main_evidence, expected=5)
        self.assertEqual("coordinator_conflict", error["error"])

    def test_corruption_and_contract_errors_have_stable_exit_codes(self):
        run_id = self.init()
        invalid, _ = self.invoke("run-start", "--run-id", run_id, "--owner-file", self.owner, expected=2)
        self.assertEqual("contract_error", invalid["error"])
        evidence = self.write_json("evidence.json", [{"kind": "approval", "summary": "approved"}])
        common = ("--run-id", run_id, "--owner-file", self.owner, "--evidence", evidence)
        self.invoke("run-approve", *common, "--at", "2026-07-14T01:00:00Z")
        self.invoke("run-start", *common, "--at", "2026-07-14T01:00:01Z")
        blocked, _ = self.invoke("complete", *common, expected=6)
        self.assertEqual("completion_blocked", blocked["error"])
        receipt = self.state / "runs" / run_id / "receipt.jsonl"
        with receipt.open("ab") as stream:
            stream.write(b'{"event_type":')
        corrupt, _ = self.invoke("verify", "--run-id", run_id, expected=3)
        self.assertEqual("receipt_corrupt", corrupt["error"])
        self.assertEqual("receipt-diagnose", corrupt["next_command"])
        diagnosis, _ = self.invoke("receipt-diagnose", "--run-id", run_id)
        self.assertEqual("blocked", diagnosis["effective_state"])
        diagnosis_path = self.write_json("diagnosis.json", diagnosis)
        recovery_owner = self.state / "handles" / "recovery.owner"
        recovered, _ = self.invoke(
            "recovery-run-create", "--run-id", run_id,
            "--owner-file", recovery_owner, "--input", diagnosis_path,
            "--evidence", evidence,
        )
        self.assertNotEqual(run_id, recovered["new_run_id"])
        verified, _ = self.invoke("verify", "--run-id", recovered["new_run_id"])
        self.assertEqual(1, verified["event_count"])

    def test_run_id_traversal_is_rejected_as_contract_error(self):
        invalid, _ = self.invoke("verify", "--run-id", "../escape", expected=2)
        self.assertEqual("contract_error", invalid["error"])

    def test_mutation_expected_head_is_a_cli_cas_precondition(self):
        run_id = self.init()
        initial, _ = self.invoke("verify", "--run-id", run_id)
        evidence = self.write_json(
            "cas-evidence.json", [{"kind": "approval", "summary": "approved"}]
        )
        common = (
            "--run-id", run_id,
            "--owner-file", self.owner,
            "--evidence", evidence,
        )
        approved, _ = self.invoke(
            "run-approve",
            *common,
            "--expected-head", initial["checksum"],
            "--at", "2026-07-14T01:00:00Z",
        )

        stale, _ = self.invoke(
            "run-start",
            *common,
            "--expected-head", initial["checksum"],
            "--at", "2026-07-14T01:00:01Z",
            expected=5,
        )

        self.assertEqual("coordinator_conflict", stale["error"])
        verified, _ = self.invoke("verify", "--run-id", run_id)
        self.assertEqual(2, verified["event_count"])
        self.assertEqual(approved["checksum"], verified["checksum"])

    def test_resume_rotates_owner_without_printing_fencing_value(self):
        run_id = self.init()
        evidence = self.write_json("resume.json", [{"kind": "resume", "summary": "verified"}])
        new_owner = self.state / "handles" / "resumed.owner"
        before, _ = self.invoke("resume-check", "--run-id", run_id)
        resumed, completed = self.invoke(
            "resume", "--run-id", run_id, "--owner-file", self.owner,
            "--new-owner-file", new_owner, "--evidence", evidence,
        )
        self.assertEqual(before["owner_epoch"] + 1, resumed["owner_epoch"])
        token = json.loads(new_owner.read_text(encoding="utf-8"))["token"]
        self.assertNotIn(token, completed.stdout)
        self.assertFalse(self.owner.exists())

    def test_handoff_report_is_immutable_idempotent_and_secret_safe(self):
        run_id = self.init()
        evidence = self.write_json("evidence.json", [{"kind": "approval", "summary": "approved"}])
        common = ("--run-id", run_id, "--owner-file", self.owner, "--evidence", evidence)
        self.invoke("run-approve", *common, "--at", "2026-07-14T01:00:00Z")
        self.invoke("run-start", *common, "--at", "2026-07-14T01:00:01Z")
        inspection, _ = self.invoke("resume-check", "--run-id", run_id)
        checksum = "a" * 64
        report = {
            "canonical_sha": checksum,
            "agents_hash": "b" * 64,
            "skill_hash": "c" * 64,
            "manifest_hash": inspection["manifest_hash"],
            "run_id": run_id,
            "owner_epoch": inspection["owner_epoch"],
            "receipt_head": inspection["last_checksum"],
            "target_hashes": {"private_dot_codex": "d" * 64},
        }
        report_path = self.write_json("handoff.json", report)
        first, completed = self.invoke(
            "handoff-create", "--run-id", run_id, "--owner-file", self.owner,
            "--input", report_path,
        )
        second, _ = self.invoke(
            "handoff-create", "--run-id", run_id, "--owner-file", self.owner,
            "--input", report_path,
        )
        self.assertEqual(first["sequence"], second["sequence"])
        owner_token = json.loads(self.owner.read_text(encoding="utf-8"))["token"]
        self.assertNotIn(owner_token, completed.stdout)
        immutable = self.state / first["report_path"]
        self.assertEqual(0o600, immutable.stat().st_mode & 0o777)

        secret_report = dict(report)
        secret_report["token"] = owner_token
        secret_path = self.write_json("secret-report.json", secret_report)
        rejected, _ = self.invoke(
            "handoff-create", "--run-id", run_id, "--owner-file", self.owner,
            "--input", secret_path, expected=2,
        )
        self.assertEqual("contract_error", rejected["error"])


if __name__ == "__main__":
    unittest.main()
