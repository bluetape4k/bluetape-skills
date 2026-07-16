from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = SKILL_ROOT / "scripts" / "diagram-connector-audit.py"


class DiagramConnectorAuditTest(unittest.TestCase):
    def run_audit(self, body: str) -> subprocess.CompletedProcess[str]:
        svg = textwrap.dedent(
            f"""\
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
              <style>
                .edgeLabel {{ font-size: 20px; }}
                .edge {{ fill: none; stroke: #334155; }}
              </style>
              {body}
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

    def test_intrusion_uses_ancestor_relationship_name(self) -> None:
        result = self.run_audit(
            """
            <rect class="card" x="40" y="40" width="100" height="80"/>
            <g data-from="WritePath" data-to="FrontCache">
              <path class="edge" d="M0 60 H100"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("WritePath-to-FrontCache", result.stdout)
        self.assertIn("intrusions=1", result.stdout)

    def test_shared_connector_segment_is_rejected(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 40 H180"/>
            </g>
            <g data-from="Gamma" data-to="Delta">
              <path class="edge" d="M100 40 H260"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("shared_segments=1", result.stdout)
        self.assertIn("Alpha-to-Beta", result.stdout)
        self.assertIn("Gamma-to-Delta", result.stdout)

    def test_short_shared_connector_segment_is_rejected(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 40 H100"/>
            </g>
            <g data-from="Gamma" data-to="Delta">
              <path class="edge" d="M92.5 40 H180"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("shared_segments=1", result.stdout)

    def test_label_overlapping_card_is_rejected(self) -> None:
        result = self.run_audit(
            """
            <rect class="card" x="40" y="40" width="150" height="90"/>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 20 H260"/>
              <text class="edgeLabel" x="70" y="85">inside card</text>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_cards=1", result.stdout)
        self.assertIn("inside card", result.stdout)

    def test_overlapping_labels_are_rejected(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 30 H260"/>
              <text class="edgeLabel" x="80" y="100">first label</text>
            </g>
            <g data-from="Gamma" data-to="Delta">
              <path class="edge" d="M10 190 H260"/>
              <text class="edgeLabel" x="95" y="100">second label</text>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_labels=1", result.stdout)
        self.assertIn("first label", result.stdout)
        self.assertIn("second label", result.stdout)

    def test_unrelated_connector_crossing_label_is_rejected(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 30 H260"/>
              <text class="edgeLabel" x="70" y="100">guarded label</text>
            </g>
            <g data-from="Gamma" data-to="Delta">
              <path class="edge" d="M110 55 V125"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_connectors=1", result.stdout)
        self.assertIn("guarded label", result.stdout)
        self.assertIn("Gamma-to-Delta", result.stdout)

    def test_duplicate_relationship_names_do_not_hide_crossings(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 80 H260"/>
            </g>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M120 20 V160"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("crossings=1", result.stdout)

    def test_duplicate_relationship_names_do_not_claim_other_connector(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 30 H260"/>
              <text class="edgeLabel" x="70" y="100">guarded label</text>
            </g>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M110 55 V125"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_connectors=1", result.stdout)
        self.assertIn("guarded label", result.stdout)

    def test_unscoped_label_does_not_claim_every_root_connector(self) -> None:
        result = self.run_audit(
            """
            <g id="edges">
              <path id="horizontal" class="edge" d="M10 30 H260"/>
              <path id="vertical" class="edge" d="M110 55 V125"/>
            </g>
            <text class="edgeLabel" x="70" y="100">unscoped label</text>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_connectors=1", result.stdout)
        self.assertIn("unscoped label", result.stdout)
        self.assertIn("vertical", result.stdout)

    def test_translated_label_group_overlapping_card_is_rejected(self) -> None:
        result = self.run_audit(
            """
            <rect class="card" x="150" y="70" width="120" height="90"/>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 30 H260"/>
              <g class="edgeLabel" transform="translate(170 80)">
                <rect width="80" height="28"/>
                <text x="40" y="20" text-anchor="middle">moved</text>
              </g>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("label_cards=1", result.stdout)
        self.assertIn("moved", result.stdout)

    def test_scaled_or_matrix_label_collision_is_rejected(self) -> None:
        transforms = (
            "translate(100 80) scale(2)",
            "matrix(2 0 0 2 100 80)",
        )
        for transform in transforms:
            with self.subTest(transform=transform):
                result = self.run_audit(
                    f"""
                    <g data-from="Alpha" data-to="Beta">
                      <path class="edge" d="M10 30 H260"/>
                      <g class="edgeLabel" transform="{transform}">
                        <rect width="60" height="20"/>
                        <text x="30" y="15" text-anchor="middle">scaled</text>
                      </g>
                    </g>
                    <g data-from="Gamma" data-to="Delta">
                      <path class="edge" d="M190 60 V140"/>
                    </g>
                    """
                )

                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn("label_connectors=1", result.stdout)
                self.assertIn("Gamma-to-Delta", result.stdout)

    def test_multiple_path_subpaths_do_not_create_a_fictitious_bridge(self) -> None:
        result = self.run_audit(
            """
            <rect class="card" x="80" y="30" width="40" height="40"/>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 50 H40 M160 50 H190"/>
            </g>
            """
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("intrusions=0", result.stdout)

    def test_unsupported_path_command_fails_closed_without_traceback(self) -> None:
        result = self.run_audit(
            """
            <path class="edge" d="M10 10 S 20 20 30 30"/>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("unsupported path command S", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_unbounded_relationship_label_fails_closed(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M10 30 H260"/>
              <text class="edgeLabel">missing coordinates</text>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("relationship label could not be bounded", result.stdout)
        self.assertIn("missing coordinates", result.stdout)

    def test_unsupported_transform_fails_closed_without_traceback(self) -> None:
        result = self.run_audit(
            """
            <g data-from="Alpha" data-to="Beta" transform="warp(2)">
              <path class="edge" d="M10 30 H260"/>
            </g>
            """
        )

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("FAIL schema: unsupported transform operation", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_malformed_transform_arguments_fail_closed(self) -> None:
        transforms = (
            "translate(10 nonsense 20)",
            "matrix(1,0,0,1,10,20 trailing)",
            "translate(1.2.3)",
            "matrix(1.0.0.1.10.20.30)",
        )
        for transform in transforms:
            with self.subTest(transform=transform):
                result = self.run_audit(
                    f"""
                    <g data-from="Alpha" data-to="Beta" transform="{transform}">
                      <path class="edge" d="M10 30 H260"/>
                    </g>
                    """
                )

                self.assertEqual(1, result.returncode, result.stdout + result.stderr)
                self.assertIn(
                    "FAIL schema: unsupported transform syntax", result.stdout
                )
                self.assertNotIn("Traceback", result.stderr)

    def test_clear_relationship_passes_all_geometry_counts(self) -> None:
        result = self.run_audit(
            """
            <rect class="card" x="10" y="80" width="90" height="80"/>
            <rect class="card" x="300" y="80" width="90" height="80"/>
            <g data-from="Alpha" data-to="Beta">
              <path class="edge" d="M100 120 H300"/>
              <g class="edgeLabel" transform="translate(155 55)">
                <rect width="90" height="28"/>
                <text x="45" y="20" text-anchor="middle">clear</text>
              </g>
            </g>
            """
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("shared_segments=0", result.stdout)
        self.assertIn("label_cards=0", result.stdout)
        self.assertIn("label_labels=0", result.stdout)
        self.assertIn("label_connectors=0", result.stdout)


if __name__ == "__main__":
    unittest.main()
