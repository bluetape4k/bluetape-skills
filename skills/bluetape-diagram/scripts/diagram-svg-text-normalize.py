#!/usr/bin/env python3
"""Normalize SVG text so CairoSVG and code diagrams render consistently.

The checker rejects two repository-wide failure modes:

* thick white text strokes combined with ``paint-order: stroke``; CairoSVG can
  paint the stroke over the fill and make lane or relationship labels vanish;
* explicitly marked source snippets without token-level color.

``--write`` removes only the hazardous text-halo declarations and wraps plain
code text in color-only ``tspan`` tokens. Coordinates and font metrics stay
unchanged, so the operation is suitable for mechanical SVG/PNG refreshes.
"""

from __future__ import annotations

import argparse
from html import escape, unescape
from pathlib import Path
import re
import sys


CSS_RULE_RE = re.compile(r"(?P<selector>[^{}]+)\{(?P<body>[^{}]*)\}")
CLASS_RE = re.compile(r"\bclass\s*=\s*(['\"])(?P<value>.*?)\1", re.DOTALL)
STYLE_RE = re.compile(r"<style\b[^>]*>(?P<body>.*?)</style>", re.DOTALL | re.I)
TEXT_RE = re.compile(
    r"(?P<open><text\b(?P<attrs>[^>]*)>)(?P<body>.*?)(?P<close></text>)",
    re.DOTALL | re.I,
)
TOKEN_RE = re.compile(
    r"(?P<comment>//.*|(?<!\w)#\s.*)$"
    r"|(?P<string>\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`[^`]*`)"
    r"|(?P<number>\b\d+(?:\.\d+)?\b)"
    r"|(?P<identifier>\b[A-Za-z_][A-Za-z0-9_]*\b)"
    r"|(?P<operator>->|=>|::|==|!=|<=|>=|\?:|[=+\-*/<>?:{}\[\](),.])",
    re.MULTILINE,
)
CODE_CLASSES = {"code", "sql", "snippet"}
TOKEN_CLASS_PREFIXES = ("syntax-",)
LEGACY_TOKEN_CLASSES = {
    "keyword",
    "kw",
    "type",
    "string",
    "str",
    "number",
    "num",
    "comment",
    "literal",
    "function",
    "fn",
    "operator",
    "punctuation",
    "warn",
    "fail",
}

KEYWORDS = {
    "abstract",
    "as",
    "async",
    "await",
    "break",
    "case",
    "catch",
    "chan",
    "class",
    "const",
    "continue",
    "data",
    "def",
    "defer",
    "do",
    "else",
    "enum",
    "except",
    "false",
    "finally",
    "fn",
    "for",
    "from",
    "func",
    "fun",
    "go",
    "if",
    "impl",
    "import",
    "in",
    "interface",
    "internal",
    "is",
    "lambda",
    "let",
    "map",
    "match",
    "mut",
    "new",
    "nil",
    "none",
    "null",
    "object",
    "open",
    "override",
    "package",
    "pass",
    "private",
    "protected",
    "pub",
    "public",
    "raise",
    "return",
    "sealed",
    "select",
    "static",
    "struct",
    "suspend",
    "this",
    "throw",
    "trait",
    "true",
    "try",
    "type",
    "val",
    "var",
    "when",
    "where",
    "while",
    "with",
    "yield",
    "select",
    "insert",
    "update",
    "delete",
    "from",
    "join",
    "on",
    "values",
    "into",
}

KNOWN_TYPES = {
    "Any",
    "Bool",
    "Boolean",
    "Byte",
    "Char",
    "Double",
    "Duration",
    "EntityID",
    "Error",
    "Float",
    "Flow",
    "Future",
    "Int",
    "Int32",
    "Int64",
    "List",
    "Long",
    "Map",
    "Nothing",
    "Option",
    "Result",
    "Set",
    "Short",
    "String",
    "Unit",
    "User",
    "Vec",
    "bool",
    "byte",
    "error",
    "f32",
    "f64",
    "float32",
    "float64",
    "i16",
    "i32",
    "i64",
    "i8",
    "int",
    "int32",
    "int64",
    "rune",
    "str",
    "string",
    "u16",
    "u32",
    "u64",
    "u8",
    "uint",
    "uint32",
    "uint64",
    "usize",
}

LIGHT_SYNTAX_COLORS = {
    "syntax-keyword": "#7E22CE",
    "syntax-type": "#0F766E",
    "syntax-function": "#1D4ED8",
    "syntax-string": "#B45309",
    "syntax-number": "#C2410C",
    "syntax-comment": "#64748B",
    "syntax-operator": "#BE123C",
}
DARK_SYNTAX_COLORS = {
    "syntax-keyword": "#C4B5FD",
    "syntax-type": "#5EEAD4",
    "syntax-function": "#93C5FD",
    "syntax-string": "#FCD34D",
    "syntax-number": "#FDBA74",
    "syntax-comment": "#94A3B8",
    "syntax-operator": "#FDA4AF",
}


def class_names(attributes: str) -> set[str]:
    match = CLASS_RE.search(attributes)
    return set(match.group("value").split()) if match else set()


def selector_classes(selector: str) -> set[str]:
    return set(re.findall(r"\.([A-Za-z_][\w-]*)", selector))


def attribute_value(attributes: str, name: str) -> str | None:
    match = re.search(
        rf"\b{re.escape(name)}\s*=\s*(['\"])(?P<value>.*?)\1",
        attributes,
        re.DOTALL | re.I,
    )
    return match.group("value") if match else None


def selector_matches_text(selector: str, attributes: str) -> bool:
    classes = class_names(attributes)
    element_id = attribute_value(attributes, "id")
    for branch in selector.split(","):
        terminal = re.split(r"[\s>+~]+", branch.strip())[-1]
        tag = re.match(r"([A-Za-z_][\w:-]*)", terminal)
        if tag and tag.group(1).lower().rsplit(":", 1)[-1] != "text":
            continue
        required_ids = set(re.findall(r"#([A-Za-z_][\w-]*)", terminal))
        if required_ids and element_id not in required_ids:
            continue
        required_classes = selector_classes(terminal)
        if required_classes and not required_classes.issubset(classes):
            continue
        if tag or required_ids or required_classes:
            return True
    return False


def declaration_entries(body: str) -> list[tuple[str, str, bool]]:
    entries: list[tuple[str, str, bool]] = []
    for part in body.split(";"):
        if ":" not in part:
            continue
        name, value = part.split(":", 1)
        important = bool(re.search(r"!important\s*$", value, re.I))
        clean_value = re.sub(r"\s*!important\s*$", "", value, flags=re.I).strip()
        entries.append((name.strip().lower(), clean_value, important))
    return entries


def effective_text_declarations(svg: str, attributes: str) -> dict[str, str]:
    winners: dict[str, tuple[tuple[int, int, int, int, int, int], str]] = {}

    def offer(
        name: str,
        value: str,
        important: bool,
        origin: int,
        specificity: tuple[int, int, int],
        order: int,
    ) -> None:
        priority = (int(important), origin, *specificity, order)
        current = winners.get(name)
        if current is None or priority >= current[0]:
            winners[name] = (priority, value)

    for name, value in presentation_declarations(attributes).items():
        offer(name, value, False, 0, (0, 0, 0), -1)

    order = 0
    for style in STYLE_RE.finditer(svg):
        for rule in CSS_RULE_RE.finditer(style.group("body")):
            for branch in rule.group("selector").split(","):
                if not selector_matches_text(branch, attributes):
                    continue
                specificity: tuple[int, int, int] = (
                    branch.count("#"),
                    len(selector_classes(branch))
                    + len(re.findall(r"\[[^]]+\]", branch)),
                    len(re.findall(r"(?:^|[\s>+~])text(?:$|[.#:\[])", branch, re.I)),
                )
                for name, value, important in declaration_entries(rule.group("body")):
                    offer(name, value, important, 1, specificity, order)
            order += 1

    for name, value, important in declaration_entries(
        attribute_value(attributes, "style") or ""
    ):
        offer(name, value, important, 2, (1, 0, 0), order)

    return {name: value for name, (_, value) in winners.items()}


def presentation_declarations(attributes: str) -> dict[str, str]:
    declarations: dict[str, str] = {}
    for name in ("stroke", "paint-order", "stroke-width", "stroke-linejoin"):
        attribute = re.search(
            rf"\b{re.escape(name)}\s*=\s*(['\"])(?P<value>.*?)\1",
            attributes,
            re.DOTALL | re.I,
        )
        if attribute:
            declarations[name] = attribute.group("value").strip()
    return declarations


def declaration_map(body: str) -> dict[str, str]:
    declarations: dict[str, str] = {}
    for part in body.split(";"):
        if ":" not in part:
            continue
        name, value = part.split(":", 1)
        declarations[name.strip().lower()] = value.strip()
    return declarations


def is_text_hazard_declarations(declarations: dict[str, str]) -> bool:
    stroke = declarations.get("stroke", "").lower()
    paint_order = declarations.get("paint-order", "").lower()
    try:
        stroke_width = float(
            re.match(r"[-+]?\d+(?:\.\d+)?", declarations.get("stroke-width", "0"))[0]
        )
    except (TypeError, ValueError):
        stroke_width = 0.0
    return (
        stroke in {"#fff", "#ffffff", "white"}
        and paint_order.startswith("stroke")
        and stroke_width >= 2.0
    )


def remove_hazardous_halo(body: str) -> str:
    kept: list[str] = []
    for part in body.split(";"):
        stripped = part.strip()
        if not stripped:
            continue
        name = stripped.split(":", 1)[0].strip().lower()
        if name in {"paint-order", "stroke", "stroke-width", "stroke-linejoin"}:
            continue
        kept.append(stripped)
    if not kept:
        return ""
    leading = " " if body.startswith(" ") else ""
    trailing = " " if body.endswith(" ") else ""
    return f"{leading}{'; '.join(kept)};{trailing}"


def remove_local_halo(attributes: str) -> str:
    style = re.search(
        r"\bstyle\s*=\s*(['\"])(?P<body>.*?)\1",
        attributes,
        re.DOTALL | re.I,
    )
    normalized = attributes
    if style:
        normalized_style = remove_hazardous_halo(style.group("body"))
        replacement = (
            f'style={style.group(1)}{normalized_style}{style.group(1)}'
            if normalized_style
            else ""
        )
        normalized = normalized[: style.start()] + replacement + normalized[style.end() :]
        if not replacement:
            normalized = re.sub(r"[ \t]{2,}", " ", normalized)
    for name in ("paint-order", "stroke", "stroke-width", "stroke-linejoin"):
        normalized = re.sub(
            rf"\s+{re.escape(name)}\s*=\s*(['\"]).*?\1",
            "",
            normalized,
            flags=re.DOTALL | re.I,
        )
    return normalized


def add_safe_text_override(attributes: str) -> str:
    safe = (
        "paint-order:normal!important;"
        "stroke:none!important;"
        "stroke-width:0!important;"
    )
    style = re.search(
        r"\bstyle\s*=\s*(['\"])(?P<body>.*?)\1",
        attributes,
        re.DOTALL | re.I,
    )
    if not style:
        return f'{attributes} style="{safe}"'
    body = style.group("body").rstrip()
    separator = "" if not body or body.endswith(";") else ";"
    replacement = f"style={style.group(1)}{body}{separator}{safe}{style.group(1)}"
    return attributes[: style.start()] + replacement + attributes[style.end() :]


def normalize_halos(svg: str) -> tuple[str, int]:
    hazards = 0

    def replace_text(match: re.Match[str]) -> str:
        nonlocal hazards
        attributes = match.group("attrs")
        effective = effective_text_declarations(svg, attributes)
        if not is_text_hazard_declarations(effective):
            return match.group(0)

        hazards += 1
        normalized_attributes = remove_local_halo(attributes)
        normalized_attributes = add_safe_text_override(normalized_attributes)
        return (
            f"<text{normalized_attributes}>"
            f"{match.group('body')}{match.group('close')}"
        )

    return TEXT_RE.sub(replace_text, svg), hazards


def token_classes_in_markup(body: str) -> set[str]:
    classes = set(re.findall(r"\bclass=['\"]([^'\"]+)['\"]", body))
    flattened = {name for group in classes for name in group.split()}
    return {
        name
        for name in flattened
        if name in LEGACY_TOKEN_CLASSES
        or any(name.startswith(prefix) for prefix in TOKEN_CLASS_PREFIXES)
    }


def has_token_markup(body: str) -> bool:
    return bool(token_classes_in_markup(body))


def token_classes_with_fill(svg: str) -> set[str]:
    defined: set[str] = set()
    for match in CSS_RULE_RE.finditer(svg):
        if "fill" not in declaration_map(match.group("body")):
            continue
        defined.update(selector_classes(match.group("selector")))
    return defined


def looks_like_code(attributes: str, classes: set[str], source: str) -> bool:
    explicit = re.search(r"\bdata-code-snippet\s*=", attributes, re.I) is not None
    if not explicit and not (classes & CODE_CLASSES):
        return False
    if explicit:
        return True
    lowered = source.lower()
    keyword_pattern = r"\b(?:" + "|".join(sorted(KEYWORDS)) + r")\b"
    return bool(
        re.search(keyword_pattern, lowered)
        or re.search(r"[={}\[\];]|->|=>|::", source)
        or re.search(r"\b[A-Za-z_][A-Za-z0-9_]*\s*\(", source)
        or re.search(r"(['\"`]).*\1", source)
    )


def classify_token(match: re.Match[str], source: str) -> str | None:
    kind = match.lastgroup
    token = match.group(0)
    if kind in {"comment", "string", "number", "operator"}:
        return f"syntax-{kind}"
    if kind != "identifier":
        return None
    lowered = token.lower()
    if lowered in KEYWORDS:
        return "syntax-keyword"
    if token in KNOWN_TYPES or token[:1].isupper():
        return "syntax-type"
    remainder = source[match.end() :]
    if re.match(r"\s*\(", remainder):
        return "syntax-function"
    return None


def highlight_code(source: str) -> tuple[str, int]:
    output: list[str] = []
    cursor = 0
    highlighted = 0
    for match in TOKEN_RE.finditer(source):
        css_class = classify_token(match, source)
        if css_class is None:
            continue
        output.append(escape(source[cursor : match.start()], quote=False))
        output.append(
            f'<tspan class="{css_class}">{escape(match.group(0), quote=False)}</tspan>'
        )
        cursor = match.end()
        highlighted += 1
    if highlighted == 0:
        return escape(source, quote=False), 0
    output.append(escape(source[cursor:], quote=False))
    return "".join(output), highlighted


def normalize_code(svg: str) -> tuple[str, int, int]:
    candidates = 0
    changed = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal candidates, changed
        classes = class_names(match.group("attrs"))
        body = match.group("body")
        if "<" in body or has_token_markup(body):
            return match.group(0)
        source = unescape(body)
        if not looks_like_code(match.group("attrs"), classes, source):
            return match.group(0)
        highlighted_body, token_count = highlight_code(source)
        if token_count == 0:
            return match.group(0)
        candidates += 1
        changed += 1
        return f'{match.group("open")}{highlighted_body}{match.group("close")}'

    return TEXT_RE.sub(replace, svg), candidates, changed


def count_plain_code(svg: str) -> int:
    count = 0
    defined_token_classes = token_classes_with_fill(svg)
    for match in TEXT_RE.finditer(svg):
        body = match.group("body")
        token_classes = token_classes_in_markup(body)
        if token_classes:
            if token_classes - defined_token_classes:
                count += 1
            continue
        if "<" in body:
            continue
        source = unescape(body)
        classes = class_names(match.group("attrs"))
        if not looks_like_code(match.group("attrs"), classes, source):
            continue
        _, token_count = highlight_code(source)
        if token_count:
            count += 1
    return count


def parse_hex_color(value: str) -> tuple[int, int, int] | None:
    match = re.fullmatch(r"#([0-9A-Fa-f]{6})", value.strip())
    if not match:
        return None
    digits = match.group(1)
    return tuple(int(digits[index : index + 2], 16) for index in (0, 2, 4))


def uses_dark_canvas(svg: str) -> bool:
    if re.search(r"\bdata-code-theme=['\"]dark['\"]", svg, re.I):
        return True
    match = re.search(r"\.canvas\s*\{([^{}]*)\}", svg, re.I)
    if not match:
        return False
    fill = declaration_map(match.group(1)).get("fill", "")
    rgb = parse_hex_color(fill)
    if rgb is None:
        return False
    red, green, blue = (channel / 255.0 for channel in rgb)
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    return luminance < 0.4


def inject_syntax_css(svg: str) -> str:
    used_classes = {
        css_class
        for match in TEXT_RE.finditer(svg)
        for css_class in token_classes_in_markup(match.group("body"))
        if css_class.startswith(TOKEN_CLASS_PREFIXES)
    }
    missing_classes = used_classes - token_classes_with_fill(svg)
    if not missing_classes:
        return svg
    colors = DARK_SYNTAX_COLORS if uses_dark_canvas(svg) else LIGHT_SYNTAX_COLORS
    css = "".join(
        f".{css_class}{{fill:{colors[css_class]}}}"
        for css_class in colors
        if css_class in missing_classes
    )
    if not css:
        return svg
    match = STYLE_RE.search(svg)
    if not match:
        root = re.search(r"<svg\b[^>]*>", svg, re.I)
        if not root:
            return svg
        return svg[: root.end()] + f"<style>{css}</style>" + svg[root.end() :]
    body = match.group("body").rstrip()
    separator = "\n    " if "\n" in body else ""
    replacement = f"<style{match.group(0).split('<style', 1)[1].split('>', 1)[0]}>{body}{separator}{css}</style>"
    return svg[: match.start()] + replacement + svg[match.end() :]


def expand_paths(inputs: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for item in inputs:
        if item.is_file():
            paths.append(item)
            continue
        if item.is_dir():
            candidates = (
                item.glob("*.svg")
                if item.name == "readme-diagrams"
                else item.rglob("*.svg")
            )
            paths.extend(
                path
                for path in candidates
                if not {".git", "build", ".gradle", "node_modules", "target"}
                & set(path.parts)
            )
            continue
        raise FileNotFoundError(item)
    return sorted(set(paths))


def process(path: Path, write: bool) -> tuple[int, int, int]:
    original = path.read_text(encoding="utf-8")
    halo_normalized, hazards = normalize_halos(original)
    plain_code = count_plain_code(halo_normalized)
    changed = 0
    normalized = halo_normalized
    if write and hazards:
        changed = 1
    if write:
        normalized, _, code_changes = normalize_code(normalized)
        with_syntax_css = inject_syntax_css(normalized)
        if code_changes or with_syntax_css != normalized:
            normalized = with_syntax_css
            changed = 1
        if normalized != original:
            path.write_text(normalized, encoding="utf-8")
    return hazards, plain_code, changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="normalize SVG files in place")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    try:
        paths = expand_paths(args.paths)
    except FileNotFoundError as exc:
        print(f"FAIL missing path: {exc}", file=sys.stderr)
        return 2

    total_hazards = 0
    total_plain_code = 0
    changed_files = 0
    for path in paths:
        try:
            hazards, plain_code, changed = process(path, args.write)
        except (OSError, UnicodeError) as exc:
            print(f"FAIL {path}: {exc}", file=sys.stderr)
            return 2
        total_hazards += hazards
        total_plain_code += plain_code
        changed_files += changed
        if hazards or plain_code:
            print(
                f"{path}: text_hazards={hazards} "
                f"code_without_highlight={plain_code} changed={changed if args.write else 0}"
            )

    print(
        f"SUMMARY files={len(paths)} text_hazards={total_hazards} "
        f"code_without_highlight={total_plain_code} changed={changed_files}"
    )
    if args.write:
        return 0
    return 1 if total_hazards or total_plain_code else 0


if __name__ == "__main__":
    raise SystemExit(main())
