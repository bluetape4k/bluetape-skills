#!/usr/bin/env python3
"""Audit SVG/PNG pairs and README exposure for diagram asset directories."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

MARKDOWN_IMAGE = re.compile(r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))")
HTML_IMAGE = re.compile(r"<img\b[^>]*?\bsrc\s*=\s*(['\"])(.*?)\1", re.IGNORECASE | re.DOTALL)
MERMAID_FENCE = re.compile(r"```\s*mermaid\b", re.IGNORECASE)
GRAPHVIZ_RESIDUE = re.compile(r"```\s*(?:dot|graphviz)\b|\bdigraph\b|\bdot\s+-T(?:svg|png)\b", re.IGNORECASE)
REMOTE_SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.-]*:)?//", re.IGNORECASE)


def relative_stem(path: Path, root: Path) -> str:
    return str(path.relative_to(root).with_suffix(""))


def scan_asset_dirs(asset_dirs: list[Path]) -> dict[str, object]:
    failures: list[str] = []
    svg_stems: set[str] = set()
    png_stems: set[str] = set()
    svg_count = 0
    png_count = 0
    for asset_dir in asset_dirs:
        if not asset_dir.is_dir():
            failures.append(f"asset directory missing: {asset_dir}")
            continue
        for path in asset_dir.rglob("*"):
            if not path.is_file():
                continue
            suffix = path.suffix.lower()
            if suffix == ".svg":
                svg_count += 1
                svg_stems.add(relative_stem(path, asset_dir))
            elif suffix == ".png":
                png_count += 1
                png_stems.add(relative_stem(path, asset_dir))
    missing_png = sorted(svg_stems - png_stems)
    missing_svg = sorted(png_stems - svg_stems)
    if not svg_count and not png_count:
        failures.append("no SVG/PNG assets found")
    failures.extend(f"missing PNG pair: {stem}.png" for stem in missing_png)
    failures.extend(f"missing SVG pair: {stem}.svg" for stem in missing_svg)
    return {
        "asset_dirs": [str(path) for path in asset_dirs],
        "svg_count": svg_count,
        "png_count": png_count,
        "pair_count": len(svg_stems & png_stems),
        "missing_png": missing_png,
        "missing_svg": missing_svg,
        "failures": failures,
    }


def local_image_refs(readme: Path) -> list[str]:
    text = readme.read_text(encoding="utf-8")
    refs = [match.group(1) or match.group(2) for match in MARKDOWN_IMAGE.finditer(text)]
    refs.extend(match.group(2) for match in HTML_IMAGE.finditer(text))
    return [ref.strip() for ref in refs if ref and ref.strip()]


def scan_readmes(readmes: list[Path], require_all_referenced: bool) -> dict[str, object]:
    failures: list[str] = []
    missing_refs: list[str] = []
    svg_refs: list[str] = []
    mermaid_files: list[str] = []
    graphviz_files: list[str] = []
    duplicate_refs: dict[str, int] = {}
    png_refs: set[str] = set()
    for readme in readmes:
        if not readme.is_file():
            failures.append(f"README missing: {readme}")
            continue
        text = readme.read_text(encoding="utf-8")
        if MERMAID_FENCE.search(text):
            mermaid_files.append(str(readme))
        if GRAPHVIZ_RESIDUE.search(text):
            graphviz_files.append(str(readme))
        refs = local_image_refs(readme)
        counts = Counter(refs)
        duplicate_refs.update({f"{readme}:{ref}": count for ref, count in counts.items() if count > 1})
        for ref in refs:
            parsed = urlsplit(ref)
            if parsed.scheme or REMOTE_SCHEME.match(ref) or ref.startswith("#"):
                continue
            clean_ref = ref.split("#", 1)[0].split("?", 1)[0]
            target = (readme.parent / clean_ref).resolve()
            if not target.is_file():
                missing_refs.append(f"{readme}: {ref}")
                continue
            if target.suffix.lower() == ".svg":
                svg_refs.append(f"{readme}: {ref}")
            elif target.suffix.lower() == ".png":
                png_refs.add(str(target))
    if missing_refs:
        failures.extend(f"missing README image: {item}" for item in missing_refs)
    failures.extend(f"README embeds SVG: {item}" for item in svg_refs)
    failures.extend(f"README contains Mermaid residue: {item}" for item in mermaid_files)
    failures.extend(f"README contains Graphviz residue: {item}" for item in graphviz_files)
    return {
        "readmes": [str(path) for path in readmes],
        "readme_count": len(readmes),
        "png_refs": sorted(png_refs),
        "png_ref_count": len(png_refs),
        "missing_refs": missing_refs,
        "svg_refs": svg_refs,
        "mermaid_files": mermaid_files,
        "graphviz_files": graphviz_files,
        "duplicate_refs": duplicate_refs,
        "failures": failures,
        "require_all_referenced": require_all_referenced,
    }


def add_unreferenced_png_failures(report: dict[str, object], readme_report: dict[str, object]) -> None:
    if not readme_report["require_all_referenced"]:
        return
    referenced = set(readme_report["png_refs"])
    for asset_dir in report["asset_dirs"]:
        root = Path(asset_dir)
        for png in root.rglob("*.png"):
            if str(png.resolve()) not in referenced:
                report["failures"].append(f"PNG is not exposed by a README: {png}")


def format_report(report: dict[str, object]) -> str:
    readme_report = report["readme"]
    summary = (
        f"asset-pair audit: {'PASS' if report['ok'] else 'FAIL'} dirs={len(report['asset_dirs'])} "
        f"svgs={report['svg_count']} pngs={report['png_count']} pairs={report['pair_count']} "
        f"missing_svg={len(report['missing_svg'])} missing_png={len(report['missing_png'])} "
        f"readmes={readme_report['readme_count']} png_refs={readme_report['png_ref_count']} "
        f"svg_refs={len(readme_report['svg_refs'])} duplicates={len(readme_report['duplicate_refs'])}"
    )
    if report["failures"]:
        summary += " failures=" + "; ".join(str(item) for item in report["failures"])
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SVG/PNG diagram pairs and README image exposure.")
    parser.add_argument("--asset-dir", action="append", type=Path, required=True)
    parser.add_argument("--readme", action="append", type=Path, default=[])
    parser.add_argument("--require-all-referenced", action="store_true")
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    report = scan_asset_dirs(args.asset_dir)
    readme_report = scan_readmes(args.readme, args.require_all_referenced)
    report["readme"] = readme_report
    report["failures"].extend(readme_report["failures"])
    add_unreferenced_png_failures(report, readme_report)
    report["ok"] = not report["failures"]
    if args.as_json:
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
    else:
        print(format_report(report))
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
