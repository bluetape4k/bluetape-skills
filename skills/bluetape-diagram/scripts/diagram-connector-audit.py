#!/usr/bin/env python3
"""Audit bluetape4k SVG connector markers, card intrusions, and crossings.

This is a screening tool for bluetape4k README diagrams. It intentionally does
not replace rendered-PNG inspection: visual near-crossings, title collisions,
and confusing detours still fail even when this script reports PASS.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

NS = {"svg": "http://www.w3.org/2000/svg"}
PATH_TOKEN_RE = re.compile(
    r"[MLHVQCZmlhvqcz]|[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?"
)
SKIP_CONTAINER_TAGS = {"defs", "marker", "clipPath", "mask", "pattern", "symbol"}
CONNECTOR_CLASSES = {
    "arrow",
    "call",
    "connector",
    "edge",
    "event",
    "flow",
    "message",
    "path",
    "return",
    "route",
    "skip",
    "slot",
    "state",
}


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class Segment:
    name: str
    a: tuple[float, float]
    b: tuple[float, float]


def parse_style(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    entries = {}
    for part in style.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        entries[key.strip()] = value.strip()
    return entries


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def classes(node: ET.Element) -> set[str]:
    return set(node.attrib.get("class", "").split())


def iter_rendered(root: ET.Element, tag: str | None = None):
    """Yield rendered nodes, skipping marker/defs internals."""
    for child in list(root):
        child_tag = local_name(child.tag)
        if child_tag in SKIP_CONTAINER_TAGS:
            continue
        if tag is None or child_tag == tag:
            yield child
        yield from iter_rendered(child, tag)


def is_no_dash(value: str | None) -> bool:
    if value is None:
        return True
    return value.replace("!important", "").strip() == "none"


def is_number(token: str) -> bool:
    try:
        float(token)
        return True
    except ValueError:
        return False


def has_numbers(tokens: list[str], index: int, count: int) -> bool:
    return index + count <= len(tokens) and all(
        is_number(token) for token in tokens[index : index + count]
    )


def parse_points(d: str) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    tokens = PATH_TOKEN_RE.findall(d.replace(",", " "))
    index = 0
    command: str | None = None
    current = (0.0, 0.0)
    while index < len(tokens):
        token = tokens[index]
        if not is_number(token):
            command = token
            index += 1
            if command in {"Z", "z"}:
                continue
        if command is None:
            raise ValueError("path data starts without a command")

        relative = command.islower()
        op = command.upper()
        if op == "M":
            if not has_numbers(tokens, index, 2):
                raise ValueError("M command lacks coordinate pair")
            x, y = float(tokens[index]), float(tokens[index + 1])
            index += 2
            if relative:
                x += current[0]
                y += current[1]
            current = (x, y)
            points.append(current)
            command = "l" if relative else "L"
            continue
        if op == "L":
            if not has_numbers(tokens, index, 2):
                raise ValueError("L command lacks coordinate pair")
            x, y = float(tokens[index]), float(tokens[index + 1])
            index += 2
            if relative:
                x += current[0]
                y += current[1]
            current = (x, y)
            points.append(current)
            continue
        if op == "H":
            if not has_numbers(tokens, index, 1):
                raise ValueError("H command lacks coordinate")
            x = float(tokens[index])
            index += 1
            if relative:
                x += current[0]
            current = (x, current[1])
            points.append(current)
            continue
        if op == "V":
            if not has_numbers(tokens, index, 1):
                raise ValueError("V command lacks coordinate")
            y = float(tokens[index])
            index += 1
            if relative:
                y += current[1]
            current = (current[0], y)
            points.append(current)
            continue
        if op == "Q":
            if not has_numbers(tokens, index, 4):
                raise ValueError("Q command lacks control/end coordinates")
            control = (float(tokens[index]), float(tokens[index + 1]))
            end = (float(tokens[index + 2]), float(tokens[index + 3]))
            index += 4
            if relative:
                control = (control[0] + current[0], control[1] + current[1])
                end = (end[0] + current[0], end[1] + current[1])
            for i in range(1, 9):
                t = i / 8.0
                x = (
                    (1 - t) * (1 - t) * current[0]
                    + 2 * (1 - t) * t * control[0]
                    + t * t * end[0]
                )
                y = (
                    (1 - t) * (1 - t) * current[1]
                    + 2 * (1 - t) * t * control[1]
                    + t * t * end[1]
                )
                points.append((x, y))
            current = end
            continue
        if op == "C":
            if not has_numbers(tokens, index, 6):
                raise ValueError("C command lacks control/end coordinates")
            c1 = (float(tokens[index]), float(tokens[index + 1]))
            c2 = (float(tokens[index + 2]), float(tokens[index + 3]))
            end = (float(tokens[index + 4]), float(tokens[index + 5]))
            index += 6
            if relative:
                c1 = (c1[0] + current[0], c1[1] + current[1])
                c2 = (c2[0] + current[0], c2[1] + current[1])
                end = (end[0] + current[0], end[1] + current[1])
            for i in range(1, 9):
                t = i / 8.0
                x = (
                    (1 - t) ** 3 * current[0]
                    + 3 * (1 - t) ** 2 * t * c1[0]
                    + 3 * (1 - t) * t**2 * c2[0]
                    + t**3 * end[0]
                )
                y = (
                    (1 - t) ** 3 * current[1]
                    + 3 * (1 - t) ** 2 * t * c1[1]
                    + 3 * (1 - t) * t**2 * c2[1]
                    + t**3 * end[1]
                )
                points.append((x, y))
            current = end
            continue
        raise ValueError(f"unsupported path command {command}")
    return points


def rect_from_element(el: ET.Element) -> Rect | None:
    try:
        return Rect(
            float(el.attrib["x"]),
            float(el.attrib["y"]),
            float(el.attrib["width"]),
            float(el.attrib["height"]),
        )
    except KeyError:
        return None


def is_card_rect(el: ET.Element) -> bool:
    cls = " ".join(classes(el)).lower()
    ident = el.attrib.get("id", "").lower()
    return "card" in cls or re.search(r"(^|[-_])card($|[-_])", ident) is not None


def is_connector_path(el: ET.Element) -> bool:
    if el.attrib.get("data-connector"):
        return True
    if any(el.attrib.get(name) for name in ("marker-start", "marker-mid", "marker-end")):
        return True
    lower_classes = {name.lower() for name in classes(el)}
    if lower_classes & CONNECTOR_CLASSES:
        return True
    ident = el.attrib.get("id", "").lower()
    return re.search(r"(^|[-_])(connector|edge|flow|message|route|arrow)($|[-_])", ident) is not None


def connector_name(el: ET.Element, index: int) -> str:
    return (
        el.attrib.get("data-connector")
        or el.attrib.get("id")
        or el.attrib.get("class")
        or f"path#{index}"
    )


def point_inside_rect(point: tuple[float, float], rect: Rect, pad: float) -> bool:
    x, y = point
    return (
        rect.x + pad < x < rect.x + rect.width - pad
        and rect.y + pad < y < rect.y + rect.height - pad
    )


def segment_intrudes_rect(
    segment: Segment,
    rect: Rect,
    pad: float,
    sample_step: float,
) -> bool:
    ax, ay = segment.a
    bx, by = segment.b
    length = max(abs(ax - bx), abs(ay - by))
    steps = max(8, int(length / sample_step))
    for i in range(1, steps):
        t = i / steps
        point = (ax + (bx - ax) * t, ay + (by - ay) * t)
        if point_inside_rect(point, rect, pad):
            return True
    return False


def orientation(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def on_segment(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> bool:
    return (
        min(a[0], b[0]) - 1e-6 <= c[0] <= max(a[0], b[0]) + 1e-6
        and min(a[1], b[1]) - 1e-6 <= c[1] <= max(a[1], b[1]) + 1e-6
    )


def shared_endpoint(seg1: Segment, seg2: Segment, tolerance: float) -> bool:
    for p in (seg1.a, seg1.b):
        for q in (seg2.a, seg2.b):
            if math.hypot(p[0] - q[0], p[1] - q[1]) <= tolerance:
                return True
    return False


def proper_intersection(seg1: Segment, seg2: Segment) -> bool:
    if shared_endpoint(seg1, seg2, 1.0):
        return False
    a, b, c, d = seg1.a, seg1.b, seg2.a, seg2.b
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    if abs(o1) < 1e-6 and on_segment(a, b, c):
        return False
    if abs(o2) < 1e-6 and on_segment(a, b, d):
        return False
    if abs(o3) < 1e-6 and on_segment(c, d, a):
        return False
    if abs(o4) < 1e-6 and on_segment(c, d, b):
        return False
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def audit_markers(root: ET.Element) -> list[str]:
    failures: list[str] = []
    for marker in root.findall(".//svg:marker", NS):
        mid = marker.attrib.get("id", "<missing>")
        if marker.attrib.get("markerUnits") != "userSpaceOnUse":
            failures.append(f"{mid}: markerUnits is not userSpaceOnUse")
        for child in list(marker):
            fill = child.attrib.get("fill")
            stroke = child.attrib.get("stroke")
            if fill in {"context-stroke", "context-fill"}:
                failures.append(f"{mid}: marker fill uses {fill}")
            if stroke in {"context-stroke", "context-fill"}:
                failures.append(f"{mid}: marker stroke uses {stroke}")
            dash = child.attrib.get("stroke-dasharray")
            style_dash = parse_style(child.attrib.get("style")).get("stroke-dasharray")
            if not is_no_dash(dash):
                failures.append(f"{mid}: marker child dasharray is {dash}")
            if not is_no_dash(style_dash):
                failures.append(f"{mid}: marker child style dasharray is {style_dash}")
    return failures


def audit_file(path: Path, args: argparse.Namespace) -> bool:
    root = ET.parse(path).getroot()
    rects: list[Rect] = []
    for rect_el in iter_rendered(root, "rect"):
        if not is_card_rect(rect_el):
            continue
        rect = rect_from_element(rect_el)
        if rect is not None:
            rects.append(rect)

    connector_paths = [el for el in iter_rendered(root, "path") if is_connector_path(el)]
    segments: list[Segment] = []
    for path_index, path_el in enumerate(connector_paths, start=1):
        name = connector_name(path_el, path_index)
        try:
            points = parse_points(path_el.attrib.get("d", ""))
        except ValueError as exc:
            print(f"{path.name}: FAIL {name}: {exc}")
            return False
        for a, b in zip(points, points[1:]):
            segments.append(Segment(name, a, b))

    marker_failures = audit_markers(root)
    intrusions: set[str] = set()
    for segment in segments:
        for rect in rects:
            if segment_intrudes_rect(segment, rect, args.card_padding, args.sample_step):
                intrusions.add(segment.name)
                break

    crossings: set[tuple[str, str]] = set()
    for idx, left in enumerate(segments):
        for right in segments[idx + 1 :]:
            if left.name == right.name:
                continue
            if proper_intersection(left, right):
                crossings.add(tuple(sorted((left.name, right.name))))

    schema_failures: list[str] = []
    connector_like_markers = len(root.findall(".//svg:marker", NS))
    if connector_like_markers and not connector_paths:
        schema_failures.append(
            "marker definitions exist but no rendered connector paths were detected"
        )
    if connector_paths and not any(segments):
        schema_failures.append("connector paths were detected but no path segments parsed")

    failed = bool(marker_failures or schema_failures or intrusions or crossings)
    status = "FAIL" if failed else "PASS"
    print(
        f"{path.name}: {status} markers={len(root.findall('.//svg:marker', NS))} "
        f"connectors={len(connector_paths)} cards={len(rects)} "
        f"intrusions={len(intrusions)} crossings={len(crossings)}"
    )
    if marker_failures:
        for failure in marker_failures:
            print(f"  marker: {failure}")
    if schema_failures:
        for failure in schema_failures:
            print(f"  schema: {failure}")
    if intrusions:
        print("  intrusions: " + ", ".join(sorted(intrusions)))
    if crossings:
        for left, right in sorted(crossings):
            print(f"  crossing: {left} <-> {right}")
    return not failed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit SVG connector markers, card intrusions, and crossings."
    )
    parser.add_argument("svg", nargs="+", type=Path)
    parser.add_argument("--card-padding", type=float, default=1.5)
    parser.add_argument("--sample-step", type=float, default=8.0)
    args = parser.parse_args()

    ok = True
    for svg in args.svg:
        ok = audit_file(svg, args) and ok
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
