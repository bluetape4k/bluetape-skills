#!/usr/bin/env python3
"""Audit SVG connector geometry for bluetape4k diagrams.

This helper is intentionally conservative. It flags geometry that must be
reviewed visually: sharp orthogonal L turns, rounded Q turns whose legs are too
short to render as curves, and optional diagonal connector segments. It skips
marker definitions so arrowhead polygons do not dominate the report.
"""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


NUMBER = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
TOKEN_RE = re.compile(r"[A-Za-z]|" + NUMBER)


def parse_path(d: str) -> list[tuple[str, tuple[float, ...]]]:
    tokens = TOKEN_RE.findall(d)
    ops: list[tuple[str, tuple[float, ...]]] = []
    i = 0
    cmd: str | None = None
    cur = (0.0, 0.0)

    while i < len(tokens):
        if re.fullmatch(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
        if cmd is None:
            i += 1
            break

        upper = cmd.upper()
        rel = cmd.islower()
        if upper in {"M", "L"}:
            if i + 1 >= len(tokens):
                break
            if re.fullmatch(r"[A-Za-z]", tokens[i]) or re.fullmatch(r"[A-Za-z]", tokens[i + 1]):
                cmd = None
                continue
            x, y = float(tokens[i]), float(tokens[i + 1])
            i += 2
            if rel:
                x += cur[0]
                y += cur[1]
            ops.append((upper, (x, y)))
            cur = (x, y)
            if upper == "M":
                cmd = "l" if rel else "L"
        elif upper == "H":
            if i >= len(tokens):
                break
            if re.fullmatch(r"[A-Za-z]", tokens[i]):
                cmd = None
                continue
            x = float(tokens[i])
            i += 1
            if rel:
                x += cur[0]
            cur = (x, cur[1])
            ops.append(("L", cur))
        elif upper == "V":
            if i >= len(tokens):
                break
            if re.fullmatch(r"[A-Za-z]", tokens[i]):
                cmd = None
                continue
            y = float(tokens[i])
            i += 1
            if rel:
                y += cur[1]
            cur = (cur[0], y)
            ops.append(("L", cur))
        elif upper == "Q":
            if i + 3 >= len(tokens):
                break
            if any(re.fullmatch(r"[A-Za-z]", token) for token in tokens[i : i + 4]):
                cmd = None
                continue
            x1, y1, x, y = (float(tokens[i]), float(tokens[i + 1]), float(tokens[i + 2]), float(tokens[i + 3]))
            i += 4
            if rel:
                x1 += cur[0]
                y1 += cur[1]
                x += cur[0]
                y += cur[1]
            ops.append((upper, (x1, y1, x, y)))
            cur = (x, y)
        elif upper == "Z":
            ops.append((upper, ()))
            cmd = None
        else:
            cmd = None
            while i < len(tokens) and not re.fullmatch(r"[A-Za-z]", tokens[i]):
                i += 1

    return ops


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


CONNECTOR_HINT_RE = re.compile(
    r"(arrow|edge|call|return|seq|work|async|fail|skip|flow|connector|dependency|link|route)",
    re.IGNORECASE,
)
NON_RENDER_CONTAINER_TAGS = {"defs", "marker", "symbol", "clipPath", "mask", "pattern", "filter"}


def is_connector_path(node: ET.Element) -> bool:
    d = node.get("d", "")
    if node.get("marker-end") or node.get("marker-start") or node.get("marker-mid"):
        return True
    hint = " ".join(filter(None, [node.get("class"), node.get("id"), node.get("data-edge"), node.get("data-connector")]))
    if CONNECTOR_HINT_RE.search(hint):
        return True
    style = node.get("style", "")
    if (node.get("fill") == "none" or "fill:none" in style.replace(" ", "")) and (node.get("stroke") or "stroke:" in style):
        nums = [float(value) for value in re.findall(NUMBER, d)]
        xs = nums[0::2]
        ys = nums[1::2]
        if xs and ys:
            width = max(xs) - min(xs)
            height = max(ys) - min(ys)
            if "Z" in d.upper() or (width < 120 and height < 120):
                return False
        return True
    return False


def iter_paths(node: ET.Element, inside_non_render: bool = False):
    tag = node.tag.rsplit("}", 1)[-1]
    now_inside_non_render = inside_non_render or tag in NON_RENDER_CONTAINER_TAGS
    if tag == "path" and not now_inside_non_render and is_connector_path(node):
        yield node
    for child in node:
        yield from iter_paths(child, now_inside_non_render)


def audit_file(path: Path, tight_q: float, fail_diagonal: bool) -> tuple[int, list[str]]:
    root = ET.parse(path).getroot()
    failures = 0
    lines: list[str] = []

    for idx, node in enumerate(iter_paths(root), 1):
        d = node.get("d")
        if not d:
            continue
        ops = parse_path(d)
        cur: tuple[float, float] | None = None
        last_line: tuple[str, float] | None = None

        for op, values in ops:
            if op == "M":
                cur = (values[0], values[1])
                last_line = None
                continue
            if op == "L" and cur is not None:
                end = (values[0], values[1])
                direction, length = segment_direction(cur, end)
                if direction == "D" and fail_diagonal:
                    failures += 1
                    lines.append(f"{path.name}: path#{idx}: diagonal segment length={length:.1f} d={d[:140]}")
                if (
                    last_line
                    and direction in {"H", "V"}
                    and last_line[0] in {"H", "V"}
                    and direction != last_line[0]
                ):
                    failures += 1
                    short = min(last_line[1], length)
                    lines.append(f"{path.name}: path#{idx}: sharp L-after-L turn short_leg={short:.1f} d={d[:160]}")
                last_line = (direction, length)
                cur = end
                continue
            if op == "Q" and cur is not None:
                x1, y1, x, y = values
                pre = math.hypot(x1 - cur[0], y1 - cur[1])
                post = math.hypot(x - x1, y - y1)
                if min(pre, post) < tight_q:
                    failures += 1
                    lines.append(
                        f"{path.name}: path#{idx}: tight Q corner pre={pre:.1f} post={post:.1f} threshold={tight_q:.1f} d={d[:160]}"
                    )
                cur = (x, y)
                last_line = None
                continue
            last_line = None

    return failures, lines


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SVG connector corner geometry.")
    parser.add_argument("svg", nargs="+", type=Path)
    parser.add_argument("--tight-q", type=float, default=8.0, help="Minimum Q leg length before a corner is flagged.")
    parser.add_argument("--fail-diagonal", action="store_true", help="Treat diagonal path segments as failures.")
    args = parser.parse_args()

    total = 0
    for svg in args.svg:
        failures, lines = audit_file(svg, args.tight_q, args.fail_diagonal)
        total += failures
        for line in lines:
            print(line)
        print(f"{svg.name}: geometry_failures={failures}")

    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
