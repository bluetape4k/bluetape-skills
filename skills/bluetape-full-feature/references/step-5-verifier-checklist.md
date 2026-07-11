# Step 5 Verifier Checklist

Use this reference during `bluetape-full-feature` Step 5 after implementation tests pass and before review gates begin.

## Purpose

Confirm that the implementation still matches the approved spec and plan. This gate is not a code review replacement; it checks delivery completeness, scope discipline, and evidence quality before Step 6-R.

## Inputs

- Approved spec under `docs/superpowers/specs/`.
- Approved plan under `docs/superpowers/plans/`.
- Current diff and changed files.
- Targeted compile/test output from Step 4-T.
- README, KDoc, CI, and docs updates when the public surface changed.

## Checklist

- [ ] **A-VER-01 — Map accepted requirements**
  - **Action:** Map every accepted spec requirement to implemented code, tests, or a documented approved non-goal.
  - **Evidence:** Requirement-to-file/test traceability table.
  - **Failure:** Return to implementation or reopen the spec before review.
- [ ] **A-VER-02 — Reconcile planned tasks**
  - **Action:** Mark every planned task complete, explicitly deferred with rationale, or removed through an approved scope change.
  - **Evidence:** Plan-task status with decision authority for every non-complete item.
  - **Failure:** Unexplained incomplete tasks block Step 6.
- [ ] **A-VER-03 — Protect scope discipline**
  - **Action:** Inspect the final diff for unrelated files, formatting churn, dependency changes, and generated artifacts.
  - **Evidence:** Changed-file review and scoped diff result.
  - **Failure:** Remove, split, or approve scope expansion before continuing.
- [ ] **A-VER-04 — Synchronize public documentation**
  - **Action:** Verify public API changes have English KDoc and applicable multilingual README/examples/diagrams.
  - **Evidence:** API-to-doc mapping or concrete source-backed N/A.
  - **Failure:** Repair public documentation drift before review.
- [ ] **A-VER-05 — Prove planned risks in tests**
  - **Action:** Verify new/changed tests cover the behavior, failure paths, compatibility, lifecycle, and concurrency risks named in the plan.
  - **Evidence:** Risk-to-test mapping and fresh targeted results.
  - **Failure:** Add or strengthen proof before Step 6.
- [ ] **A-VER-06 — Confirm fresh module evidence**
  - **Action:** Tie every validation result to the current diff and affected module/repository.
  - **Evidence:** Fresh commands, SHAs/working tree, modules, and results.
  - **Failure:** Rerun stale, mismatched, or incomplete validation.
- [ ] **A-VER-07 — Expose every known gap**
  - **Action:** Record gaps as blockers, durable follow-up issues, or explicit `Not-tested` notes with impact.
  - **Evidence:** Gap list, disposition, owner/issue when durable, and completion impact.
  - **Failure:** Hidden or generic gaps keep the verifier verdict blocked.

## Output

Report one of:

- `PASS`: spec and plan are satisfied with current evidence.
- `NEEDS FIX`: implementation or tests are incomplete; return to Step 4-T.
- `NEEDS REVIEW SCOPE`: requirements changed enough that the spec or plan must be updated before continuing.

Include concise evidence: changed files inspected, tests/compile commands run, and any remaining gaps.
