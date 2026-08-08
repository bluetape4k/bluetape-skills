from __future__ import annotations

import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = next(
    path
    for path in (
        SKILL_ROOT / "scripts" / "diagram-arrowhead-audit.py",
        SKILL_ROOT / "scripts" / "executable_diagram-arrowhead-audit.py",
    )
    if path.exists()
)


def marker(width: int = 14, height: int = 14, role: str = "primary", child: str | None = None) -> str:
    child = child or '<path d="M0 0 L14 7 L0 14 Z" fill="#2563EB"/>'
    return f'<marker id="head" markerUnits="userSpaceOnUse" markerWidth="{width}" markerHeight="{height}" orient="auto" data-tip-direction="positive-x" data-role="{role}">{child}</marker>'


class DiagramArrowheadAuditTest(unittest.TestCase):
    def run_audit(self, body: str) -> subprocess.CompletedProcess[str]:
        svg = textwrap.dedent(
            f"""\
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160">
              <defs>{body.split("<!-- BODY -->")[0]}</defs>
              {body.split("<!-- BODY -->")[-1]}
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

    def test_role_size_and_dashed_line_solid_head_pass(self) -> None:
        result = self.run_audit(
            marker() + "<!-- BODY -->"
            '<path id="flow" d="M20 80 H200" fill="none" stroke="#2563EB" stroke-dasharray="6 4" marker-end="url(#head)"/>'
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("terminal_checks=1", result.stdout)

    def test_wrong_role_size_is_rejected(self) -> None:
        result = self.run_audit(
            marker(width=18, height=14) + "<!-- BODY -->"
            '<path d="M20 80 H200" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("expected 14x14 for role primary", result.stdout)

    def test_missing_role_is_rejected(self) -> None:
        result = self.run_audit(
            marker().replace(' data-role="primary"', "") + "<!-- BODY -->"
            '<path d="M20 80 H200" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("needs data-role", result.stdout)

    def test_untyped_nonstandard_size_is_rejected(self) -> None:
        result = self.run_audit(
            marker(width=13, height=13).replace(' data-role="primary"', "") + "<!-- BODY -->"
            '<path d="M20 80 H200" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("untyped size is 13x13", result.stdout)

    def test_dashed_marker_child_is_rejected(self) -> None:
        result = self.run_audit(
            marker(child='<path d="M0 0 L14 7 L0 14 Z" fill="none" stroke="#2563EB" stroke-dasharray="4 2"/>')
            + "<!-- BODY -->"
            '<path d="M20 80 H200" stroke-dasharray="6 4" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("dasharray is 4 2", result.stdout)

    def test_bend_without_marker_clearance_is_rejected(self) -> None:
        result = self.run_audit(
            marker() + "<!-- BODY -->"
            '<path id="short" d="M20 30 H120 Q120 30 120 40 V52" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("terminal clearance 12.0px < required 15.0px", result.stdout)

    def test_direct_arrowhead_requires_solid_metadata(self) -> None:
        result = self.run_audit(
            "<!-- BODY -->"
            '<polygon id="head" class="arrowhead" data-role="primary" data-size="14x14" data-tip-direction="positive-x" points="0,0 14,7 0,14" fill="#2563EB" stroke-dasharray="4 2"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("data-solid-head", result.stdout)
        self.assertIn("dasharray is 4 2", result.stdout)

    def test_reversed_marker_geometry_is_rejected(self) -> None:
        result = self.run_audit(
            marker(child='<path d="M14 0 L0 7 L14 14 Z" fill="#2563EB"/>')
            + "<!-- BODY -->"
            '<path d="M20 80 H200" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("tip points negative-x", result.stdout)

    def test_marker_start_requires_auto_start_reverse(self) -> None:
        result = self.run_audit(
            marker() + "<!-- BODY -->"
            '<path d="M200 80 H20" marker-start="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("marker-start requires orient=auto-start-reverse", result.stdout)

    def test_missing_orientation_is_rejected(self) -> None:
        result = self.run_audit(
            marker().replace(' orient="auto"', "") + "<!-- BODY -->"
            '<path d="M20 80 H200" marker-end="url(#head)"/>'
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("orient must be auto", result.stdout)


if __name__ == "__main__":
    unittest.main()
