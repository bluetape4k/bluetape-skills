from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT = next(
    path
    for path in (
        SKILL_ROOT / "scripts" / "diagram-semantic-audit.py",
        SKILL_ROOT / "scripts" / "executable_diagram-semantic-audit.py",
    )
    if path.exists()
)


def ledger(**overrides: object) -> dict[str, object]:
    value: dict[str, object] = {
        "kind": "workflow",
        "source": {
            "question": "How does repeat execution reach its final report?",
            "revision": "abc123",
            "paths": ["docs/manual/en/modules/workflow.md"],
        },
        "nodes": [
            {"id": "start", "label": "Repeat flow starts", "source": "workflow.md"},
            {"id": "work", "label": "Execute work", "source": "workflow.md"},
            {"id": "stop", "label": "Stop guard", "source": "workflow.md"},
        ],
        "edges": [
            {"id": "start-work", "from": "start", "to": "work", "kind": "flow", "source": "workflow.md"},
            {"id": "work-stop", "from": "work", "to": "stop", "kind": "branch", "source": "workflow.md"},
        ],
    }
    value.update(overrides)
    return value


class DiagramSemanticAuditTest(unittest.TestCase):
    def run_audit(self, payload: dict[str, object], *extra: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(AUDIT), *extra, str(path)],
                text=True,
                capture_output=True,
                check=False,
            )

    def test_valid_ledger_passes_with_machine_readable_counts(self) -> None:
        result = self.run_audit(ledger(), "--json")

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["ok"])
        self.assertEqual("workflow", report["kind"])
        self.assertEqual(3, report["counts"]["nodes"])
        self.assertEqual(2, report["counts"]["edges"])
        self.assertEqual([], report["diagnostics"])

    def test_missing_source_question_fails_closed(self) -> None:
        payload = ledger(source={"revision": "abc123", "paths": ["workflow.md"]})

        result = self.run_audit(payload)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("SEM-SOURCE-QUESTION", result.stdout)

    def test_unknown_edge_endpoint_is_rejected(self) -> None:
        payload = ledger(
            edges=[
                {
                    "id": "bad",
                    "from": "work",
                    "to": "missing",
                    "kind": "flow",
                    "source": "workflow.md",
                }
            ]
        )

        result = self.run_audit(payload)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("SEM-EDGE-ENDPOINT", result.stdout)

    def test_complexity_budget_suggests_split_without_shortening_labels(self) -> None:
        payload = ledger(
            nodes=[
                {"id": f"n{index}", "label": f"Technical component {index}", "source": "workflow.md"}
                for index in range(12)
            ],
            edges=[],
        )

        result = self.run_audit(payload)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("SEM-BUDGET-NODES", result.stdout)
        self.assertIn("split", result.stdout.lower())

    def test_duplicate_ids_and_missing_node_source_are_reported_together(self) -> None:
        payload = ledger(
            nodes=[
                {"id": "same", "label": "A", "source": "workflow.md"},
                {"id": "same", "label": "B"},
            ]
        )

        result = self.run_audit(payload)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("SEM-NODE-ID", result.stdout)
        self.assertIn("SEM-NODE-SOURCE", result.stdout)

    def test_repair_receipt_requires_positive_touch_count(self) -> None:
        payload = ledger(
            repairs=[
                {"target": "context", "reason": "move label outside work card", "touches": 0}
            ]
        )

        result = self.run_audit(payload)

        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertIn("SEM-REPAIR-TOUCHES", result.stdout)


if __name__ == "__main__":
    unittest.main()
