import importlib.util
import json
import math
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1] / "scripts" / "bluetape_contracts.py"
)


def load_contracts():
    spec = importlib.util.spec_from_file_location(
        "bluetape_contracts_tokens", MODULE_PATH
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TokenAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contracts = load_contracts()

    def write_skill(self, skills_root, name, files):
        skill_dir = Path(skills_root) / name
        skill_dir.mkdir(parents=True)
        for relative_path, content in files.items():
            path = skill_dir / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)
        return skill_dir

    def test_reports_sorted_deterministic_byte_and_token_totals(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            self.write_skill(skills_root, "bluetape-zeta", {"SKILL.md": b"abcde"})
            self.write_skill(
                skills_root,
                "bluetape-alpha",
                {"SKILL.md": "é\n".encode("utf-8"), "references/a.md": b"1234"},
            )

            report = self.contracts.audit_token_budget(skills_root)

            self.assertEqual(
                ["bluetape-alpha", "bluetape-zeta"],
                [row["skill"] for row in report["skills"]],
            )
            expected_bytes = [7, 5]
            self.assertEqual(expected_bytes, [row["bytes"] for row in report["skills"]])
            self.assertEqual(
                [math.ceil(value / 4) for value in expected_bytes],
                [row["approx_tokens"] for row in report["skills"]],
            )
            self.assertEqual(12, report["totals"]["bytes"])
            self.assertEqual(4, report["totals"]["approx_tokens"])
            serialized = json.dumps(report, sort_keys=True)
            for forbidden in ("pass", "fail", "budget_exceeded", "hard_limit"):
                self.assertNotIn(forbidden, serialized)

    def test_baseline_produces_signed_deltas(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            self.write_skill(skills_root, "bluetape-alpha", {"SKILL.md": b"12345"})
            baseline = {
                "skills": [
                    {
                        "skill": "bluetape-alpha",
                        "bytes": 9,
                        "approx_tokens": 3,
                    }
                ]
            }

            report = self.contracts.audit_token_budget(skills_root, baseline=baseline)
            row = report["skills"][0]

            self.assertEqual(-4, row["byte_delta"])
            self.assertEqual(-1, row["token_delta"])

    def test_marked_block_counts_content_bytes_only(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            content = (
                "before\n"
                "<!-- bluetape-token:start routing -->\n"
                "é\n"
                "abc\n"
                "<!-- bluetape-token:end routing -->\n"
                "after\n"
            ).encode("utf-8")
            self.write_skill(
                skills_root, "bluetape-workflow", {"SKILL.md": content}
            )

            report = self.contracts.audit_token_budget(skills_root)

            self.assertEqual(
                [
                    {
                        "skill": "bluetape-workflow",
                        "path": "SKILL.md",
                        "name": "routing",
                        "bytes": 7,
                        "approx_tokens": 2,
                    }
                ],
                report["marked_blocks"],
            )

    def test_nested_and_unmatched_markers_have_deterministic_diagnostics(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            content = (
                "<!-- bluetape-token:end orphan -->\n"
                "<!-- bluetape-token:start outer -->\n"
                "<!-- bluetape-token:start nested -->\n"
            ).encode("utf-8")
            self.write_skill(
                skills_root, "bluetape-workflow", {"SKILL.md": content}
            )

            first = self.contracts.audit_token_budget(skills_root)
            second = self.contracts.audit_token_budget(skills_root)

            self.assertEqual(first, second)
            self.assertEqual(
                ["unmatched_token_end", "nested_token_marker", "unmatched_token_start"],
                [diagnostic["code"] for diagnostic in first["diagnostics"]],
            )

    def test_runtime_and_temporary_files_are_excluded(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            skills_root = Path(temp_dir) / "skills"
            self.write_skill(
                skills_root,
                "bluetape-alpha",
                {
                    "SKILL.md": b"1234",
                    "__pycache__/cache.pyc": b"ignored",
                    ".DS_Store": b"ignored",
                    "report.tmp": b"ignored",
                },
            )

            report = self.contracts.audit_token_budget(skills_root)

            self.assertEqual(4, report["skills"][0]["bytes"])


if __name__ == "__main__":
    unittest.main()
