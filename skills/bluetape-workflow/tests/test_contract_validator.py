import importlib.util
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = SKILL_ROOT / "scripts" / "bluetape_contracts.py"
CANONICAL_MANIFEST = (
    Path(__file__).resolve().parents[1] / "references" / "workflow-manifest.json"
)
CANONICAL_RECEIPT_SCHEMA = (
    Path(__file__).resolve().parents[1] / "references" / "receipt-schema.json"
)


def resolve_sync_codex():
    candidates = (
        Path(__file__).resolve().parents[4]
        / "private_dot_local"
        / "private_bin"
        / "executable_sync-codex.sh",
        Path.home() / ".local" / "bin" / "sync-codex.sh",
    )
    return next((candidate for candidate in candidates if candidate.is_file()), candidates[0])


SYNC_CODEX = resolve_sync_codex()


def load_contracts():
    spec = importlib.util.spec_from_file_location("bluetape_contracts_test", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ContractValidatorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = load_contracts()

    def write_skill(self, skills_root, name, body="", frontmatter_name=None):
        skill_dir = Path(skills_root) / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        declared_name = name if frontmatter_name is None else frontmatter_name
        (skill_dir / "SKILL.md").write_text(
            "---\n"
            + "name: "
            + declared_name
            + "\n"
            + "description: fixture\n"
            + "---\n\n"
            + body
            + "\n",
            encoding="utf-8",
        )
        return skill_dir

    def issue_codes(self, skill_root, skills_root):
        return {
            issue["code"]
            for issue in self.contracts.validate_skill_tree(skill_root, skills_root)
        }

    def copy_phase2_skill(self, skills_root, rendered_cli=False):
        source = Path(__file__).resolve().parents[1]
        skill_root = Path(skills_root) / "bluetape-workflow"
        shutil.copytree(source, skill_root)
        manifest = json.loads(CANONICAL_MANIFEST.read_text(encoding="utf-8"))
        for route_name in {
            route
            for routes in manifest["workflow_routes"].values()
            for route in routes
        }:
            self.write_skill(skills_root, route_name)
        if rendered_cli:
            source_cli = skill_root / "scripts" / "executable_bluetape-flow.py"
            rendered_cli_path = skill_root / "scripts" / "bluetape-flow.py"
            if source_cli.is_file():
                source_cli.rename(rendered_cli_path)
            elif not rendered_cli_path.is_file():
                self.fail("guarded CLI fixture is missing")
        return skill_root

    def test_valid_frontmatter_and_known_skill_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            skill_root = self.write_skill(
                skills_root, "bluetape-alpha", "Use $known-skill."
            )
            self.write_skill(skills_root, "known-skill")

            self.assertEqual(
                [], self.contracts.validate_skill_tree(skill_root, skills_root)
            )

    def test_missing_and_mismatched_frontmatter_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            missing = skills_root / "bluetape-missing"
            missing.mkdir(parents=True)
            (missing / "SKILL.md").write_text("# Missing\n", encoding="utf-8")
            mismatch = self.write_skill(
                skills_root,
                "bluetape-mismatch",
                frontmatter_name="different-name",
            )

            self.assertIn(
                "frontmatter_missing", self.issue_codes(missing, skills_root)
            )
            self.assertIn(
                "frontmatter_name_mismatch",
                self.issue_codes(mismatch, skills_root),
            )

    def test_unknown_skill_reference_is_rejected_but_fenced_example_is_ignored(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            active = self.write_skill(
                skills_root, "bluetape-active", "Use $missing-skill."
            )
            fenced = self.write_skill(
                skills_root,
                "bluetape-fenced",
                "```markdown\nUse $missing-skill.\n```",
            )

            self.assertIn(
                "unknown_skill_reference", self.issue_codes(active, skills_root)
            )
            self.assertNotIn(
                "unknown_skill_reference", self.issue_codes(fenced, skills_root)
            )

    def test_direct_state_mutation_is_rejected_but_guarded_cli_is_allowed(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            direct = self.write_skill(
                skills_root,
                "bluetape-direct",
                "Run `echo '{}' > .bluetape/config.json`.",
            )
            guarded = self.write_skill(
                skills_root,
                "bluetape-guarded",
                "Run `scripts/bluetape-flow.py init --workflow-type A`.",
            )
            (guarded / "scripts").mkdir()
            (guarded / "scripts" / "executable_bluetape-flow.py").touch()

            self.assertIn(
                "direct_state_mutation", self.issue_codes(direct, skills_root)
            )
            self.assertNotIn(
                "direct_state_mutation", self.issue_codes(guarded, skills_root)
            )

    def test_active_omx_dependencies_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            for index, dependency in enumerate(
                ("`.omx/run.json`", "`omx team 2`", "`OMX_RUN_ID`"), start=1
            ):
                with self.subTest(dependency=dependency):
                    skill_root = self.write_skill(
                        skills_root,
                        "bluetape-omx-" + str(index),
                        "Depends on " + dependency + ".",
                    )
                    self.assertIn(
                        "omx_dependency", self.issue_codes(skill_root, skills_root)
                    )

    def test_unsafe_native_lifecycle_guidance_is_rejected(self):
        cases = (
            (
                "spawn-order",
                "Call spawn_agent before lane-create and lane-start.",
                "native_spawn_order",
            ),
            (
                "heartbeat-completion",
                "A heartbeat proves completion evidence.",
                "heartbeat_as_completion",
            ),
            (
                "interrupt-order",
                "Call interrupt_agent before probe-sent authority.",
                "native_interrupt_order",
            ),
            (
                "replacement-id",
                "Replace a writer by reusing the same replacement lane id.",
                "replacement_identity",
            ),
            (
                "direct-lane-json",
                "Python writes .bluetape/lanes/build.json directly.",
                "direct_runtime_json",
            ),
            (
                "completion-order",
                "Mark topology complete without completion-check.",
                "completion_check_missing",
            ),
            (
                "python-native",
                "Python invokes native spawn_agent for the main session.",
                "python_native_tool_claim",
            ),
            (
                "fencing-argv",
                "Pass --owner-token in argv and expose owner_token in JSON.",
                "owner_fencing_exposure",
            ),
            (
                "unsafe-scope",
                "Accept a symlinked noncanonical write scope.",
                "unsafe_write_scope",
            ),
            (
                "same-session",
                "Apply new guidance and run native dogfood in the same session.",
                "same_session_dogfood",
            ),
        )
        for name, guidance, expected_code in cases:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                skills_root = Path(temp_dir) / "skills"
                skill_root = self.write_skill(
                    skills_root, "bluetape-" + name, guidance
                )
                self.assertIn(
                    expected_code, self.issue_codes(skill_root, skills_root)
                )

    def test_missing_local_inline_code_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            skill_root = self.write_skill(
                skills_root,
                "bluetape-local",
                "Read `references/missing.md`, `templates/missing.md`, and "
                "`scripts/missing.py`.",
            )

            issues = self.contracts.validate_skill_tree(skill_root, skills_root)
            self.assertEqual(
                3,
                sum(issue["code"] == "missing_local_reference" for issue in issues),
            )

    def test_manifest_route_and_router_checklist_drift_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            manifest = json.loads(CANONICAL_MANIFEST.read_text(encoding="utf-8"))
            checklist = "\n".join(
                "- [ ] **" + checklist_id + " — fixture**"
                for checklist_id in manifest["router_checklist_ids"][:-1]
            )
            checklist += "\n- [ ] **WF-99 — drift**"
            skill_root = self.write_skill(
                skills_root, "bluetape-workflow", checklist
            )
            references = skill_root / "references"
            references.mkdir()
            (references / "workflow-manifest.json").write_text(
                json.dumps(manifest), encoding="utf-8"
            )
            route_names = {
                route
                for routes in manifest["workflow_routes"].values()
                for route in routes
            }
            missing_route = sorted(route_names)[0]
            for route_name in route_names - {missing_route}:
                self.write_skill(skills_root, route_name)

            codes = self.issue_codes(skill_root, skills_root)

            self.assertIn("manifest_route_missing", codes)
            self.assertIn("router_checklist_missing", codes)
            self.assertIn("router_checklist_drift", codes)

    def test_receipt_schema_syntax_and_manifest_event_drift_are_rejected(self):
        for case in ("invalid-json", "event-drift"):
            with self.subTest(case=case), tempfile.TemporaryDirectory() as temp_dir:
                skills_root = Path(temp_dir) / "skills"
                manifest = json.loads(
                    CANONICAL_MANIFEST.read_text(encoding="utf-8")
                )
                checklist = "\n".join(
                    "- [ ] **" + checklist_id + " — fixture**"
                    for checklist_id in manifest["router_checklist_ids"]
                )
                skill_root = self.write_skill(
                    skills_root, "bluetape-workflow", checklist
                )
                references = skill_root / "references"
                references.mkdir()
                (references / "workflow-manifest.json").write_text(
                    json.dumps(manifest), encoding="utf-8"
                )
                for route_name in {
                    route
                    for routes in manifest["workflow_routes"].values()
                    for route in routes
                }:
                    self.write_skill(skills_root, route_name)
                schema_path = references / "receipt-schema.json"
                if case == "invalid-json":
                    schema_path.write_text("{", encoding="utf-8")
                    expected_code = "receipt_schema_invalid"
                else:
                    schema = json.loads(
                        CANONICAL_RECEIPT_SCHEMA.read_text(encoding="utf-8")
                    )
                    schema["properties"]["event_type"]["enum"].pop()
                    schema_path.write_text(json.dumps(schema), encoding="utf-8")
                    expected_code = "receipt_event_drift"

                self.assertIn(
                    expected_code, self.issue_codes(skill_root, skills_root)
                )

    def test_phase2_guidance_requires_every_guarded_command(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            source = Path(__file__).resolve().parents[1]
            skill_root = skills_root / "bluetape-workflow"
            shutil.copytree(source, skill_root)
            manifest = json.loads(CANONICAL_MANIFEST.read_text(encoding="utf-8"))
            for route_name in {
                route
                for routes in manifest["workflow_routes"].values()
                for route in routes
            }:
                self.write_skill(skills_root, route_name)
            topology = skill_root / "references" / "topology-contract.md"
            topology.write_text(
                topology.read_text(encoding="utf-8").replace("`lane-cancel`", "`lane-stop`"),
                encoding="utf-8",
            )

            self.assertIn(
                "cli_command_guidance_missing",
                self.issue_codes(skill_root, skills_root),
            )

    def test_phase2_coordinator_covers_every_manifest_event(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            source = Path(__file__).resolve().parents[1]
            skill_root = skills_root / "bluetape-workflow"
            shutil.copytree(source, skill_root)
            manifest = json.loads(CANONICAL_MANIFEST.read_text(encoding="utf-8"))
            for route_name in {
                route
                for routes in manifest["workflow_routes"].values()
                for route in routes
            }:
                self.write_skill(skills_root, route_name)
            coordinator = skill_root / "scripts" / "bluetape_coordinator.py"
            coordinator.write_text(
                coordinator.read_text(encoding="utf-8").replace(
                    '"candidate_rejected"', '"candidate_declined"'
                ),
                encoding="utf-8",
            )

            self.assertIn(
                "coordinator_event_missing",
                self.issue_codes(skill_root, skills_root),
            )

    def test_phase2_validator_accepts_live_rendered_cli_name(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            skill_root = self.copy_phase2_skill(skills_root, rendered_cli=True)

            codes = self.issue_codes(skill_root, skills_root)

            self.assertNotIn("guarded_cli_missing", codes)
            self.assertNotIn("guarded_cli_invalid", codes)

    def test_phase2_partial_live_apply_reports_missing_coordinator(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            skill_root = self.copy_phase2_skill(skills_root, rendered_cli=True)
            (skill_root / "scripts" / "bluetape_coordinator.py").unlink()

            codes = self.issue_codes(skill_root, skills_root)

            self.assertNotIn("guarded_cli_missing", codes)
            self.assertIn("coordinator_missing", codes)

    def test_phase2_live_validator_failure_is_reported(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            skill_root = self.copy_phase2_skill(skills_root, rendered_cli=True)
            (skill_root / "scripts" / "bluetape-flow.py").write_text(
                "raise RuntimeError('fixture validator failure')\n",
                encoding="utf-8",
            )

            codes = self.issue_codes(skill_root, skills_root)

            self.assertNotIn("guarded_cli_missing", codes)
            self.assertIn("guarded_cli_invalid", codes)

    def test_sync_status_propagates_managed_drift_command_failure(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            fixture_root = Path(temp_dir)
            home = fixture_root / "home"
            source = fixture_root / "source"
            bin_dir = fixture_root / "bin"
            home.mkdir()
            bin_dir.mkdir()
            for relative in (
                "private_dot_codex/private_prompts",
                "private_dot_codex/private_rules",
                "private_dot_codex/private_skills",
                "private_dot_codex/hooks",
            ):
                (source / relative).mkdir(parents=True, exist_ok=True)
            chezmoi = bin_dir / "chezmoi"
            chezmoi.write_text("#!/bin/sh\nexit 41\n", encoding="utf-8")
            chezmoi.chmod(0o755)
            env = os.environ.copy()
            env.update(
                {
                    "DOTFILES_DIR": str(source),
                    "HOME": str(home),
                    "PATH": str(bin_dir) + os.pathsep + env["PATH"],
                }
            )

            result = subprocess.run(
                ["bash", str(SYNC_CODEX), "--status", "--quiet"],
                capture_output=True,
                check=False,
                env=env,
                text=True,
            )

            self.assertEqual(41, result.returncode)


if __name__ == "__main__":
    unittest.main()
