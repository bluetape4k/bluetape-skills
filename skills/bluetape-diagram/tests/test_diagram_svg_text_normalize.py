from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import tempfile
import textwrap
import unittest
import xml.etree.ElementTree as ET


SKILL_ROOT = Path(__file__).resolve().parents[1]
NORMALIZER = SKILL_ROOT / "scripts" / "diagram-svg-text-normalize.py"


class DiagramSvgTextNormalizeTest(unittest.TestCase):
    def write_fixture(self, directory: str) -> Path:
        path = Path(directory) / "fixture.svg"
        path.write_text(
            textwrap.dedent(
                """\
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 240">
                  <style>
                    .canvas { fill: #F8FAFC; }
                    .panelTitle { font-size: 24px; fill: #0F172A; paint-order: stroke; stroke: #fff; stroke-width: 4px; stroke-linejoin: round; }
                    .edgeLabel { font-size: 12px; fill: #334155; paint-order: stroke; stroke: #FFFFFF; stroke-width: 5px; }
                    .badge { fill: #2563EB; paint-order: stroke; stroke: #fff; stroke-width: 4px; }
                    .shared { fill: #0F172A; paint-order: stroke; stroke: #fff; stroke-width: 4px; }
                    .split { fill: #0F172A; stroke: #fff; stroke-width: 4px; }
                    .code, .member { font-family: "Comic Mono"; font-size: 14px; fill: #334155; }
                  </style>
                  <rect class="canvas" width="400" height="240"/>
                  <rect class="badge" x="360" y="20" width="20" height="20"/>
                  <rect class="shared" x="330" y="50" width="20" height="20"/>
                  <text class="panelTitle" x="20" y="40">Application lane</text>
                  <text class="edgeLabel" x="20" y="80">loads</text>
                  <text style="fill:#0F172A;paint-order:stroke;stroke:#fff;stroke-width:4px" x="180" y="40">Inline lane</text>
                  <text fill="#0F172A" paint-order="stroke" stroke="white" stroke-width="4" x="180" y="80">Attribute lane</text>
                  <text class="shared" x="180" y="110">Shared class lane</text>
                  <text class="split" style="paint-order:stroke" x="180" y="140">Split cascade lane</text>
                  <text class="code" x="20" y="120">val answer: Int = 42</text>
                  <text class="code" x="20" y="150">findById(id: Long): User?</text>
                  <text class="member" x="20" y="180">reader-facing prose</text>
                  <text class="member" data-code-snippet="kotlin" x="20" y="210">virtualFutureOf { ... }</text>
                </svg>
                """
            ),
            encoding="utf-8",
        )
        return path

    def run_normalizer(
        self, path: Path, *extra: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(NORMALIZER), *extra, str(path)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_check_rejects_cairosvg_text_hazards_and_plain_code(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory)

            result = self.run_normalizer(path)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("text_hazards=6", result.stdout)
            self.assertIn("code_without_highlight=3", result.stdout)

    def test_write_removes_hazards_and_adds_token_highlighting(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory)

            write_result = self.run_normalizer(path, "--write")
            check_result = self.run_normalizer(path)

            self.assertEqual(0, write_result.returncode, write_result.stdout)
            self.assertEqual(0, check_result.returncode, check_result.stdout)
            content = path.read_text(encoding="utf-8")
            self.assertIn(
                ".badge { fill: #2563EB; paint-order: stroke; stroke: #fff; stroke-width: 4px; }",
                content,
            )
            self.assertIn(
                ".shared { fill: #0F172A; paint-order: stroke; stroke: #fff; stroke-width: 4px; }",
                content,
            )
            self.assertIn(
                'style="fill:#0F172A;paint-order:normal!important;stroke:none!important;stroke-width:0!important;"',
                content,
            )
            self.assertNotIn('paint-order="stroke"', content)
            self.assertNotIn('stroke="white"', content)
            self.assertIn(
                'class="shared" x="180" y="110" style="paint-order:normal!important;stroke:none!important;stroke-width:0!important;"',
                content,
            )
            self.assertIn(
                'class="split" x="180" y="140" style="paint-order:normal!important;stroke:none!important;stroke-width:0!important;"',
                content,
            )
            self.assertIn('class="syntax-keyword">val</tspan>', content)
            self.assertIn('class="syntax-type">Int</tspan>', content)
            self.assertIn('class="syntax-number">42</tspan>', content)
            self.assertIn('class="syntax-function">findById</tspan>', content)
            self.assertIn('class="syntax-type">User</tspan>', content)
            self.assertIn('class="syntax-operator">{</tspan>', content)
            self.assertIn(">reader-facing prose</text>", content)
            self.assertFalse(
                any(line.endswith((" ", "\t")) for line in content.splitlines())
            )

            root = ET.parse(path).getroot()
            texts = {
                " ".join("".join(node.itertext()).split())
                for node in root.iter()
                if node.tag.rsplit("}", 1)[-1] == "text"
            }
            self.assertIn("val answer: Int = 42", texts)
            self.assertIn("findById(id: Long): User?", texts)
            self.assertIn("virtualFutureOf { ... }", texts)

    def test_missing_token_fill_is_rejected_and_repaired(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing-token-style.svg"
            path.write_text(
                textwrap.dedent(
                    """\
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 80">
                      <style>.syntax-keyword{fill:#7E22CE}</style>
                      <text data-code-snippet="kotlin" x="10" y="40"><tspan class="syntax-keyword">val</tspan> answer = <tspan class="syntax-number">42</tspan></text>
                    </svg>
                    """
                ),
                encoding="utf-8",
            )

            check_before = self.run_normalizer(path)
            write_result = self.run_normalizer(path, "--write")
            check_after = self.run_normalizer(path)

            self.assertEqual(1, check_before.returncode, check_before.stdout)
            self.assertIn("code_without_highlight=1", check_before.stdout)
            self.assertEqual(0, write_result.returncode, write_result.stdout)
            self.assertEqual(0, check_after.returncode, check_after.stdout)
            content = path.read_text(encoding="utf-8")
            self.assertIn(".syntax-keyword{fill:#7E22CE}", content)
            self.assertIn(".syntax-number{fill:#C2410C}", content)

    def test_grouped_id_and_important_css_only_override_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cascade.svg"
            path.write_text(
                textwrap.dedent(
                    """\
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 100">
                      <style>
                        .badge,.title{paint-order:stroke;stroke:#fff;stroke-width:4px}
                        #lane{paint-order:stroke;stroke:#fff !important;stroke-width:4px}
                      </style>
                      <rect class="badge" x="5" y="5" width="20" height="20"/>
                      <text class="title" x="40" y="30">Grouped title</text>
                      <text id="lane" x="40" y="70">Important lane</text>
                    </svg>
                    """
                ),
                encoding="utf-8",
            )

            check_before = self.run_normalizer(path)
            write_result = self.run_normalizer(path, "--write")
            check_after = self.run_normalizer(path)

            self.assertEqual(1, check_before.returncode, check_before.stdout)
            self.assertIn("text_hazards=2", check_before.stdout)
            self.assertEqual(0, write_result.returncode, write_result.stdout)
            self.assertEqual(0, check_after.returncode, check_after.stdout)
            content = path.read_text(encoding="utf-8")
            self.assertIn(
                ".badge,.title{paint-order:stroke;stroke:#fff;stroke-width:4px}",
                content,
            )
            self.assertIn(
                "#lane{paint-order:stroke;stroke:#fff !important;stroke-width:4px}",
                content,
            )
            self.assertEqual(2, content.count("stroke:none!important"))

    def test_write_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = self.write_fixture(directory)
            first = self.run_normalizer(path, "--write")
            first_content = path.read_text(encoding="utf-8")

            second = self.run_normalizer(path, "--write")
            second_content = path.read_text(encoding="utf-8")

            self.assertEqual(0, first.returncode, first.stdout)
            self.assertEqual(0, second.returncode, second.stdout)
            self.assertEqual(first_content, second_content)
            self.assertIn("changed=0", second.stdout)


if __name__ == "__main__":
    unittest.main()
