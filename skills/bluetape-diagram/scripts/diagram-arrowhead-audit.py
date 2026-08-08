#!/usr/bin/env python3
"""Audit SVG arrowhead roles, solid rendering, and bend clearance.

The audit deliberately complements (rather than replaces) connector geometry
and PNG inspection.  SVG metadata makes the intended arrowhead role and size
machine-checkable; the terminal-segment check catches a bend that is too close
to an arrowhead for the head to render cleanly.
"""

from __future__ import annotations

import argparse
import math
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

SVG_NS = "http://www.w3.org/2000/svg"
NS = {"svg": SVG_NS}
NUMBER = r"[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?"
TOKEN_RE = re.compile(rf"[A-Za-z]|{NUMBER}")
URL_RE = re.compile(r"url\(\s*#([^\s)]+)\s*\)")
SIZE_RE = re.compile(rf"^\s*({NUMBER})\s*[xX]\s*({NUMBER})\s*$")
NON_RENDER_TAGS = {"defs", "marker", "symbol", "clipPath", "mask", "pattern", "filter"}

ROLE_SIZES: dict[str, tuple[float, float]] = {
    "uml-hollow": (18.0, 16.0),
    "sequence": (16.0, 16.0),
    "primary": (14.0, 14.0),
    "secondary": (10.0, 10.0),
}
ROLE_ALIASES = {
    "uml": "uml-hollow",
    "inheritance": "uml-hollow",
    "generalization": "uml-hollow",
    "sequence-message": "sequence",
    "message": "sequence",
    "flow": "primary",
    "progression": "primary",
    "relationship": "secondary",
    "static": "secondary",
}
STANDARD_SIZES = set(ROLE_SIZES.values())


@dataclass(frozen=True)
class Marker:
    marker_id: str
    width: float | None
    height: float | None
    units: str | None
    role: str | None
    orient: str | None
    ref_x: float | None
    tip_direction: str | None


@dataclass(frozen=True)
class Segment:
    start_clearance: float
    end_clearance: float
    start_point: tuple[float, float] = (0.0, 0.0)
    end_point: tuple[float, float] = (0.0, 0.0)
    start_tangent: tuple[float, float] = (0.0, 0.0)
    end_tangent: tuple[float, float] = (0.0, 0.0)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_style(value: str | None) -> dict[str, str]:
    if not value:
        return {}
    result: dict[str, str] = {}
    for part in value.split(";"):
        if ":" not in part:
            continue
        key, item = part.split(":", 1)
        result[key.strip()] = item.strip()
    return result


def effective_attr(node: ET.Element, name: str) -> str | None:
    return node.attrib.get(name) or parse_style(node.attrib.get("style")).get(name)


def iter_rendered(root: ET.Element):
    def visit(node: ET.Element, hidden: bool = False):
        tag = local_name(node.tag)
        hidden_now = hidden or tag in NON_RENDER_TAGS
        if not hidden_now:
            yield node
        for child in list(node):
            yield from visit(child, hidden_now)

    yield from visit(root)


def number(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.search(NUMBER, value)
    return float(match.group(0)) if match else None


def marker_references(node: ET.Element) -> list[tuple[str, str]]:
    references: list[tuple[str, str]] = []
    for position in ("marker-start", "marker-mid", "marker-end"):
        value = effective_attr(node, position)
        if not value:
            continue
        match = URL_RE.search(value)
        if match:
            references.append((position, match.group(1)))
    return references


def normalize_role(role: str | None) -> str | None:
    if role is None:
        return None
    normalized = role.strip().lower()
    return ROLE_ALIASES.get(normalized, normalized)


def marker_inventory(root: ET.Element) -> dict[str, Marker]:
    markers: dict[str, Marker] = {}
    for marker in root.findall(".//svg:marker", NS):
        marker_id = marker.attrib.get("id", "<missing>")
        markers[marker_id] = Marker(
            marker_id=marker_id,
            width=number(marker.attrib.get("markerWidth")),
            height=number(marker.attrib.get("markerHeight")),
            units=marker.attrib.get("markerUnits"),
            role=normalize_role(marker.attrib.get("data-role")),
            orient=marker.attrib.get("orient"),
            ref_x=number(marker.attrib.get("refX")),
            tip_direction=marker.attrib.get("data-tip-direction"),
        )
    return markers


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def read_numbers(tokens: list[str], index: int, count: int) -> tuple[list[float], int] | None:
    if index + count > len(tokens) or any(token.isalpha() for token in tokens[index : index + count]):
        return None
    return [float(token) for token in tokens[index : index + count]], index + count


def parse_path_segments(d: str) -> list[list[Segment]]:
    """Return segments grouped by SVG subpath with tangent clearances."""

    tokens = TOKEN_RE.findall(d)
    index = 0
    command: str | None = None
    current = (0.0, 0.0)
    subpath_start: tuple[float, float] | None = None
    subpaths: list[list[Segment]] = []
    current_segments: list[Segment] | None = None

    while index < len(tokens):
        if tokens[index].isalpha():
            command = tokens[index]
            index += 1
        if command is None:
            raise ValueError("path data starts without a command")
        upper = command.upper()
        relative = command.islower()

        if upper == "M":
            parsed = read_numbers(tokens, index, 2)
            if parsed is None:
                raise ValueError("M command lacks coordinate pair")
            values, index = parsed
            point = (values[0], values[1])
            if relative:
                point = (point[0] + current[0], point[1] + current[1])
            current = point
            subpath_start = point
            current_segments = []
            subpaths.append(current_segments)
            command = "l" if relative else "L"
            continue

        if current_segments is None:
            raise ValueError("path data has no subpath")

        if upper in {"L", "T"}:
            count = 2
            parsed = read_numbers(tokens, index, count)
            if parsed is None:
                raise ValueError(f"{upper} command lacks coordinate pair")
            values, index = parsed
            end = (values[0], values[1])
            if relative:
                end = (end[0] + current[0], end[1] + current[1])
            tangent = (end[0] - current[0], end[1] - current[1])
            length = distance(current, end)
            current_segments.append(Segment(length, length, current, end, tangent, tangent))
            current = end
            continue

        if upper == "H":
            parsed = read_numbers(tokens, index, 1)
            if parsed is None:
                raise ValueError("H command lacks coordinate")
            values, index = parsed
            x = values[0] + current[0] if relative else values[0]
            end = (x, current[1])
            tangent = (end[0] - current[0], end[1] - current[1])
            length = distance(current, end)
            current_segments.append(Segment(length, length, current, end, tangent, tangent))
            current = end
            continue

        if upper == "V":
            parsed = read_numbers(tokens, index, 1)
            if parsed is None:
                raise ValueError("V command lacks coordinate")
            values, index = parsed
            y = values[0] + current[1] if relative else values[0]
            end = (current[0], y)
            tangent = (end[0] - current[0], end[1] - current[1])
            length = distance(current, end)
            current_segments.append(Segment(length, length, current, end, tangent, tangent))
            current = end
            continue

        if upper == "Q":
            parsed = read_numbers(tokens, index, 4)
            if parsed is None:
                raise ValueError("Q command lacks control/end coordinates")
            values, index = parsed
            control = (values[0], values[1])
            end = (values[2], values[3])
            if relative:
                control = (control[0] + current[0], control[1] + current[1])
                end = (end[0] + current[0], end[1] + current[1])
            current_segments.append(
                Segment(
                    distance(current, control),
                    distance(control, end),
                    current,
                    end,
                    (control[0] - current[0], control[1] - current[1]),
                    (end[0] - control[0], end[1] - control[1]),
                )
            )
            current = end
            continue

        if upper == "C":
            parsed = read_numbers(tokens, index, 6)
            if parsed is None:
                raise ValueError("C command lacks control/end coordinates")
            values, index = parsed
            c1 = (values[0], values[1])
            c2 = (values[2], values[3])
            end = (values[4], values[5])
            if relative:
                c1 = (c1[0] + current[0], c1[1] + current[1])
                c2 = (c2[0] + current[0], c2[1] + current[1])
                end = (end[0] + current[0], end[1] + current[1])
            current_segments.append(
                Segment(
                    distance(current, c1),
                    distance(c2, end),
                    current,
                    end,
                    (c1[0] - current[0], c1[1] - current[1]),
                    (end[0] - c2[0], end[1] - c2[1]),
                )
            )
            current = end
            continue

        if upper == "A":
            parsed = read_numbers(tokens, index, 7)
            if parsed is None:
                raise ValueError("A command lacks arc parameters")
            values, index = parsed
            end = (values[5], values[6])
            if relative:
                end = (end[0] + current[0], end[1] + current[1])
            length = distance(current, end)
            tangent = (end[0] - current[0], end[1] - current[1])
            current_segments.append(Segment(length, length, current, end, tangent, tangent))
            current = end
            continue

        if upper == "Z":
            if subpath_start is not None and current != subpath_start:
                length = distance(current, subpath_start)
                tangent = (subpath_start[0] - current[0], subpath_start[1] - current[1])
                current_segments.append(
                    Segment(length, length, current, subpath_start, tangent, tangent)
                )
            current = subpath_start or current
            command = None
            continue

        raise ValueError(f"unsupported path command {command}")

    return subpaths


def validate_marker_paint(marker: ET.Element, marker_id: str) -> list[str]:
    failures: list[str] = []
    visible_children = 0
    explicit_paint = False
    for child in marker.iter():
        if child is marker or local_name(child.tag) in {"title", "desc"}:
            continue
        visible_children += 1
        style = parse_style(child.attrib.get("style"))
        fill = child.attrib.get("fill") or style.get("fill")
        stroke = child.attrib.get("stroke") or style.get("stroke")
        dash = child.attrib.get("stroke-dasharray") or style.get("stroke-dasharray")
        for kind, value in (("fill", fill), ("stroke", stroke)):
            if value in {"context-stroke", "context-fill"}:
                failures.append(f"{marker_id}: marker {kind} uses {value}")
            elif value and value != "none":
                explicit_paint = True
        if stroke and stroke != "none" and dash is None:
            failures.append(f"{marker_id}: stroked marker child must declare stroke-dasharray=none")
        if dash and dash.replace("!important", "").strip() != "none":
            failures.append(f"{marker_id}: marker child dasharray is {dash}")
    if visible_children == 0:
        failures.append(f"{marker_id}: marker has no visible child")
    elif not explicit_paint:
        failures.append(f"{marker_id}: marker child has no explicit fill or stroke")
    return failures


def direct_arrowhead_nodes(root: ET.Element):
    for node in iter_rendered(root):
        classes = {item.replace("-", "").replace("_", "").lower() for item in node.attrib.get("class", "").split()}
        if node.attrib.get("data-arrowhead") == "true" or "arrowhead" in classes:
            yield node


def validate_direct_arrowhead(node: ET.Element) -> list[str]:
    failures: list[str] = []
    name = node.attrib.get("id") or node.attrib.get("class") or local_name(node.tag)
    if node.attrib.get("data-solid-head") != "true":
        failures.append(f"{name}: direct arrowhead must declare data-solid-head=\"true\"")
    role = normalize_role(node.attrib.get("data-role"))
    if role not in ROLE_SIZES:
        failures.append(f"{name}: direct arrowhead needs data-role in {', '.join(sorted(ROLE_SIZES))}")
    declared = node.attrib.get("data-size")
    expected = ROLE_SIZES.get(role or "")
    parsed = SIZE_RE.match(declared or "")
    if expected is not None and (parsed is None or tuple(float(item) for item in parsed.groups()) != expected):
        failures.append(f"{name}: data-size must be {expected[0]:g}x{expected[1]:g} for role {role}")
    dash = effective_attr(node, "stroke-dasharray")
    if dash and dash.replace("!important", "").strip() != "none":
        failures.append(f"{name}: direct arrowhead dasharray is {dash}")
    tip_direction = node.attrib.get("data-tip-direction")
    if tip_direction != "positive-x":
        failures.append(f"{name}: direct arrowhead needs data-tip-direction=positive-x")
    return failures


def path_tangent(node: ET.Element, position: str) -> tuple[float, float] | None:
    """Return the local tangent at the marker attachment point."""

    tag = local_name(node.tag)
    if tag == "path" and node.attrib.get("d"):
        subpaths = [subpath for subpath in parse_path_segments(node.attrib["d"]) if subpath]
        if not subpaths:
            return None
        segment = subpaths[0][0] if position == "marker-start" else subpaths[-1][-1]
        return segment.start_tangent if position == "marker-start" else segment.end_tangent
    if tag == "line":
        start = (number(node.attrib.get("x1")) or 0.0, number(node.attrib.get("y1")) or 0.0)
        end = (number(node.attrib.get("x2")) or 0.0, number(node.attrib.get("y2")) or 0.0)
        tangent = (end[0] - start[0], end[1] - start[1])
        return tangent if position == "marker-end" else (-tangent[0], -tangent[1])
    if tag in {"polyline", "polygon"} and node.attrib.get("points"):
        values = [float(item) for item in re.findall(NUMBER, node.attrib["points"])]
        points = list(zip(values[::2], values[1::2]))
        if len(points) < 2:
            return None
        if position == "marker-start":
            return (points[0][0] - points[1][0], points[0][1] - points[1][1])
        return (points[-1][0] - points[-2][0], points[-1][1] - points[-2][1])
    return None


def infer_marker_tip_direction(marker_element: ET.Element) -> str | None:
    """Infer a simple triangle's tip side, or return None for an ambiguous shape."""

    points: list[tuple[float, float]] = []
    for child in marker_element.iter():
        if local_name(child.tag) != "path" or not child.attrib.get("d"):
            continue
        try:
            points.extend(
                point
                for subpath in parse_path_segments(child.attrib["d"])
                for segment in subpath
                for point in (segment.start_point, segment.end_point)
            )
        except ValueError:
            return None
    unique = {(round(x, 6), round(y, 6)) for x, y in points}
    if len(unique) < 3:
        return None
    min_x = min(x for x, _ in unique)
    max_x = max(x for x, _ in unique)
    min_points = [point for point in unique if point[0] == min_x]
    max_points = [point for point in unique if point[0] == max_x]
    if len(max_points) == 1 and len(min_points) >= 2:
        return "positive-x"
    if len(min_points) == 1 and len(max_points) >= 2:
        return "negative-x"
    return None


def validate_marker_direction(marker: Marker, marker_element: ET.Element, positions: set[str], marker_id: str) -> list[str]:
    failures: list[str] = []
    orient = (marker.orient or "").strip().lower()
    if orient not in {"auto", "auto-start-reverse"}:
        failures.append(
            f"{marker_id}: orient must be auto or auto-start-reverse so SVG renderers follow connector direction"
        )
    if marker.tip_direction != "positive-x":
        failures.append(f"{marker_id}: marker needs data-tip-direction=positive-x for a forward local axis")
    inferred = infer_marker_tip_direction(marker_element)
    if inferred == "negative-x":
        failures.append(f"{marker_id}: marker geometry tip points negative-x; SVG output will reverse the arrowhead")
    elif inferred is None:
        failures.append(f"{marker_id}: marker geometry tip direction is ambiguous; declare a simple +x triangle")
    if "marker-start" in positions and orient != "auto-start-reverse":
        failures.append(f"{marker_id}: marker-start requires orient=auto-start-reverse")
    if "marker-end" in positions and orient not in {"auto", "auto-start-reverse"}:
        failures.append(f"{marker_id}: marker-end requires automatic orientation")
    return failures


def audit_file(path: Path, margin: float) -> tuple[bool, list[str], str]:
    root = ET.parse(path).getroot()
    markers = marker_inventory(root)
    marker_elements = {marker.attrib.get("id"): marker for marker in root.findall(".//svg:marker", NS)}
    references: list[tuple[ET.Element, str, str]] = []
    for node in iter_rendered(root):
        for position, marker_id in marker_references(node):
            references.append((node, position, marker_id))

    failures: list[str] = []
    used_ids = {marker_id for _, _, marker_id in references}
    positions_by_marker: dict[str, set[str]] = {}
    for _, position, marker_id in references:
        positions_by_marker.setdefault(marker_id, set()).add(position)
    for marker_id in sorted(used_ids):
        marker = markers.get(marker_id)
        if marker is None:
            failures.append(f"{marker_id}: referenced marker definition is missing")
            continue
        if marker.units != "userSpaceOnUse":
            failures.append(f"{marker_id}: markerUnits is not userSpaceOnUse")
        expected = ROLE_SIZES.get(marker.role or "")
        if marker.role not in ROLE_SIZES:
            failures.append(f"{marker_id}: referenced marker needs data-role in {', '.join(sorted(ROLE_SIZES))}")
            if marker.width is not None and marker.height is not None and (marker.width, marker.height) not in STANDARD_SIZES:
                allowed = ", ".join(f"{width:g}x{height:g}" for width, height in sorted(STANDARD_SIZES))
                failures.append(f"{marker_id}: untyped size is {marker.width:g}x{marker.height:g}; standard role sizes are {allowed}")
        elif marker.width is None or marker.height is None:
            failures.append(f"{marker_id}: markerWidth and markerHeight must be numeric")
        elif (marker.width, marker.height) != expected:
            failures.append(
                f"{marker_id}: size is {marker.width:g}x{marker.height:g}, expected {expected[0]:g}x{expected[1]:g} for role {marker.role}"
            )
        marker_element = marker_elements.get(marker_id)
        if marker_element is not None:
            failures.extend(validate_marker_paint(marker_element, marker_id))
            failures.extend(
                validate_marker_direction(marker, marker_element, positions_by_marker.get(marker_id, set()), marker_id)
            )

    for node in direct_arrowhead_nodes(root):
        failures.extend(validate_direct_arrowhead(node))

    terminal_checks = 0
    direction_checks = 0
    for node, position, marker_id in references:
        marker = markers.get(marker_id)
        if marker is None or marker.width is None or marker.height is None:
            continue
        if position != "marker-mid":
            tangent = path_tangent(node, position)
            if tangent is None:
                failures.append(
                    f"{node.attrib.get('id') or local_name(node.tag)}: {position} marker direction cannot be established from this shape"
                )
            elif math.hypot(*tangent) <= 1e-9:
                failures.append(
                    f"{node.attrib.get('id') or local_name(node.tag)}: {position} marker direction has a zero terminal tangent"
                )
            direction_checks += 1
        if position == "marker-mid" or local_name(node.tag) != "path" or not node.attrib.get("d"):
            continue
        try:
            subpaths = [subpath for subpath in parse_path_segments(node.attrib["d"]) if subpath]
        except ValueError as exc:
            failures.append(f"{node.attrib.get('id') or 'path'}: {exc}")
            continue
        if not subpaths:
            failures.append(f"{node.attrib.get('id') or 'path'}: marker {position} has no path segment")
            continue
        segments = subpaths[0] if position == "marker-start" else subpaths[-1]
        segment = segments[0] if position == "marker-start" else segments[-1]
        clearance = segment.start_clearance if position == "marker-start" else segment.end_clearance
        required = max(marker.width, marker.height) + margin
        terminal_checks += 1
        if clearance < required:
            name = node.attrib.get("id") or node.attrib.get("data-connector") or "path"
            failures.append(
                f"{name}: {position} marker {marker_id} terminal clearance {clearance:.1f}px < required {required:.1f}px"
            )

    status = "FAIL" if failures else "PASS"
    summary = (
        f"{path.name}: {status} markers={len(markers)} used_markers={len(used_ids)} "
        f"direct_heads={sum(1 for _ in direct_arrowhead_nodes(root))} direction_checks={direction_checks} "
        f"terminal_checks={terminal_checks}"
    )
    return not failures, failures, summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SVG arrowhead roles, paint, and bend clearance.")
    parser.add_argument("svg", nargs="+", type=Path)
    parser.add_argument(
        "--clearance-margin",
        type=float,
        default=1.0,
        help="Extra pixels required beyond marker width/height before a bend.",
    )
    args = parser.parse_args()
    ok = True
    for path in args.svg:
        try:
            passed, failures, summary = audit_file(path, args.clearance_margin)
        except (ET.ParseError, OSError, ValueError) as exc:
            print(f"{path.name}: FAIL schema: {exc}")
            ok = False
            continue
        print(summary)
        if not passed:
            ok = False
            for failure in failures:
                print(f"  arrowhead: {failure}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
