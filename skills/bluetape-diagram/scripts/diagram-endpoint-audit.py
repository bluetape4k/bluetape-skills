#!/usr/bin/env python3
"""Audit bluetape4k SVG connector endpoints against card edges.

The audit is intentionally conservative:
- only SVG <rect> elements are treated as cards/layers;
- only path connectors are inspected;
- endpoints on a rect edge must stay away from adjacent corners by
  max(8px, rx / 2);
- top/bottom attachments must have a vertical terminal segment;
- left/right attachments must have a horizontal terminal segment.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

SVG_NS = "{http://www.w3.org/2000/svg}"
COMMAND_RE = re.compile(r"[MLHVQZmlhvqz]|-?\d+(?:\.\d+)?")
CONNECTOR_CLASSES = {
    "arrow",
    "call",
    "aws",
    "return",
    "retry",
    "slot",
    "state",
    "skip",
    "flow",
    "message",
    "connector",
    "edge",
}


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float
    rx: float
    label: str


@dataclass(frozen=True)
class PathEndpoint:
    point: tuple[float, float]
    direction: str


def attr_float(node: ET.Element, name: str, default: float = 0.0) -> float:
    value = node.attrib.get(name)
    if value is None or value == "":
        return default
    return float(value)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_rects(root: ET.Element) -> list[Rect]:
    rects: list[Rect] = []
    for i, node in enumerate(root.iter()):
        if local_name(node.tag) != "rect":
            continue
        width = attr_float(node, "width")
        height = attr_float(node, "height")
        if width <= 0 or height <= 0:
            continue
        rects.append(
            Rect(
                x=attr_float(node, "x"),
                y=attr_float(node, "y"),
                width=width,
                height=height,
                rx=attr_float(node, "rx"),
                label=node.attrib.get("id") or node.attrib.get("class") or f"rect#{i}",
            )
        )
    return rects


def connector_paths(root: ET.Element, include_all_paths: bool) -> list[ET.Element]:
    paths: list[ET.Element] = []
    for node in root.iter():
        if local_name(node.tag) != "path" or "d" not in node.attrib:
            continue
        if include_all_paths:
            paths.append(node)
            continue
        classes = set(node.attrib.get("class", "").split())
        marker = node.attrib.get("marker-end") or node.attrib.get("marker-start")
        if classes & CONNECTOR_CLASSES or marker:
            paths.append(node)
    return paths


def direction_between(a: tuple[float, float], b: tuple[float, float]) -> str:
    if math.isclose(a[0], b[0], abs_tol=0.001) and not math.isclose(a[1], b[1], abs_tol=0.001):
        return "V"
    if math.isclose(a[1], b[1], abs_tol=0.001) and not math.isclose(a[0], b[0], abs_tol=0.001):
        return "H"
    return "D"


def path_endpoints(d: str) -> tuple[PathEndpoint, PathEndpoint] | None:
    tokens = COMMAND_RE.findall(d)
    i = 0
    current: tuple[float, float] | None = None
    points: list[tuple[float, float]] = []
    while i < len(tokens):
        cmd = tokens[i]
        i += 1
        if cmd in {"M", "m"}:
            x = float(tokens[i])
            y = float(tokens[i + 1])
            i += 2
            current = (x, y)
            points.append(current)
        elif cmd in {"H", "h"} and current is not None:
            x = float(tokens[i])
            i += 1
            current = (x, current[1])
            points.append(current)
        elif cmd in {"V", "v"} and current is not None:
            y = float(tokens[i])
            i += 1
            current = (current[0], y)
            points.append(current)
        elif cmd in {"L", "l"} and current is not None:
            x = float(tokens[i])
            y = float(tokens[i + 1])
            i += 2
            current = (x, y)
            points.append(current)
        elif cmd in {"Q", "q"} and current is not None:
            # Endpoint tangent is approximated from the previous point to the curve
            # endpoint. This is sufficient for detecting card-side terminal tangent.
            _cx = float(tokens[i])
            _cy = float(tokens[i + 1])
            x = float(tokens[i + 2])
            y = float(tokens[i + 3])
            i += 4
            current = (x, y)
            points.append(current)
        elif cmd in {"Z", "z"}:
            continue
        else:
            raise ValueError(f"unsupported path token {cmd!r} in {d!r}")
    unique = [points[0]] if points else []
    for point in points[1:]:
        if point != unique[-1]:
            unique.append(point)
    if len(unique) < 2:
        return None
    start = PathEndpoint(unique[0], direction_between(unique[0], unique[1]))
    end = PathEndpoint(unique[-1], direction_between(unique[-2], unique[-1]))
    return start, end


def edge_for_point(rect: Rect, point: tuple[float, float], eps: float) -> str | None:
    x, y = point
    on_x = rect.x - eps <= x <= rect.x + rect.width + eps
    on_y = rect.y - eps <= y <= rect.y + rect.height + eps
    if math.isclose(y, rect.y, abs_tol=eps) and on_x:
        return "top"
    if math.isclose(y, rect.y + rect.height, abs_tol=eps) and on_x:
        return "bottom"
    if math.isclose(x, rect.x, abs_tol=eps) and on_y:
        return "left"
    if math.isclose(x, rect.x + rect.width, abs_tol=eps) and on_y:
        return "right"
    return None


def validate_endpoint(rect: Rect, endpoint: PathEndpoint, edge: str) -> list[str]:
    x, y = endpoint.point
    guard = max(8.0, rect.rx / 2.0)
    failures: list[str] = []
    if edge in {"top", "bottom"}:
        if x < rect.x + guard or x > rect.x + rect.width - guard:
            failures.append(f"{edge} endpoint within corner guard {guard:g}px")
        if endpoint.direction != "V":
            failures.append(f"{edge} endpoint terminal segment is {endpoint.direction}, expected V")
    else:
        if y < rect.y + guard or y > rect.y + rect.height - guard:
            failures.append(f"{edge} endpoint within corner guard {guard:g}px")
        if endpoint.direction != "H":
            failures.append(f"{edge} endpoint terminal segment is {endpoint.direction}, expected H")
    return failures


def audit_file(path: Path, include_all_paths: bool, eps: float) -> list[str]:
    root = ET.parse(path).getroot()
    rects = parse_rects(root)
    failures: list[str] = []
    for index, node in enumerate(connector_paths(root, include_all_paths), start=1):
        d = node.attrib["d"]
        try:
            endpoints = path_endpoints(d)
        except ValueError as exc:
            failures.append(f"{path}: path#{index}: {exc}")
            continue
        if endpoints is None:
            continue
        for side, endpoint in (("start", endpoints[0]), ("end", endpoints[1])):
            matches: list[tuple[Rect, str]] = []
            for rect in rects:
                edge = edge_for_point(rect, endpoint.point, eps)
                if edge is not None:
                    matches.append((rect, edge))
            if not matches:
                # Free-floating sequence/lifeline endpoints are allowed. This script
                # audits endpoints that do touch known rect boundaries.
                continue
            for rect, edge in matches:
                endpoint_failures = validate_endpoint(rect, endpoint, edge)
                for failure in endpoint_failures:
                    failures.append(
                        f"{path}: path#{index} {side} {endpoint.point} on {rect.label} {edge}: {failure}"
                    )
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", nargs="+", type=Path)
    parser.add_argument("--all-paths", action="store_true", help="audit every path, not only likely connectors")
    parser.add_argument("--eps", type=float, default=0.75)
    args = parser.parse_args()

    failures: list[str] = []
    for svg in args.svg:
        failures.extend(audit_file(svg, args.all_paths, args.eps))

    if failures:
        print("diagram endpoint audit: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"diagram endpoint audit: PASS files={len(args.svg)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
