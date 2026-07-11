---
name: bluetape-fast-track
description: Use when a bluetape ecosystem change is a narrow Type B feature, API extension, test improvement, or small class addition that does not need full design artifacts.
---

# bluetape4k Fast Track

## Parent Contract

Use `bluetape-workflow` first for classification, first-plan approval, Step
DoD, common gates, GitHub metadata, concurrency tests, and side-effect authority.
This skill shortens artifacts, not verification. Load the language pattern skill
for every implementation/review:

- Kotlin: `bluetape-kotlin-patterns`
- Go: `bluetape-go-patterns`
- Rust: `bluetape-rs-patterns`
- Python: `bluetape-py-patterns`

## Type B Boundary

Use this lane only when the change:

- fits an existing module and architecture;
- has one clear approach and narrow blast radius;
- adds no new dependency or subsystem;
- does not require a broad public API/product decision;
- can be explained by an inline scope and task list.

Escalate to `bluetape-full-feature` before editing when it adds/moves/removes a
module, changes architecture, introduces a dependency, spans five or more
meaningfully coupled files, or exposes a public contract needing alternatives
and compatibility review.

## Mandatory Type B Checklist

Apply `bluetape-workflow/references/checklist-contract.md`. Complete these
items in order. An unchecked item blocks every dependent item.

- [ ] **B-01 — Confirm the Type B boundary**
  - **Action:** Inspect the repository, worktree, user changes, requested behavior, files/modules, exclusions, and risk; reclassify before editing if any Type B boundary is false.
  - **Evidence:** Safe branch/worktree, preserved dirty state, inline scope, acceptance criteria, exclusions, and explicit Type B classification.
  - **Failure:** Stop implementation and route to the correct workflow lane.
- [ ] **B-02 — Inspect existing patterns**
  - **Action:** Load the language pattern skill and inspect repository anchors; consult official documentation only for unfamiliar external APIs.
  - **Evidence:** Named skill and concrete source/test/config anchors that the change will follow.
  - **Failure:** Do not design or edit from recall; complete repository and reference discovery first.
- [ ] **B-03 — Prepare and review the lightweight design**
  - **Action:** Record one approach, contract, risks, and tests inline; create a spec or plan only when useful, and independently review every written artifact with material 7-Tier lenses.
  - **Evidence:** Inline contract and ordered task list, plus artifact paths and review result when created; P0/P1 findings are zero or a concrete evidence-backed N/A.
  - **Failure:** Repair the design/review gate or reclassify before implementation.
- [ ] **B-04 — Implement narrowly**
  - **Action:** Make the smallest pattern-aligned change inside the approved scope; simplify duplication or generated slop before verification.
  - **Evidence:** Scoped diff mapped to the accepted behavior and existing repository patterns.
  - **Failure:** Revert or split out-of-scope work; stop if the blast radius no longer fits Type B.
- [ ] **B-05 — Prove changed behavior**
  - **Action:** Run RED/GREEN for behavior changes, diagnostics/format/lint, targeted compile/tests, and cancellation/race/resource checks when those risks are touched.
  - **Evidence:** Fresh command outputs showing the regression test fails before the fix when applicable and all required targeted checks pass afterward.
  - **Failure:** Keep this item unchecked, diagnose the failure, and do not advance to final review.
- [ ] **B-06 — Review the final scope and blast radius**
  - **Action:** Review Tier 4/5 always, affected risk lenses, Tier 7 evidence, and README locale/KDoc/module/CI registration when affected.
  - **Evidence:** Final scoped-diff review with P0/P1 findings at zero and every conditional surface either verified or evidence-backed N/A.
  - **Failure:** Repair findings and rerun affected downstream proof before delivery.
- [ ] **B-07 — Capture durable learning when applicable**
  - **Action:** Record a concise lesson and reindex reusable knowledge when the change produced substantial reusable guidance.
  - **Evidence:** Lesson path and indexing result, or concrete scope evidence proving N/A.
  - **Failure:** Do not use a generic “not needed”; supply the artifact or valid N/A evidence.
- [ ] **B-08 — Complete delivery gates when authorized**
  - **Action:** Create or update the PR with linked issue metadata and final `## DoD Status`, review the live final diff and threads, and wait for required CI conclusions.
  - **Evidence:** Live PR metadata/body/review-thread evidence and required checks successful; or concrete evidence that PR delivery is outside the approved scope.
  - **Failure:** Keep delivery blocked; do not treat `SKIPPED`, pending, stale, or missing checks as success unless the parent contract explicitly proves an allowed N/A.
- [ ] **B-09 — Report completion**
  - **Action:** Render the parent final checklist report with every Type B row, counts, commands, commits, risks, and side-effect state.
  - **Evidence:** `Required checks: X/Y; N/A: N; Blocked: 0` with X=Y and concrete evidence for every checked row.
  - **Failure:** Do not claim completion; expose the unchecked or blocked row and its next repair action.

Written spec/plan artifacts trigger B-03 review evidence; omitting the artifact
is allowed only when the inline scope/task list is sufficient. Implementation
review is never optional.

## Verification Minimum

- diagnostics/format/lint for the touched language;
- regression test for new or changed behavior;
- targeted module/package compile and tests;
- cancellation/race/resource tests when that risk is touched;
- README locale/KDoc/module/CI registration checks when affected;
- `git diff --check` and final scoped-diff review.

Run heavyweight infrastructure checks sequentially. A flaky first failure needs
lifecycle/timing investigation before it can be classified as noise.

## Stop Conditions

Stop and reclassify when scope grows beyond Type B, a second architecture
approach becomes materially plausible, the test shape cannot prove the contract,
or review finds a broad compatibility/security/data-migration risk. Otherwise
continue through review and verification until required Step DoD rows pass.
