#!/usr/bin/env python3
"""Audit PNG canvas geometry before a diagram is exposed in a README.

The check is intentionally dependency-free.  It catches the recurring case
where a rendered diagram occupies only a small part of a stale viewBox/canvas,
or where a transparent/blank export looks valid to an XML-only check.
"""

from __future__ import annotations

import argparse
import binascii
import json
import struct
import sys
import zlib
from dataclasses import dataclass
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
COLOR_CHANNELS = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}


class PNGError(ValueError):
    pass


@dataclass(frozen=True)
class PNGImage:
    width: int
    height: int
    pixels: list[tuple[int, int, int, int]]


def paeth(left: int, up: int, upper_left: int) -> int:
    estimate = left + up - upper_left
    distance_left = abs(estimate - left)
    distance_up = abs(estimate - up)
    distance_upper_left = abs(estimate - upper_left)
    if distance_left <= distance_up and distance_left <= distance_upper_left:
        return left
    if distance_up <= distance_upper_left:
        return up
    return upper_left


def unfilter(raw: bytes, width: int, height: int, bytes_per_pixel: int) -> list[bytes]:
    row_bytes = width * bytes_per_pixel
    expected = height * (row_bytes + 1)
    if len(raw) != expected:
        raise PNGError(f"decompressed scanline length is {len(raw)}, expected {expected}")
    rows: list[bytes] = []
    offset = 0
    previous = bytearray(row_bytes)
    for _ in range(height):
        filter_type = raw[offset]
        offset += 1
        encoded = raw[offset : offset + row_bytes]
        offset += row_bytes
        row = bytearray(row_bytes)
        for index, value in enumerate(encoded):
            left = row[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            up = previous[index]
            upper_left = previous[index - bytes_per_pixel] if index >= bytes_per_pixel else 0
            if filter_type == 0:
                decoded = value
            elif filter_type == 1:
                decoded = value + left
            elif filter_type == 2:
                decoded = value + up
            elif filter_type == 3:
                decoded = value + ((left + up) // 2)
            elif filter_type == 4:
                decoded = value + paeth(left, up, upper_left)
            else:
                raise PNGError(f"unsupported PNG filter type {filter_type}")
            row[index] = decoded & 0xFF
        rows.append(bytes(row))
        previous = row
    return rows


def decode_png(path: Path) -> PNGImage:
    data = path.read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise PNGError("missing PNG signature")
    offset = len(PNG_SIGNATURE)
    ihdr: tuple[int, int, int, int, int, int, int] | None = None
    idat = bytearray()
    palette: list[tuple[int, int, int]] = []
    transparency: list[int] = []
    while offset + 12 <= len(data):
        length = struct.unpack(">I", data[offset : offset + 4])[0]
        chunk_start = offset + 8
        chunk_end = chunk_start + length
        if chunk_end + 4 > len(data):
            raise PNGError("truncated PNG chunk")
        chunk_type = data[offset + 4 : offset + 8]
        chunk = data[chunk_start:chunk_end]
        crc = struct.unpack(">I", data[chunk_end : chunk_end + 4])[0]
        if binascii.crc32(chunk_type + chunk) & 0xFFFFFFFF != crc:
            raise PNGError(f"invalid CRC for {chunk_type.decode('ascii', 'replace')}")
        offset = chunk_end + 4
        if chunk_type == b"IHDR":
            if len(chunk) != 13:
                raise PNGError("invalid IHDR")
            ihdr = struct.unpack(">IIBBBBB", chunk)
        elif chunk_type == b"PLTE":
            if len(chunk) % 3:
                raise PNGError("invalid PLTE")
            palette = [tuple(chunk[index : index + 3]) for index in range(0, len(chunk), 3)]  # type: ignore[list-item]
        elif chunk_type == b"tRNS":
            transparency = list(chunk)
        elif chunk_type == b"IDAT":
            idat.extend(chunk)
        elif chunk_type == b"IEND":
            break
    if ihdr is None:
        raise PNGError("missing IHDR")
    width, height, bit_depth, color_type, compression, filter_method, interlace = ihdr
    if width <= 0 or height <= 0:
        raise PNGError("PNG dimensions must be positive")
    if bit_depth != 8 or compression != 0 or filter_method != 0 or interlace != 0:
        raise PNGError("only non-interlaced 8-bit PNGs are supported")
    channels = COLOR_CHANNELS.get(color_type)
    if channels is None:
        raise PNGError(f"unsupported PNG color type {color_type}")
    if color_type == 3 and not palette:
        raise PNGError("indexed PNG is missing PLTE")
    rows = unfilter(zlib.decompress(bytes(idat)), width, height, channels)
    pixels: list[tuple[int, int, int, int]] = []
    for row in rows:
        for index in range(width):
            values = row[index * channels : (index + 1) * channels]
            if color_type == 0:
                gray = values[0]
                pixel = (gray, gray, gray, 255)
            elif color_type == 2:
                pixel = (values[0], values[1], values[2], 255)
            elif color_type == 3:
                palette_index = values[0]
                if palette_index >= len(palette):
                    raise PNGError("indexed PNG references a missing palette entry")
                red, green, blue = palette[palette_index]
                pixel = (red, green, blue, transparency[palette_index] if palette_index < len(transparency) else 255)
            elif color_type == 4:
                gray, alpha = values
                pixel = (gray, gray, gray, alpha)
            else:
                pixel = (values[0], values[1], values[2], values[3])
            pixels.append(pixel)
    return PNGImage(width, height, pixels)


def analyze(image: PNGImage, background_delta: int) -> dict[str, object]:
    corner = image.pixels[0]
    transparent_background = corner[3] <= 8
    bbox: list[int] | None = None
    ink_pixels = 0
    alpha_min = 255
    transparent_pixels = 0
    for index, pixel in enumerate(image.pixels):
        red, green, blue, alpha = pixel
        alpha_min = min(alpha_min, alpha)
        if alpha < 255:
            transparent_pixels += 1
        if transparent_background:
            content = alpha > 8
        else:
            content = max(abs(red - corner[0]), abs(green - corner[1]), abs(blue - corner[2])) > background_delta
            content = content and alpha > 8
        if not content:
            continue
        ink_pixels += 1
        x = index % image.width
        y = index // image.width
        if bbox is None:
            bbox = [x, x, y, y]
        else:
            bbox[0] = min(bbox[0], x)
            bbox[1] = max(bbox[1], x)
            bbox[2] = min(bbox[2], y)
            bbox[3] = max(bbox[3], y)
    total = image.width * image.height
    if bbox is None:
        margins = [image.width, image.width, image.height, image.height]
        bbox_occupancy = 0.0
    else:
        margins = [bbox[0], image.width - 1 - bbox[1], bbox[2], image.height - 1 - bbox[3]]
        bbox_occupancy = ((bbox[1] - bbox[0] + 1) * (bbox[3] - bbox[2] + 1)) / total
    return {
        "width": image.width,
        "height": image.height,
        "aspect": max(image.width / image.height, image.height / image.width),
        "bbox": bbox,
        "bbox_occupancy": bbox_occupancy,
        "ink_occupancy": ink_pixels / total,
        "ink_pixels": ink_pixels,
        "margins": margins,
        "margin_imbalance": (max(margins) - min(margins)) / max(1, min(image.width, image.height)),
        "alpha_min": alpha_min,
        "transparent_pixels": transparent_pixels,
        "transparent_background": transparent_background,
    }


def audit(path: Path, max_aspect: float, min_bbox_occupancy: float, max_margin_imbalance: float, background_delta: int, require_opaque: bool) -> dict[str, object]:
    image = decode_png(path)
    report = analyze(image, background_delta)
    failures: list[str] = []
    if report["ink_pixels"] == 0:
        failures.append("blank/background-only export")
    if report["aspect"] > max_aspect:
        failures.append(f"aspect {report['aspect']:.2f} > {max_aspect:.2f}")
    if report["bbox_occupancy"] < min_bbox_occupancy:
        failures.append(f"bbox occupancy {report['bbox_occupancy']:.3f} < {min_bbox_occupancy:.3f}")
    if report["margin_imbalance"] > max_margin_imbalance:
        failures.append(f"margin imbalance {report['margin_imbalance']:.3f} > {max_margin_imbalance:.3f}")
    if require_opaque and report["alpha_min"] < 255:
        failures.append(f"alpha_min {report['alpha_min']} < 255 (opaque PNG required)")
    report["path"] = str(path)
    report["failures"] = failures
    report["ok"] = not failures
    return report


def format_report(report: dict[str, object]) -> str:
    margins = ",".join(str(item) for item in report["margins"])
    status = "PASS" if report["ok"] else "FAIL"
    details = (
        f"{report['path']}: {status} width={report['width']} height={report['height']} "
        f"aspect={report['aspect']:.2f} bbox_occupancy={report['bbox_occupancy']:.3f} "
        f"ink_occupancy={report['ink_occupancy']:.3f} margins=L{margins.split(',')[0]}/R{margins.split(',')[1]}/"
        f"T{margins.split(',')[2]}/B{margins.split(',')[3]} margin_imbalance={report['margin_imbalance']:.3f} "
        f"alpha_min={report['alpha_min']} transparent_pixels={report['transparent_pixels']}"
    )
    if report["failures"]:
        details += " failures=" + "; ".join(str(item) for item in report["failures"])
    return details


def expand_paths(paths: list[Path]) -> list[Path]:
    expanded: list[Path] = []
    for path in paths:
        if path.is_dir():
            expanded.extend(sorted(path.rglob("*.png")))
        else:
            expanded.append(path)
    return expanded


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit rendered diagram PNG canvas geometry and content occupancy.")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--max-aspect", type=float, default=4.0)
    parser.add_argument("--min-bbox-occupancy", type=float, default=0.22)
    parser.add_argument("--max-margin-imbalance", type=float, default=0.35)
    parser.add_argument("--background-delta", type=int, default=12)
    parser.add_argument("--require-opaque", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    reports: list[dict[str, object]] = []
    for path in expand_paths(args.paths):
        try:
            reports.append(
                audit(path, args.max_aspect, args.min_bbox_occupancy, args.max_margin_imbalance, args.background_delta, args.require_opaque)
            )
        except (OSError, PNGError, ValueError, zlib.error) as exc:
            reports.append({"path": str(path), "ok": False, "failures": [f"schema: {exc}"]})
    if args.as_json:
        print(json.dumps(reports, ensure_ascii=False, sort_keys=True))
    else:
        for report in reports:
            print(format_report(report) if "width" in report else f"{report['path']}: FAIL " + "; ".join(report["failures"]))
    return 0 if reports and all(report["ok"] for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
