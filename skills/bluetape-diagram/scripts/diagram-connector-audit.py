#!/usr/bin/env python3
"""Audit bluetape4k SVG connector and relationship-label geometry.

This is a screening tool for bluetape4k README diagrams. It intentionally does
not replace rendered-PNG inspection: typography quality, visual near-crossings,
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
NUMBER_PATTERN = r"[-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?"
PATH_TOKEN_RE = re.compile(rf"[A-Za-z]|{NUMBER_PATTERN}")
NUMBER_RE = re.compile(NUMBER_PATTERN)
NUMBER_SEPARATOR_PATTERN = r"(?:\s*,\s*|\s+|(?=[+-]))"
NUMBER_LIST_RE = re.compile(
    rf"\s*{NUMBER_PATTERN}(?:{NUMBER_SEPARATOR_PATTERN}{NUMBER_PATTERN})*\s*"
)
TRANSFORM_RE = re.compile(r"([A-Za-z]+)\s*\(([^)]*)\)")
CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")
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
LABEL_CLASSES = {"connectorlabel", "edgelabel", "relationshiplabel"}
IDENTITY_MATRIX = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


@dataclass(frozen=True)
class Rect:
    x: float
    y: float
    width: float
    height: float


@dataclass(frozen=True)
class Segment:
    key: str
    name: str
    a: tuple[float, float]
    b: tuple[float, float]


@dataclass(frozen=True)
class Label:
    name: str
    rect: Rect
    own_connectors: frozenset[str]


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


def normalized_classes(node: ET.Element) -> set[str]:
    return {re.sub(r"[-_]", "", name).lower() for name in classes(node)}


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


def parse_subpaths(d: str) -> list[list[tuple[float, float]]]:
    subpaths: list[list[tuple[float, float]]] = []
    points: list[tuple[float, float]] = []
    tokens = PATH_TOKEN_RE.findall(d.replace(",", " "))
    index = 0
    command: str | None = None
    current = (0.0, 0.0)
    subpath_start: tuple[float, float] | None = None
    while index < len(tokens):
        token = tokens[index]
        if not is_number(token):
            command = token
            index += 1
            if command in {"Z", "z"}:
                if subpath_start is not None and points[-1] != subpath_start:
                    points.append(subpath_start)
                current = subpath_start or current
                command = None
                continue
        if command is None:
            raise ValueError("path data starts without a command")

        relative = command.islower()
        op = command.upper()
        if op == "M":
            if not has_numbers(tokens, index, 2):
                raise ValueError("M command lacks coordinate pair")
            if points:
                subpaths.append(points)
                points = []
            x, y = float(tokens[index]), float(tokens[index + 1])
            index += 2
            if relative:
                x += current[0]
                y += current[1]
            current = (x, y)
            subpath_start = current
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
    if points:
        subpaths.append(points)
    return subpaths


def rect_from_element(el: ET.Element) -> Rect | None:
    try:
        return Rect(
            float(el.attrib.get("x", "0")),
            float(el.attrib.get("y", "0")),
            float(el.attrib["width"]),
            float(el.attrib["height"]),
        )
    except (KeyError, ValueError):
        return None


def is_card_rect(el: ET.Element) -> bool:
    cls = " ".join(classes(el)).lower()
    ident = el.attrib.get("id", "").lower()
    return "card" in cls or re.search(r"(^|[-_])card($|[-_])", ident) is not None


def is_connector_path(el: ET.Element) -> bool:
    if el.attrib.get("data-connector"):
        return True
    if any(
        el.attrib.get(name) for name in ("marker-start", "marker-mid", "marker-end")
    ):
        return True
    lower_classes = {name.lower() for name in classes(el)}
    if lower_classes & CONNECTOR_CLASSES:
        return True
    ident = el.attrib.get("id", "").lower()
    return (
        re.search(r"(^|[-_])(connector|edge|flow|message|route|arrow)($|[-_])", ident)
        is not None
    )


def ancestor_chain(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
):
    current: ET.Element | None = el
    while current is not None:
        yield current
        current = parent_map.get(current)


def relationship_name(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
) -> str | None:
    for ancestor in ancestor_chain(el, parent_map):
        source = ancestor.attrib.get("data-from")
        target = ancestor.attrib.get("data-to")
        if source and target:
            return f"{source}-to-{target}"
    return None


def connector_name(
    el: ET.Element,
    index: int,
    parent_map: dict[ET.Element, ET.Element],
) -> str:
    return (
        el.attrib.get("data-connector")
        or relationship_name(el, parent_map)
        or el.attrib.get("id")
        or f"path#{index}"
    )


def card_name(
    el: ET.Element,
    index: int,
    parent_map: dict[ET.Element, ET.Element],
) -> str:
    for ancestor in ancestor_chain(el, parent_map):
        if ancestor.attrib.get("id"):
            return ancestor.attrib["id"]
    return f"card#{index}"


def multiply_matrices(
    left: tuple[float, float, float, float, float, float],
    right: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    la, lb, lc, ld, le, lf = left
    ra, rb, rc, rd, re, rf = right
    return (
        la * ra + lc * rb,
        lb * ra + ld * rb,
        la * rc + lc * rd,
        lb * rc + ld * rd,
        la * re + lc * rf + le,
        lb * re + ld * rf + lf,
    )


def parse_transform(
    value: str,
) -> tuple[float, float, float, float, float, float]:
    combined = IDENTITY_MATRIX
    remainder = TRANSFORM_RE.sub("", value).strip(" ,\t\r\n")
    if remainder:
        raise ValueError(f"unsupported transform syntax: {value}")
    for match in TRANSFORM_RE.finditer(value):
        operation = match.group(1).lower()
        arguments = match.group(2)
        if NUMBER_LIST_RE.fullmatch(arguments) is None:
            raise ValueError(f"unsupported transform syntax: {match.group(0)}")
        values = [float(number) for number in NUMBER_RE.findall(arguments)]
        if operation == "matrix" and len(values) == 6:
            local = tuple(values)
        elif operation == "translate" and len(values) in {1, 2}:
            local = (
                1.0,
                0.0,
                0.0,
                1.0,
                values[0],
                values[1] if len(values) == 2 else 0.0,
            )
        elif operation == "scale" and len(values) in {1, 2}:
            sy = values[1] if len(values) == 2 else values[0]
            local = (values[0], 0.0, 0.0, sy, 0.0, 0.0)
        elif operation == "rotate" and len(values) in {1, 3}:
            angle = math.radians(values[0])
            rotation = (
                math.cos(angle),
                math.sin(angle),
                -math.sin(angle),
                math.cos(angle),
                0.0,
                0.0,
            )
            if len(values) == 3:
                cx, cy = values[1:]
                local = multiply_matrices(
                    multiply_matrices((1.0, 0.0, 0.0, 1.0, cx, cy), rotation),
                    (1.0, 0.0, 0.0, 1.0, -cx, -cy),
                )
            else:
                local = rotation
        elif operation == "skewx" and len(values) == 1:
            local = (1.0, 0.0, math.tan(math.radians(values[0])), 1.0, 0.0, 0.0)
        elif operation == "skewy" and len(values) == 1:
            local = (1.0, math.tan(math.radians(values[0])), 0.0, 1.0, 0.0, 0.0)
        else:
            raise ValueError(f"unsupported transform operation: {match.group(0)}")
        combined = multiply_matrices(combined, local)  # type: ignore[arg-type]
    return combined


def element_matrix(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
) -> tuple[float, float, float, float, float, float]:
    combined = IDENTITY_MATRIX
    for ancestor in reversed(list(ancestor_chain(el, parent_map))):
        local = parse_transform(ancestor.attrib.get("transform", ""))
        combined = multiply_matrices(combined, local)
    return combined


def transform_point(
    point: tuple[float, float],
    matrix: tuple[float, float, float, float, float, float],
) -> tuple[float, float]:
    a, b, c, d, e, f = matrix
    x, y = point
    return a * x + c * y + e, b * x + d * y + f


def transformed_rect(
    rect: Rect,
    matrix: tuple[float, float, float, float, float, float],
) -> Rect:
    corners = (
        (rect.x, rect.y),
        (rect.x + rect.width, rect.y),
        (rect.x, rect.y + rect.height),
        (rect.x + rect.width, rect.y + rect.height),
    )
    points = [transform_point(point, matrix) for point in corners]
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))


def transformed_points(
    points: list[tuple[float, float]],
    matrix: tuple[float, float, float, float, float, float],
) -> list[tuple[float, float]]:
    return [transform_point(point, matrix) for point in points]


def point_inside_rect(point: tuple[float, float], rect: Rect, pad: float) -> bool:
    x, y = point
    return (
        rect.x + pad < x < rect.x + rect.width - pad
        and rect.y + pad < y < rect.y + rect.height - pad
    )


def point_in_or_on_rect(point: tuple[float, float], rect: Rect) -> bool:
    x, y = point
    return rect.x <= x <= rect.x + rect.width and rect.y <= y <= rect.y + rect.height


def expanded_rect(rect: Rect, padding: float) -> Rect:
    return Rect(
        rect.x - padding,
        rect.y - padding,
        rect.width + 2 * padding,
        rect.height + 2 * padding,
    )


def rects_overlap(left: Rect, right: Rect) -> bool:
    return (
        left.x < right.x + right.width
        and left.x + left.width > right.x
        and left.y < right.y + right.height
        and left.y + left.height > right.y
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


def segments_intersect_inclusive(seg1: Segment, seg2: Segment) -> bool:
    a, b, c, d = seg1.a, seg1.b, seg2.a, seg2.b
    o1 = orientation(a, b, c)
    o2 = orientation(a, b, d)
    o3 = orientation(c, d, a)
    o4 = orientation(c, d, b)
    if abs(o1) < 1e-6 and on_segment(a, b, c):
        return True
    if abs(o2) < 1e-6 and on_segment(a, b, d):
        return True
    if abs(o3) < 1e-6 and on_segment(c, d, a):
        return True
    if abs(o4) < 1e-6 and on_segment(c, d, b):
        return True
    return (o1 > 0) != (o2 > 0) and (o3 > 0) != (o4 > 0)


def segment_intersects_rect(segment: Segment, rect: Rect) -> bool:
    if point_in_or_on_rect(segment.a, rect) or point_in_or_on_rect(segment.b, rect):
        return True
    top_left = (rect.x, rect.y)
    top_right = (rect.x + rect.width, rect.y)
    bottom_left = (rect.x, rect.y + rect.height)
    bottom_right = (rect.x + rect.width, rect.y + rect.height)
    edges = (
        Segment("rect-top", "rect", top_left, top_right),
        Segment("rect-right", "rect", top_right, bottom_right),
        Segment("rect-bottom", "rect", bottom_right, bottom_left),
        Segment("rect-left", "rect", bottom_left, top_left),
    )
    return any(segments_intersect_inclusive(segment, edge) for edge in edges)


def collinear_overlap_length(left: Segment, right: Segment) -> float:
    if (
        abs(orientation(left.a, left.b, right.a)) > 1e-6
        or abs(orientation(left.a, left.b, right.b)) > 1e-6
    ):
        return 0.0
    dx = abs(left.b[0] - left.a[0])
    dy = abs(left.b[1] - left.a[1])
    axis = 0 if dx >= dy else 1
    left_min, left_max = sorted((left.a[axis], left.b[axis]))
    right_min, right_max = sorted((right.a[axis], right.b[axis]))
    return max(0.0, min(left_max, right_max) - max(left_min, right_min))


def is_label_element(el: ET.Element) -> bool:
    return bool(normalized_classes(el) & LABEL_CLASSES)


def parse_css_font_sizes(root: ET.Element) -> dict[str, float]:
    font_sizes: dict[str, float] = {}
    for style in root.iter():
        if local_name(style.tag) != "style" or not style.text:
            continue
        for selectors, declarations in CSS_RULE_RE.findall(style.text):
            size_match = re.search(
                r"font-size\s*:\s*"
                r"([-+]?(?:\d+\.\d+|\d+|\.\d+)(?:[eE][-+]?\d+)?)",
                declarations,
            )
            if not size_match:
                continue
            for class_name in re.findall(r"\.([A-Za-z_][\w-]*)", selectors):
                font_sizes[re.sub(r"[-_]", "", class_name).lower()] = float(
                    size_match.group(1)
                )
    return font_sizes


def first_number(value: str | None) -> float | None:
    if not value:
        return None
    match = NUMBER_RE.search(value)
    return float(match.group(0)) if match else None


def label_text(el: ET.Element) -> str:
    return " ".join("".join(el.itertext()).split()) or "<empty-label>"


def font_size_for(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    css_font_sizes: dict[str, float],
) -> float:
    direct = first_number(el.attrib.get("font-size"))
    if direct is not None:
        return direct
    styled = first_number(parse_style(el.attrib.get("style")).get("font-size"))
    if styled is not None:
        return styled
    for ancestor in ancestor_chain(el, parent_map):
        for class_name in normalized_classes(ancestor):
            if class_name in css_font_sizes:
                return css_font_sizes[class_name]
    return 14.0


def text_rect(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    css_font_sizes: dict[str, float],
) -> Rect | None:
    coordinate_node = el
    x = first_number(el.attrib.get("x"))
    y = first_number(el.attrib.get("y"))
    if x is None or y is None:
        for descendant in el.iter():
            if local_name(descendant.tag) != "tspan":
                continue
            candidate_x = first_number(descendant.attrib.get("x"))
            candidate_y = first_number(descendant.attrib.get("y"))
            if candidate_x is not None and candidate_y is not None:
                coordinate_node = descendant
                x, y = candidate_x, candidate_y
                break
    if x is None or y is None:
        return None

    size = font_size_for(el, parent_map, css_font_sizes)
    lines = [" ".join("".join(node.itertext()).split()) for node in el]
    content = label_text(el)
    longest = max((len(line) for line in lines if line), default=len(content))
    width = max(size, longest * size * 0.62)
    height = size * 1.25 * max(1, len([line for line in lines if line]))
    anchor = el.attrib.get("text-anchor") or parse_style(el.attrib.get("style")).get(
        "text-anchor", "start"
    )
    if anchor == "middle":
        x -= width / 2
    elif anchor == "end":
        x -= width
    rect = Rect(x, y - size, width, height)
    return transformed_rect(rect, element_matrix(coordinate_node, parent_map))


def label_rect(
    el: ET.Element,
    parent_map: dict[ET.Element, ET.Element],
    css_font_sizes: dict[str, float],
) -> Rect | None:
    if local_name(el.tag) == "text":
        return text_rect(el, parent_map, css_font_sizes)
    for descendant in el.iter():
        if local_name(descendant.tag) != "rect":
            continue
        rect = rect_from_element(descendant)
        if rect is not None:
            return transformed_rect(rect, element_matrix(descendant, parent_map))
    for descendant in el.iter():
        if local_name(descendant.tag) == "text":
            return text_rect(descendant, parent_map, css_font_sizes)
    return None


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
    parent_map = {child: parent for parent in root.iter() for child in parent}
    cards: list[tuple[str, Rect]] = []
    for card_index, rect_el in enumerate(iter_rendered(root, "rect"), start=1):
        if not is_card_rect(rect_el):
            continue
        rect = rect_from_element(rect_el)
        if rect is not None:
            cards.append(
                (
                    card_name(rect_el, card_index, parent_map),
                    transformed_rect(rect, element_matrix(rect_el, parent_map)),
                )
            )

    connector_paths = [
        el for el in iter_rendered(root, "path") if is_connector_path(el)
    ]
    segments: list[Segment] = []
    connector_names: dict[ET.Element, str] = {}
    connector_keys: dict[ET.Element, str] = {}
    connector_names_by_key: dict[str, str] = {}
    for path_index, path_el in enumerate(connector_paths, start=1):
        key = f"path#{path_index}"
        name = connector_name(path_el, path_index, parent_map)
        connector_keys[path_el] = key
        connector_names[path_el] = name
        connector_names_by_key[key] = name
        try:
            subpaths = parse_subpaths(path_el.attrib.get("d", ""))
        except ValueError as exc:
            print(f"{path.name}: FAIL {name}: {exc}")
            return False
        matrix = element_matrix(path_el, parent_map)
        for points in subpaths:
            points = transformed_points(points, matrix)
            for a, b in zip(points, points[1:]):
                segments.append(Segment(key, name, a, b))

    ancestor_connectors: dict[ET.Element, set[str]] = {}
    for connector, key in connector_keys.items():
        for ancestor in ancestor_chain(connector, parent_map):
            ancestor_connectors.setdefault(ancestor, set()).add(key)

    css_font_sizes = parse_css_font_sizes(root)
    labels: list[Label] = []
    unbounded_labels: list[str] = []
    for label_el in (el for el in iter_rendered(root) if is_label_element(el)):
        if any(
            is_label_element(ancestor)
            for ancestor in list(ancestor_chain(label_el, parent_map))[1:]
        ):
            continue
        name = label_text(label_el)
        bounds = label_rect(label_el, parent_map, css_font_sizes)
        if bounds is None:
            unbounded_labels.append(name)
            continue
        own_connectors: set[str] = set()
        relation = relationship_name(label_el, parent_map)
        for ancestor in ancestor_chain(label_el, parent_map):
            candidates = ancestor_connectors.get(ancestor)
            if candidates is None:
                continue
            if relation:
                matching = {
                    key for key in candidates if connector_names_by_key[key] == relation
                }
                if matching:
                    own_connectors = matching
                    break
            if len(candidates) == 1:
                own_connectors = candidates
                break
        if not own_connectors and relation:
            matching = {
                key for key, name in connector_names_by_key.items() if name == relation
            }
            if len(matching) == 1:
                own_connectors = matching
        labels.append(Label(name, bounds, frozenset(own_connectors)))

    marker_failures = audit_markers(root)
    intrusions: set[str] = set()
    for segment in segments:
        for _, rect in cards:
            if segment_intrudes_rect(
                segment, rect, args.card_padding, args.sample_step
            ):
                intrusions.add(segment.name)
                break

    crossings: set[tuple[str, str]] = set()
    shared_segments: set[tuple[str, str]] = set()
    for idx, left in enumerate(segments):
        for right in segments[idx + 1 :]:
            if left.key == right.key:
                continue
            if proper_intersection(left, right):
                crossings.add(tuple(sorted((left.name, right.name))))
            if collinear_overlap_length(left, right) >= args.min_shared_segment:
                shared_segments.add(tuple(sorted((left.name, right.name))))

    label_cards: set[tuple[str, str]] = set()
    label_labels: set[tuple[str, str]] = set()
    label_connectors: set[tuple[str, str]] = set()
    for label in labels:
        padded = expanded_rect(label.rect, args.label_padding)
        for card, rect in cards:
            if rects_overlap(padded, rect):
                label_cards.add((label.name, card))
        for segment in segments:
            if segment.key in label.own_connectors:
                continue
            if segment_intersects_rect(segment, padded):
                label_connectors.add((label.name, segment.name))
    for index, left in enumerate(labels):
        for right in labels[index + 1 :]:
            if rects_overlap(
                expanded_rect(left.rect, args.label_padding),
                expanded_rect(right.rect, args.label_padding),
            ):
                label_labels.add(tuple(sorted((left.name, right.name))))

    schema_failures: list[str] = []
    connector_like_markers = len(root.findall(".//svg:marker", NS))
    if connector_like_markers and not connector_paths:
        schema_failures.append(
            "marker definitions exist but no rendered connector paths were detected"
        )
    if connector_paths and not any(segments):
        schema_failures.append(
            "connector paths were detected but no path segments parsed"
        )
    for label in unbounded_labels:
        schema_failures.append(f"relationship label could not be bounded: {label}")

    failed = bool(
        marker_failures
        or schema_failures
        or intrusions
        or crossings
        or shared_segments
        or label_cards
        or label_labels
        or label_connectors
    )
    status = "FAIL" if failed else "PASS"
    print(
        f"{path.name}: {status} markers={len(root.findall('.//svg:marker', NS))} "
        f"connectors={len(connector_paths)} cards={len(cards)} labels={len(labels)} "
        f"intrusions={len(intrusions)} crossings={len(crossings)} "
        f"shared_segments={len(shared_segments)} label_cards={len(label_cards)} "
        f"label_labels={len(label_labels)} label_connectors={len(label_connectors)}"
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
    if shared_segments:
        for left, right in sorted(shared_segments):
            print(f"  shared segment: {left} <-> {right}")
    if label_cards:
        for label, card in sorted(label_cards):
            print(f"  label/card: {label!r} <-> {card}")
    if label_labels:
        for left, right in sorted(label_labels):
            print(f"  label/label: {left!r} <-> {right!r}")
    if label_connectors:
        for label, connector in sorted(label_connectors):
            print(f"  label/connector: {label!r} <-> {connector}")
    return not failed


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit SVG connector and relationship-label geometry."
    )
    parser.add_argument("svg", nargs="+", type=Path)
    parser.add_argument("--card-padding", type=float, default=1.5)
    parser.add_argument("--sample-step", type=float, default=8.0)
    parser.add_argument(
        "--min-shared-segment",
        type=float,
        default=0.01,
        help="Minimum collinear overlap between different connectors.",
    )
    parser.add_argument(
        "--label-padding",
        type=float,
        default=2.0,
        help="Clearance around relationship-label bounds.",
    )
    args = parser.parse_args()

    ok = True
    for svg in args.svg:
        try:
            ok = audit_file(svg, args) and ok
        except ValueError as exc:
            print(f"{svg.name}: FAIL schema: {exc}")
            ok = False
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
