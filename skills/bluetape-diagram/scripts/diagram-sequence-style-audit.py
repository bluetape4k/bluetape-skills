#!/usr/bin/env python3
"""Audit bluetape4k best-practices structure for sequence SVGs.

This is a screening gate, not a visual substitute. It rejects sequence-named
SVGs that are only lifelines plus arrows and do not contain the local
best-practices sequence-family signals:
- participant header cards;
- vertical lifelines;
- activation bars;
- pill message labels;
- fixed userSpaceOnUse sequence arrow markers with the established 10x10
  filled-triangle marker shape;
- branch regions when the diagram declares alt/else/loop text.
- visible numbered message labels;
- no hidden validator-only label artifacts;
- branch-local message colors when an alt/else/loop frame contains multiple
  message paths.
"""

from __future__ import annotations

import argparse
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

HEADER_RECT_CLASSES = {"header", "card", "actor", "participant"}
PARTICIPANT_TEXT_CLASSES = {"participant", "participant-title", "cardTitle", "card-title", "actorTitle"}
ROLE_TEXT_CLASSES = {"role", "participant-sub", "actorNote"}
LABEL_RECT_CLASSES = {"label", "labelPill", "pill"}
ALT_RECT_CLASSES = {"alt", "altBox", "branch"}
BRANCH_DIVIDER_CLASSES = {"branchDivider", "divider"}
MESSAGE_PATH_CLASSES = {
    "call",
    "slot",
    "state",
    "return",
    "ret",
    "skip",
    "error",
    "fail",
    "seq",
    "seqReturn",
    "wait",
    "edge",
    "edgeThin",
    "blue",
    "green",
    "orange",
    "purple",
    "amber",
    "callBlue",
    "callGreen",
    "callAmber",
    "callRed",
    "sql",
    "work",
    "crypto",
    "async",
}
TEXT_LABEL_CLASSES = {"label", "labelText", "msg", "badge", "badgeText", "num", "detail"}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def classes(node: ET.Element) -> set[str]:
    return set(node.attrib.get("class", "").split())


def parse_style(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    entries: dict[str, str] = {}
    for part in style.split(";"):
        if ":" not in part:
            continue
        key, value = part.split(":", 1)
        entries[key.strip()] = value.strip()
    return entries


def attr_value(node: ET.Element, name: str) -> str | None:
    return node.attrib.get(name) or parse_style(node.attrib.get("style")).get(name)


def is_hidden(node: ET.Element) -> bool:
    style = parse_style(node.attrib.get("style"))
    display = node.attrib.get("display") or style.get("display")
    visibility = node.attrib.get("visibility") or style.get("visibility")
    opacity = node.attrib.get("opacity") or style.get("opacity")
    if display == "none" or visibility == "hidden":
        return True
    try:
        return opacity is not None and float(opacity) <= 0.01
    except ValueError:
        return False


def attr_float(node: ET.Element, name: str) -> float | None:
    value = node.attrib.get(name)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def text_content(root: ET.Element) -> str:
    return " ".join(t.strip() for t in root.itertext() if t and t.strip())


def is_sequence(path: Path, root: ET.Element) -> bool:
    if "sequence" in path.name.lower():
        return True
    return "sequence" in text_content(root).lower()


def count_by_class(root: ET.Element, names: set[str], tag: str | None = None) -> int:
    count = 0
    for node in root.iter():
        if is_hidden(node):
            continue
        if tag is not None and local_name(node.tag) != tag:
            continue
        if classes(node) & names:
            count += 1
    return count


def nodes_by_class(root: ET.Element, names: set[str], tag: str | None = None) -> list[ET.Element]:
    nodes: list[ET.Element] = []
    for node in root.iter():
        if is_hidden(node):
            continue
        if tag is not None and local_name(node.tag) != tag:
            continue
        if classes(node) & names:
            nodes.append(node)
    return nodes


def visible_text_nodes(root: ET.Element) -> list[ET.Element]:
    return [
        node
        for node in root.iter()
        if local_name(node.tag) == "text" and not is_hidden(node) and text_content(node)
    ]


def text_inside_rect(text_node: ET.Element, rect: ET.Element) -> bool:
    tx = attr_float(text_node, "x")
    ty = attr_float(text_node, "y")
    rx = attr_float(rect, "x")
    ry = attr_float(rect, "y")
    rw = attr_float(rect, "width")
    rh = attr_float(rect, "height")
    if None in (tx, ty, rx, ry, rw, rh):
        return False
    return rx <= tx <= rx + rw and ry <= ty <= ry + rh


def marker_paths(marker: ET.Element) -> list[ET.Element]:
    return [node for node in marker.iter() if local_name(node.tag) == "path"]


def normalized_path(d: str | None) -> str:
    if not d:
        return ""
    return re.sub(r"\s+", " ", d.replace(",", " ")).strip()


def class_style_map(root: ET.Element) -> dict[str, dict[str, str]]:
    styles: dict[str, dict[str, str]] = {}
    for style_node in root.iter():
        if local_name(style_node.tag) != "style" or not style_node.text:
            continue
        for selector, body in re.findall(r"([^{}]+)\{([^{}]+)\}", style_node.text):
            props = parse_style(body)
            if not props:
                continue
            for part in selector.split(","):
                for class_name in re.findall(r"\.([A-Za-z0-9_-]+)", part):
                    styles.setdefault(class_name, {}).update(props)
    return styles


def css_value(node: ET.Element, name: str, styles: dict[str, dict[str, str]]) -> str | None:
    direct = attr_value(node, name)
    if direct is not None:
        return direct
    value = None
    for class_name in classes(node):
        value = styles.get(class_name, {}).get(name, value)
    return value


def message_path_nodes(root: ET.Element) -> list[ET.Element]:
    return [
        node
        for node in nodes_by_class(root, MESSAGE_PATH_CLASSES, "path")
        if node.attrib.get("d") and not node.attrib.get("d", "").startswith("M 0 0 L 10 5")
    ]


def activation_count(root: ET.Element) -> int:
    count = count_by_class(root, {"activation"}, "rect")
    for node in root.iter():
        if local_name(node.tag) != "rect" or is_hidden(node) or "activation" in classes(node):
            continue
        width = attr_float(node, "width")
        height = attr_float(node, "height")
        rx = attr_float(node, "rx") or 0.0
        if width is not None and height is not None and width <= 24 and height >= 50 and rx >= 4:
            count += 1
    return count


def label_rect_failures(root: ET.Element) -> list[str]:
    failures: list[str] = []
    for index, rect in enumerate(nodes_by_class(root, LABEL_RECT_CLASSES, "rect"), start=1):
        width = attr_float(rect, "width")
        height = attr_float(rect, "height")
        if width is not None and height is not None and (width < 8 or height < 8):
            failures.append(f"pill label #{index} is too small to be a visible message label")
    for index, node in enumerate(root.iter(), start=1):
        if not (classes(node) & (LABEL_RECT_CLASSES | TEXT_LABEL_CLASSES)):
            continue
        if is_hidden(node):
            failures.append(f"label-like element #{index} is hidden or transparent")
    return failures


def numbered_message_failures(root: ET.Element) -> list[str]:
    numbers: list[int] = []
    for text_node in visible_text_nodes(root):
        if not (classes(text_node) & TEXT_LABEL_CLASSES):
            continue
        text = text_content(text_node)
        match = re.fullmatch(r"\s*(\d+)\s*[\.)]?\s*", text)
        if match:
            numbers.append(int(match.group(1)))
    if len(numbers) < 2:
        return ["missing visible numbered message labels"]
    unique = sorted(set(numbers))
    expected = list(range(1, unique[-1] + 1))
    if unique != expected:
        return [f"message label numbers are not contiguous from 1: found={unique} expected={expected}"]
    return []


def path_y_values(path: ET.Element) -> list[float]:
    numbers = [float(value) for value in re.findall(r"[-+]?\d+(?:\.\d+)?", path.attrib.get("d", ""))]
    return numbers[1::2]


def branch_color_failures(root: ET.Element) -> list[str]:
    styles = class_style_map(root)
    failures: list[str] = []
    paths = message_path_nodes(root)
    regions = nodes_by_class(root, ALT_RECT_CLASSES, "rect")
    outside_colors: set[str] = set()
    for path in paths:
        ys = path_y_values(path)
        in_region = False
        for region in regions:
            y = attr_float(region, "y")
            height = attr_float(region, "height")
            if y is not None and height is not None and ys and not (max(ys) < y or min(ys) > y + height):
                in_region = True
                break
        if in_region:
            continue
        stroke = css_value(path, "stroke", styles)
        if stroke and stroke not in {"none", "transparent"}:
            outside_colors.add(stroke.lower())
    for index, region in enumerate(regions, start=1):
        y = attr_float(region, "y")
        height = attr_float(region, "height")
        if y is None or height is None:
            continue
        colors: set[str] = set()
        branch_paths = 0
        for path in paths:
            ys = path_y_values(path)
            if not ys or max(ys) < y or min(ys) > y + height:
                continue
            branch_paths += 1
            stroke = css_value(path, "stroke", styles)
            if stroke and stroke not in {"none", "transparent"}:
                colors.add(stroke.lower())
        if branch_paths >= 2 and not (colors - outside_colors):
            failures.append(
                f"alt/else/loop region #{index} has no branch-specific message color"
            )
    return failures


def audit_file(path: Path) -> list[str]:
    root = ET.parse(path).getroot()
    if not is_sequence(path, root):
        return []

    failures: list[str] = []
    if count_by_class(root, {"frame"}, "rect") < 1:
        failures.append("missing best-practices outer frame rect with class 'frame'")

    if count_by_class(root, {"title"}, "text") < 1:
        failures.append("missing best-practices title text with class 'title'")

    if count_by_class(root, {"subtitle"}, "text") < 1:
        failures.append("missing best-practices subtitle text with class 'subtitle'")

    participant_titles = count_by_class(root, PARTICIPANT_TEXT_CLASSES, "text")
    if participant_titles < 2:
        failures.append("missing participant title text with class 'participant'")

    participant_headers = count_by_class(root, HEADER_RECT_CLASSES, "rect")
    if participant_headers < 2 and participant_titles < 2:
        failures.append("missing participant header cards with class 'header'")

    participant_roles = count_by_class(root, ROLE_TEXT_CLASSES, "text")
    if 0 < participant_roles < 2:
        failures.append("participant role text is incomplete")

    lifelines = count_by_class(root, {"lifeline", "life"})
    if lifelines < 2:
        failures.append("missing vertical lifelines")

    activations = activation_count(root)
    if activations < 1:
        failures.append("missing activation bars")

    pill_labels = count_by_class(root, LABEL_RECT_CLASSES, "rect")
    if pill_labels < 2:
        failures.append("missing pill message labels")
    else:
        texts = visible_text_nodes(root)
        for index, rect in enumerate(nodes_by_class(root, LABEL_RECT_CLASSES, "rect"), start=1):
            if not any(text_inside_rect(text_node, rect) for text_node in texts):
                failures.append(f"pill label #{index} has no label text inside its box")
    failures.extend(label_rect_failures(root))
    failures.extend(numbered_message_failures(root))

    marker_failures: list[str] = []
    marker_count = 0
    for node in root.iter():
        if local_name(node.tag) != "marker":
            continue
        marker_id = node.attrib.get("id", "")
        if not re.search(r"arrow|seq", marker_id, re.IGNORECASE):
            continue
        marker_count += 1
        if node.attrib.get("markerUnits") != "userSpaceOnUse":
            marker_failures.append(f"{marker_id}: markerUnits is not userSpaceOnUse")
        if node.attrib.get("viewBox") is not None and node.attrib.get("viewBox") != "0 0 10 10":
            marker_failures.append(f"{marker_id}: marker viewBox is not 0 0 10 10")
        if node.attrib.get("refX") != "9" or node.attrib.get("refY") != "5":
            marker_failures.append(f"{marker_id}: marker ref point is not 9,5")
        paths = marker_paths(node)
        if not paths:
            marker_failures.append(f"{marker_id}: marker has no path")
        elif normalized_path(paths[0].attrib.get("d")) != "M 0 0 L 10 5 L 0 10 Z":
            marker_failures.append(f"{marker_id}: marker path is not the established filled triangle")
    if marker_count < 1:
        failures.append("missing sequence arrow markers")
    failures.extend(marker_failures)

    text = text_content(root).lower()
    declares_branch = any(word in text for word in ("alt ", "else ", "loop "))
    branch_regions = count_by_class(root, ALT_RECT_CLASSES, "rect") + count_by_class(root, BRANCH_DIVIDER_CLASSES)
    if declares_branch and branch_regions < 1:
        failures.append("declares alt/else/loop text but lacks best-practices branch region styling")
    for region in nodes_by_class(root, ALT_RECT_CLASSES, "rect"):
        fill = attr_value(region, "fill")
        fill_opacity = attr_value(region, "fill-opacity")
        if fill and fill not in {"none", "transparent"}:
            try:
                opacity = float(fill_opacity) if fill_opacity is not None else 1.0
            except ValueError:
                opacity = 1.0
            if opacity > 0.16:
                failures.append("alt/else/loop region uses a solid fill instead of subdued outline styling")
    failures.extend(branch_color_failures(root))

    return [f"{path}: {failure}" for failure in failures]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("svg", nargs="+", type=Path)
    args = parser.parse_args()

    failures: list[str] = []
    checked = 0
    for svg in args.svg:
        root = ET.parse(svg).getroot()
        if is_sequence(svg, root):
            checked += 1
        failures.extend(audit_file(svg))

    if failures:
        print("diagram sequence style audit: FAIL", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print(f"diagram sequence style audit: PASS sequence_files={checked}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
