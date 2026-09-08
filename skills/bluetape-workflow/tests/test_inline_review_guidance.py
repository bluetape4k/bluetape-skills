"""Regression guards for the workspace-approved code-review fallback."""

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class InlineReviewGuidanceTest(unittest.TestCase):
    def test_unavailable_code_review_has_automatic_inline_fallback(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("## Independent Code Review Fallback", text)
        self.assertIn("without requesting fallback approval again", text)
        for trigger in ("spawn failure", "thread limit", "timeout", "no usable verdict"):
            self.assertIn(trigger, text)

    def test_fallback_keeps_provenance_and_quality_gates(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        for boundary in (
            "not independent attestation",
            "exact current head and diff",
            "file:line findings",
            "P0/P1 findings are not execution failures",
            "separately required architecture review",
            "fresh exact-head merge approval",
            "takes precedence over conflicting leaf-skill",
        ):
            self.assertIn(boundary, text)

    def test_delivery_and_liveness_reference_the_canonical_fallback(self):
        for relative in ("references/common-gates.md", "references/liveness-contract.md"):
            text = (ROOT / relative).read_text(encoding="utf-8")
            self.assertIn("Independent Code Review Fallback", text)


if __name__ == "__main__":
    unittest.main()
