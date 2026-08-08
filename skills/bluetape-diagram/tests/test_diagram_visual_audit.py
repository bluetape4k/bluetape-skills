from __future__ import annotations

import struct
import subprocess
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = next(
    path
    for path in (
        SKILL_ROOT / "scripts" / "diagram-visual-audit.py",
        SKILL_ROOT / "scripts" / "executable_diagram-visual-audit.py",
    )
    if path.exists()
)


def chunk(name: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + name + payload + struct.pack(">I", zlib.crc32(name + payload) & 0xFFFFFFFF)


def write_png(path: Path, width: int, height: int, fill=(255, 255, 255, 255), content=None) -> None:
    pixels = [[fill for _ in range(width)] for _ in range(height)]
    if content:
        x0, y0, x1, y1, color = content
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                pixels[y][x] = color
    raw = b"".join(b"\x00" + b"".join(bytes(pixel) for pixel in row) for row in pixels)
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))


class DiagramVisualAuditTest(unittest.TestCase):
    def run_audit(self, png: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(AUDIT), *args, str(png)],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_balanced_opaque_png_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "balanced.png"
            write_png(path, 100, 100, content=(20, 20, 80, 80, (30, 80, 160, 255)))
            result = self.run_audit(path, "--require-opaque")
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("bbox_occupancy=0.372", result.stdout)

    def test_stale_tall_canvas_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "stale.png"
            write_png(path, 100, 400, content=(20, 20, 80, 100, (30, 80, 160, 255)))
            result = self.run_audit(path)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("bbox occupancy", result.stdout)

    def test_aspect_threshold_is_explicit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "wide.png"
            write_png(path, 500, 100, content=(20, 20, 480, 80, (30, 80, 160, 255)))
            result = self.run_audit(path, "--max-aspect", "3")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("aspect", result.stdout)

    def test_transparent_png_requires_explicit_opaque_gate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "transparent.png"
            write_png(path, 100, 100, fill=(255, 255, 255, 0), content=(20, 20, 80, 80, (30, 80, 160, 200)))
            result = self.run_audit(path, "--require-opaque")
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("opaque PNG required", result.stdout)

    def test_blank_png_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "blank.png"
            write_png(path, 40, 40)
            result = self.run_audit(path)
            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertIn("blank/background-only", result.stdout)


if __name__ == "__main__":
    unittest.main()
