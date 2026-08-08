#!/usr/bin/env python3
"""Validate source-backed semantic ledgers before a diagram is rendered.

The ledger is intentionally renderer-neutral. It proves that a diagram has a
reader question, source anchors, unique entities, closed relationships, and a
kind-specific complexity budget. It does not replace SVG/PNG geometry audits
or full-size visual inspection.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SUPPORTED_KINDS = {
    "architecture",
    "class",
    "chart",
    "erd",
    "sequence",
    "state",
    "workflow",
}

DEFAULT_BUDGETS: dict[str, dict[str, int]] = {
    "architecture": {"nodes": 16, "edges": 20, "branches": 4, "loops": 2},
    "class": {"nodes": 14, "edges": 24, "branches": 4, "loops": 2},
    "chart": {"nodes": 20, "edges": 8, "branches": 0, "loops": 0},
    "erd": {"nodes": 14, "edges": 20, "branches": 4, "loops": 2},
    "sequence": {"nodes": 10, "edges": 18, "branches": 3, "loops": 2},
    "state": {"nodes": 10, "edges": 16, "branches": 4, "loops": 2},
    "workflow": {"nodes": 10, "edges": 14, "branches": 3, "loops": 1},
}


def diagnostic(code: str, message: str, **details: Any) -> dict[str, Any]:
    value: dict[str, Any] = {"code": code, "message": message}
    if details:
        value["details"] = details
    return value


def non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def positive_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def validate(payload: Any, repo_root: Path | None = None) -> dict[str, Any]:
    diagnostics: list[dict[str, Any]] = []

    if not isinstance(payload, dict):
        return {
            "ok": False,
            "kind": None,
            "counts": {},
            "budget": {},
            "diagnostics": [
                diagnostic("SEM-ROOT", "ledger root must be a JSON object")
            ],
        }

    kind = payload.get("kind")
    if kind not in SUPPORTED_KINDS:
        diagnostics.append(
            diagnostic(
                "SEM-KIND",
                f"kind must be one of {', '.join(sorted(SUPPORTED_KINDS))}",
                value=kind,
            )
        )
        kind = str(kind) if isinstance(kind, str) else None

    source = payload.get("source")
    if not isinstance(source, dict):
        diagnostics.append(
            diagnostic("SEM-SOURCE", "source must contain question, revision, and paths")
        )
        source = {}

    if not non_empty_string(source.get("question")):
        diagnostics.append(
            diagnostic("SEM-SOURCE-QUESTION", "source.question must be non-empty")
        )
    if not non_empty_string(source.get("revision")):
        diagnostics.append(
            diagnostic("SEM-SOURCE-REVISION", "source.revision must be non-empty")
        )

    source_paths = source.get("paths")
    if not isinstance(source_paths, list) or not source_paths or not all(
        non_empty_string(path) for path in source_paths
    ):
        diagnostics.append(
            diagnostic("SEM-SOURCE-PATHS", "source.paths must contain at least one path")
        )
        source_paths = []
    elif repo_root is not None:
        for path in source_paths:
            resolved = repo_root / path
            if not resolved.is_file():
                diagnostics.append(
                    diagnostic(
                        "SEM-SOURCE-PATH",
                        f"source path does not exist: {path}",
                        path=path,
                    )
                )

    nodes = payload.get("nodes")
    if not isinstance(nodes, list):
        diagnostics.append(diagnostic("SEM-NODES", "nodes must be a JSON array"))
        nodes = []

    node_ids: set[str] = set()
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            diagnostics.append(
                diagnostic("SEM-NODE", f"nodes[{index}] must be an object", index=index)
            )
            continue
        node_id = node.get("id")
        if not non_empty_string(node_id):
            diagnostics.append(
                diagnostic("SEM-NODE-ID", f"nodes[{index}].id must be non-empty", index=index)
            )
        elif node_id in node_ids:
            diagnostics.append(
                diagnostic("SEM-NODE-ID", f"duplicate node id: {node_id}", id=node_id)
            )
        else:
            node_ids.add(node_id)
        if not non_empty_string(node.get("label")):
            diagnostics.append(
                diagnostic("SEM-NODE-LABEL", f"nodes[{index}].label must be non-empty", index=index)
            )
        if not non_empty_string(node.get("source")):
            diagnostics.append(
                diagnostic("SEM-NODE-SOURCE", f"nodes[{index}].source must be non-empty", index=index)
            )

    edges = payload.get("edges")
    if not isinstance(edges, list):
        diagnostics.append(diagnostic("SEM-EDGES", "edges must be a JSON array"))
        edges = []

    edge_ids: set[str] = set()
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            diagnostics.append(
                diagnostic("SEM-EDGE", f"edges[{index}] must be an object", index=index)
            )
            continue
        edge_id = edge.get("id")
        if not non_empty_string(edge_id):
            diagnostics.append(
                diagnostic("SEM-EDGE-ID", f"edges[{index}].id must be non-empty", index=index)
            )
        elif edge_id in edge_ids:
            diagnostics.append(
                diagnostic("SEM-EDGE-ID", f"duplicate edge id: {edge_id}", id=edge_id)
            )
        else:
            edge_ids.add(edge_id)

        source_id = edge.get("from")
        target_id = edge.get("to")
        if source_id not in node_ids or target_id not in node_ids:
            diagnostics.append(
                diagnostic(
                    "SEM-EDGE-ENDPOINT",
                    f"edge {edge_id or index} must reference declared node ids",
                    from_id=source_id,
                    to_id=target_id,
                )
            )
        if not non_empty_string(edge.get("kind")):
            diagnostics.append(
                diagnostic("SEM-EDGE-KIND", f"edges[{index}].kind must be non-empty", index=index)
            )
        if not non_empty_string(edge.get("source")):
            diagnostics.append(
                diagnostic("SEM-EDGE-SOURCE", f"edges[{index}].source must be non-empty", index=index)
            )

    behavior = payload.get("behavior", {})
    if not isinstance(behavior, dict):
        diagnostics.append(diagnostic("SEM-BEHAVIOR", "behavior must be an object when present"))
        behavior = {}

    branches = behavior.get("branches", 0)
    loops = behavior.get("loops", 0)
    for name, value in (("branches", branches), ("loops", loops)):
        if not non_negative_integer(value):
            diagnostics.append(
                diagnostic("SEM-BEHAVIOR-COUNT", f"behavior.{name} must be a non-negative integer")
            )

    budget = dict(DEFAULT_BUDGETS.get(kind or "", {}))
    custom_budget = payload.get("budget", {})
    if custom_budget is not None and not isinstance(custom_budget, dict):
        diagnostics.append(diagnostic("SEM-BUDGET", "budget must be an object when present"))
        custom_budget = {}
    if isinstance(custom_budget, dict):
        for name in budget:
            if name in custom_budget:
                value = custom_budget[name]
                if not positive_integer(value):
                    diagnostics.append(
                        diagnostic(
                            "SEM-BUDGET-VALUE",
                            f"budget.{name} must be a positive integer",
                        )
                    )
                else:
                    budget[name] = value

    counts = {
        "nodes": len(nodes),
        "edges": len(edges),
        "branches": branches if non_negative_integer(branches) else None,
        "loops": loops if non_negative_integer(loops) else None,
        "source_paths": len(source_paths),
    }
    if budget:
        for name, actual in (
            ("nodes", counts["nodes"]),
            ("edges", counts["edges"]),
            ("branches", counts["branches"]),
            ("loops", counts["loops"]),
        ):
            maximum = budget[name]
            if isinstance(actual, int) and actual > maximum:
                diagnostics.append(
                    diagnostic(
                        f"SEM-BUDGET-{name.upper()}",
                        f"{name}={actual} exceeds {kind} budget {maximum}; split the view or move detail to a subtitle/legend without shortening source identifiers",
                        actual=actual,
                        maximum=maximum,
                        repair="split-or-move-detail",
                    )
                )

    repairs = payload.get("repairs", [])
    if not isinstance(repairs, list):
        diagnostics.append(diagnostic("SEM-REPAIRS", "repairs must be an array when present"))
        repairs = []
    for index, repair in enumerate(repairs):
        if not isinstance(repair, dict):
            diagnostics.append(
                diagnostic("SEM-REPAIR", f"repairs[{index}] must be an object", index=index)
            )
            continue
        if not non_empty_string(repair.get("target")):
            diagnostics.append(
                diagnostic("SEM-REPAIR-TARGET", f"repairs[{index}].target must be non-empty", index=index)
            )
        if not non_empty_string(repair.get("reason")):
            diagnostics.append(
                diagnostic("SEM-REPAIR-REASON", f"repairs[{index}].reason must be non-empty", index=index)
            )
        if not positive_integer(repair.get("touches")):
            diagnostics.append(
                diagnostic("SEM-REPAIR-TOUCHES", f"repairs[{index}].touches must be a positive integer", index=index)
            )

    return {
        "ok": not diagnostics,
        "kind": kind,
        "counts": counts,
        "budget": budget,
        "diagnostics": diagnostics,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path, help="semantic ledger JSON file")
    parser.add_argument("--repo-root", type=Path, help="check source paths relative to this repository")
    parser.add_argument("--json", action="store_true", help="print a machine-readable report")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.ledger.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        report = {
            "ok": False,
            "kind": None,
            "counts": {},
            "budget": {},
            "diagnostics": [diagnostic("SEM-INPUT", str(error))],
        }
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"FAIL diagnostics=1 {error}")
        return 1

    report = validate(payload, args.repo_root)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "PASS" if report["ok"] else "FAIL"
        counts = report["counts"]
        print(
            f"{status} kind={report['kind']} nodes={counts.get('nodes', 0)} "
            f"edges={counts.get('edges', 0)} branches={counts.get('branches', 0)} "
            f"loops={counts.get('loops', 0)} diagnostics={len(report['diagnostics'])}"
        )
        for item in report["diagnostics"]:
            print(f"{item['code']}: {item['message']}")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
