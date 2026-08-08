from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = next(
    path
    for path in (
        SKILL_ROOT / "scripts" / "diagram-mixed-corner-audit.py",
        SKILL_ROOT / "scripts" / "executable_diagram-mixed-corner-audit.py",
    )
    if path.exists()
)


class DiagramMixedCornerAuditTest(unittest.TestCase):
    def run_audit(self, path_data: str) -> subprocess.CompletedProcess[str]:
        svg = textwrap.dedent(
            f"""\
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160">
              <path class="connector" d="{path_data}" fill="none" stroke="#334155"/>
            </svg>
            """
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "fixture.svg"
            path.write_text(svg, encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(AUDIT), str(path)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_unrounded_orthogonal_turn_is_rejected_without_q(self) -> None:
        result = self.run_audit("M20 20 H100 V120")

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("unrounded orthogonal turn", result.stdout)

    def test_rounded_orthogonal_turn_passes(self) -> None:
        result = self.run_audit("M20 20 H88 Q100 20 100 32 V120")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("q_bends=1", result.stdout)


if __name__ == "__main__":
    unittest.main()
