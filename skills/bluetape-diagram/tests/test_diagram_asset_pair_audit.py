from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = next(
    path
    for path in (
        SKILL_ROOT / "scripts" / "diagram-asset-pair-audit.py",
        SKILL_ROOT / "scripts" / "executable_diagram-asset-pair-audit.py",
    )
    if path.exists()
)


class DiagramAssetPairAuditTest(unittest.TestCase):
    def run_audit(self, asset_dir: Path, readme: Path | None = None, *args: str) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(AUDIT), "--asset-dir", str(asset_dir)]
        if readme is not None:
            command.extend(["--readme", str(readme)])
        command.extend(args)
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def test_pair_and_png_readme_reference_pass(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "images"
            assets.mkdir()
            (assets / "architecture.svg").write_text("<svg/>", encoding="utf-8")
            (assets / "architecture.png").write_bytes(b"png")
            readme = root / "README.md"
            readme.write_text("![architecture](images/architecture.png)\n", encoding="utf-8")
            result = self.run_audit(assets, readme)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("pairs=1", result.stdout)

    def test_missing_pair_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            assets = Path(temp_dir) / "images"
            assets.mkdir()
            (assets / "architecture.svg").write_text("<svg/>", encoding="utf-8")
            result = self.run_audit(assets)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("missing PNG pair", result.stdout)

    def test_svg_embed_missing_ref_and_mermaid_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "images"
            assets.mkdir()
            (assets / "architecture.svg").write_text("<svg/>", encoding="utf-8")
            (assets / "architecture.png").write_bytes(b"png")
            readme = root / "README.md"
            readme.write_text(
                "![bad](images/missing.png)\n![svg](images/architecture.svg)\n```mermaid\ngraph TD\n```\n```dot\ndigraph G {}\n```\n",
                encoding="utf-8",
            )
            result = self.run_audit(assets, readme)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("missing README image", result.stdout)
            self.assertIn("README embeds SVG", result.stdout)
            self.assertIn("Mermaid residue", result.stdout)
            self.assertIn("Graphviz residue", result.stdout)

    def test_require_all_referenced_rejects_unexposed_pair(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            assets = root / "images"
            assets.mkdir()
            for stem in ("architecture", "sequence"):
                (assets / f"{stem}.svg").write_text("<svg/>", encoding="utf-8")
                (assets / f"{stem}.png").write_bytes(b"png")
            readme = root / "README.md"
            readme.write_text("![architecture](images/architecture.png)\n", encoding="utf-8")
            result = self.run_audit(assets, readme, "--require-all-referenced")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("PNG is not exposed", result.stdout)


if __name__ == "__main__":
    unittest.main()
