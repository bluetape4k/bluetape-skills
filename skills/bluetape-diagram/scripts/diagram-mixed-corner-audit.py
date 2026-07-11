#!/usr/bin/env python3
"""Audit bluetape4k connectors that mix rounded Q bends with hard turns."""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


NUMBER = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
TOKEN_RE = re.compile(r"[A-Za-z]|" + NUMBER)
CONNECTOR_HINT_RE = re.compile(
    r"(arrow|edge|call|return|seq|work|async|fail|skip|flow|connector|dependency|link|route)",
    re.IGNORECASE,
)
NON_RENDER_CONTAINER_TAGS = {"defs", "marker", "symbol", "clipPath", "mask", "pattern", "filter"}


@dataclass(frozen=True)
class Segment:
    op: str
    start: tuple[float, float]
    end: tuple[float, float]
    entry_dir: str
    exit_dir: str
    length: float


def parse_path(d: str) -> list[Segment]:
    tokens = TOKEN_RE.findall(d)
    segments: list[Segment] = []
    i = 0
    cmd: str | None = None
    cur = (0.0, 0.0)
    start_point = (0.0, 0.0)

    while i < len(tokens):
        if re.fullmatch(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
        if cmd is None:
            i += 1
            continue

        upper = cmd.upper()
        rel = cmd.islower()
        if upper in {"M", "L"}:
            if i + 1 >= len(tokens) or any(re.fullmatch(r"[A-Za-z]", token) for token in tokens[i : i + 2]):
                cmd = None
                continue
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            if rel:
                x += cur[0]
                y += cur[1]
            end = (x, y)
            if upper == "M":
                cur = end
                start_point = end
                cmd = "l" if rel else "L"
                continue
            direction, length = segment_direction(cur, end)
            segments.append(Segment("L", cur, end, direction, direction, length))
            cur = end
        elif upper == "H":
            if i >= len(tokens) or re.fullmatch(r"[A-Za-z]", tokens[i]):
                cmd = None
                continue
            x = float(tokens[i])
            i += 1
            if rel:
                x += cur[0]
            end = (x, cur[1])
            direction, length = segment_direction(cur, end)
            segments.append(Segment("L", cur, end, direction, direction, length))
            cur = end
        elif upper == "V":
            if i >= len(tokens) or re.fullmatch(r"[A-Za-z]", tokens[i]):
                cmd = None
                continue
            y = float(tokens[i])
            i += 1
            if rel:
                y += cur[1]
            end = (cur[0], y)
            direction, length = segment_direction(cur, end)
            segments.append(Segment("L", cur, end, direction, direction, length))
            cur = end
        elif upper == "Q":
            if i + 3 >= len(tokens) or any(re.fullmatch(r"[A-Za-z]", token) for token in tokens[i : i + 4]):
                cmd = None
                continue
            cx, cy, x, y = (float(tokens[i]), float(tokens[i + 1]), float(tokens[i + 2]), float(tokens[i + 3]))
            i += 4
            if rel:
                cx += cur[0]
                cy += cur[1]
                x += cur[0]
                y += cur[1]
            control = (cx, cy)
            end = (x, y)
            entry_dir, _ = segment_direction(cur, control)
            exit_dir, length = segment_direction(control, end)
            segments.append(Segment("Q", cur, end, entry_dir, exit_dir, length))
            cur = end
        elif upper == "Z":
            direction, length = segment_direction(cur, start_point)
            if length > 0:
                segments.append(Segment("L", cur, start_point, direction, direction, length))
            cur = start_point
            cmd = None
        else:
            cmd = None
            while i < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[i]):
                i += 1

    return segments


def segment_direction(a: tuple[float, float], b: tuple[float, float]) -> tuple[str, float]:
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    if abs(dx) < 1e-6 and abs(dy) > 1e-6:
        return "V", abs(dy)
    if abs(dy) < 1e-6 and abs(dx) > 1e-6:
        return "H", abs(dx)
    if abs(dx) < 1e-6 and abs(dy) < 1e-6:
        return "Z", 0.0
    return "D", math.hypot(dx, dy)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def is_connector_path(node: ET.Element) -> bool:
    if node.get("marker-end") or node.get("marker-start") or node.get("marker-mid"):
        return True
    hint = " ".join(filter(None, [node.get("class"), node.get("id"), node.get("data-edge"), node.get("data-connector")]))
    if CONNECTOR_HINT_RE.search(hint):
        return True
    style = node.get("style", "").replace(" ", "")
    return (node.get("fill") == "none" or "fill:none" in style) and bool(node.get("stroke") or "stroke:" in style)


def iter_paths(node: ET.Element, inside_non_render: bool = False):
    tag = local_name(node.tag)
    now_inside_non_render = inside_non_render or tag in NON_RENDER_CONTAINER_TAGS
    if tag == "path" and not now_inside_non_render and is_connector_path(node):
        yield node
    for child in node:
        yield from iter_paths(child, now_inside_non_render)


def sharp_turn(previous: Segment, current: Segment) -> bool:
    if previous.exit_dir not in {"H", "V"} or current.entry_dir not in {"H", "V"}:
        return False
    return previous.exit_dir != current.entry_dir


def audit_segments(path_name: str, path_index: int, d: str, segments: list[Segment]) -> tuple[int, int, list[str]]:
    q_bends = sum(1 for segment in segments if segment.op == "Q")
    failures: list[str] = []
    if q_bends == 0:
        return 0, 0, failures

    for index, current in enumerate(segments):
        if index == 0:
            continue
        previous = segments[index - 1]
        if not sharp_turn(previous, current):
            continue
        reason = None
        if previous.op == "Q" or current.op == "Q":
            reason = "hard turn adjacent to Q bend"
        elif any(segment.op == "Q" for segment in segments):
            reason = "unrounded L/H/V turn in a path that also uses Q bends"
        if reason is None:
            continue
        failures.append(
            f"{path_name}: path#{path_index}: {reason} "
            f"{previous.exit_dir}->{current.entry_dir} at ({current.start[0]:.1f},{current.start[1]:.1f}) d={d[:180]}"
        )

    return len(failures), q_bends, failures


def audit_file(path: Path) -> tuple[int, int, int, list[str]]:
    root = ET.parse(path).getroot()
    path_count = 0
    q_bends = 0
    failure_count = 0
    failures: list[str] = []

    for index, node in enumerate(iter_paths(root), 1):
        d = node.get("d", "")
        if not d:
            continue
        path_count += 1
        segments = parse_path(d)
        path_failures, path_q_bends, lines = audit_segments(path.name, index, d, segments)
        q_bends += path_q_bends
        failure_count += path_failures
        failures.extend(lines)

    return path_count, q_bends, failure_count, failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit connector paths that mix rounded Q bends with hard L/H/V turns.")
    parser.add_argument("svg", nargs="+", type=Path)
    args = parser.parse_args()

    total_files = 0
    total_paths = 0
    total_q_bends = 0
    total_failures = 0
    all_failures: list[str] = []

    for svg in args.svg:
        total_files += 1
        path_count, q_bends, failures, lines = audit_file(svg)
        total_paths += path_count
        total_q_bends += q_bends
        total_failures += failures
        all_failures.extend(lines)

    for line in all_failures:
        print(line)

    if total_failures:
        print(
            f"diagram mixed-corner audit: FAIL files={total_files} paths={total_paths} "
            f"q_bends={total_q_bends} failures={total_failures}"
        )
        return 1

    print(
        f"diagram mixed-corner audit: PASS files={total_files} paths={total_paths} "
        f"q_bends={total_q_bends} failures=0"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
