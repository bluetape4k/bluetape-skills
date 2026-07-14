# Mandatory Checklist Contract

Use this contract for every bluetape workflow and leaf skill.

## Status Semantics

- `[ ]` means not proved. It blocks every dependent item but does not by itself
  mean failure.
- `[x]` means the required evidence was collected fresh and read.
- `PENDING` means the gate and target are valid but the workflow is waiting for
  user input or an external result. It blocks dependents while keeping the
  overall state `PENDING`, not `BLOCKED`.
- `FAIL` means an attempted proof failed and must be repaired before dependents
  run. `BLOCKED` means no safe repair or continuation is currently available.
- `UNKNOWN`, stale evidence, missing output, or agent assertion without local
  verification is `FAIL`, not a reason to continue.
- `SKIPPED` is forbidden. Use `N/A` only when the item is genuinely
  inapplicable and record concrete scope evidence proving why.
- Approval for a later action never retroactively checks an earlier gate.
- A successful later command never proves an earlier unchecked item.
- `Y` is every applicable required or conditional item instantiated for this
  task. `X` is the subset checked with PASS evidence. N/A items are excluded
  from both X and Y and counted separately; blocked/unchecked applicable items
  remain in Y.

## Required Item Shape

Every executable item uses this exact structure:

```markdown
- [ ] **{ID} — {gate}**
  - **Action:** {one concrete action}
  - **Evidence:** {required command output, file, URL, count, or decision}
  - **Failure:** {STOP, repair, rollback, or blocked handoff}
```

Do not combine independent proofs into one checkbox. A checkbox may be checked
only after its evidence has been produced and read in the current execution.

## Ordering Contract

- Executable rows must appear in dependency order. A later row may depend only
  on an earlier row; backward references are invalid.
- Every external side effect needs its own explicit row. Its authority must be
  established by an earlier row, and the action row must require fresh
  post-action read-back evidence; neither may be hidden in an unrelated row.
- Conditional branches must name their prerequisite, rejoin point, and N/A
  evidence. Document order remains authoritative inside each branch.
- Normal waiting at an approval, CI, review, or other external boundary is
  `PENDING`. Do not route around it or invoke repair solely because it waits.

## Execution Rules

- [ ] **CL-01 — Create before mutation**
  - **Action:** Instantiate the router, common, and leaf items before editing.
  - **Evidence:** checklist IDs and applicability recorded.
  - **Failure:** STOP; reconstruct before any further mutation.
- [ ] **CL-02 — Classify every item**
  - **Action:** Mark each item required, conditional, or N/A before execution.
  - **Evidence:** no unclassified checklist item.
  - **Failure:** treat the item as required and unchecked.
- [ ] **CL-03 — Respect dependency order**
  - **Action:** Execute rows top to bottom within the selected branch; enter a
    conditional branch only after its named prerequisite passes.
  - **Evidence:** document order, branch selection, and timestamps/results show
    prerequisites completed first with no backward jump.
  - **Failure:** stop and rerun affected downstream proof after repair.
- [ ] **CL-04 — Record evidence immediately**
  - **Action:** Attach evidence when checking the item.
  - **Evidence:** command/file/URL/count/result beside the item.
  - **Failure:** leave unchecked; late reconstruction is a repair, not normal flow.
- [ ] **CL-05 — Fail closed**
  - **Action:** Leave PENDING/failed items unchecked and block their downstream
    branch without converting a normal wait into failure.
  - **Evidence:** pending reason or failure plus stopped/rollback/repair state.
  - **Failure:** any continued dependent work is invalid and must be reverified.
- [ ] **CL-06 — Repair skipped or reordered work**
  - **Action:** repair the item and rerun every affected dependent proof.
  - **Evidence:** repair result and refreshed downstream results.
  - **Failure:** final status remains BLOCKED.
- [ ] **CL-07 — Refresh irreversible holds**
  - **Action:** reread from CL-01 and refresh every hold immediately before the
    external/irreversible action.
  - **Evidence:** current target/action/authority and fresh hold outputs.
  - **Failure:** do not execute the side effect.
- [ ] **CL-08 — Count before completion**
  - **Action:** report `Required checks: X/Y; N/A: N; Blocked: N` and all unchecked
    IDs.
  - **Evidence:** totals reconcile with the instantiated checklist using the X/Y
    denominator rule above.
  - **Failure:** completion claim is forbidden.

## Anti-Skip Red Flags

Stop when reasoning includes any of these:

- “CI/test success implies the earlier gate.”
- “The change is small/safe, so the checklist is administrative.”
- “The user said hurry, so evidence can be reconstructed later.”
- “The agent/reviewer said PASS, so local verification is unnecessary.”
- “N/A is obvious and needs no evidence.”
- “We can start downstream work while this gate is pending.”

All are failures of evidence, not efficiency improvements.
