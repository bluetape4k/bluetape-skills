---
name: bluetape-bugfix
description: Use when a bluetape ecosystem task is a reproducible defect, failed test, regression, static-analysis defect, or review finding that needs a root-cause-driven Type C fix.
---

# bluetape4k Bug Fix

## Parent Contract

Use `bluetape-workflow` first for Type C classification, first-plan approval,
Action/Expected DoD/Step DoD reporting, concurrency-test policy, GitHub metadata,
PR-body final-section rules, and side-effect authority. This skill adds only the
bug-fix lifecycle. Load the language pattern skill matching the changed code:

- Kotlin: `bluetape-kotlin-patterns`
- Go: `bluetape-go-patterns`
- Rust: `bluetape-rs-patterns`
- Python: `bluetape-py-patterns`

Do not use this lane for a feature disguised as a fix. Split unrelated cleanup
or newly discovered defects into separate issues.

## Required Evidence

Before editing, establish:

1. failing test, minimal reproduction, stack trace, static-analysis finding, or
   exact incorrect behavior;
2. impacted symbols/callers and the expected contract;
3. root-cause hypothesis that explains the evidence;
4. narrow fix scope and regression-test shape;
5. current GitHub issue metadata when an issue already exists.

For Kotlin symbols, inspect references/impact before editing when code-intel is
available. For all languages, use `systematic-debugging` before proposing the
fix and `test-driven-development` to make the reproduction fail first.

## Pipeline

Apply `bluetape-workflow/references/checklist-contract.md`. The pipeline
sections explain execution; the following checklist is the blocking state.

- [ ] **C-01 — Prove the defect and root cause**
  - **Action:** Load systematic debugging, reproduce the smallest deterministic failure, inspect impacted symbols/callers, and trace the first incorrect assumption.
  - **Evidence:** Exact failing command or artifact, expected contract, impacted scope, severity, and a root-cause hypothesis that explains all observed evidence.
  - **Failure:** Stop before editing; do not substitute a symptom or retry pass for root-cause proof.
- [ ] **C-02 — Confirm scope and issue gate**
  - **Action:** Define the surgical fix and regression-test shape; when issue work is authorized, create or refresh one focused issue and verify its live metadata.
  - **Evidence:** Approved narrow scope plus issue URL/assignee/labels/milestone, or concrete evidence that issue mutation is outside scope.
  - **Failure:** Split features, cleanup, or unrelated defects; keep external issue mutation blocked without authority.
- [ ] **C-03 — Lock the regression RED**
  - **Action:** Add the smallest test that reproduces the established root cause using project helpers and the existing API/exception contract.
  - **Evidence:** Fresh RED output failing for the intended behavioral reason rather than compilation or fixture setup.
  - **Failure:** Repair the reproduction before implementing the fix.
- [ ] **C-04 — Apply the surgical fix**
  - **Action:** Change only what repairs the root cause, follow the language skill, avoid new dependencies and opportunistic refactoring, and clear diagnostics.
  - **Evidence:** Minimal scoped diff mapped directly to the root cause with diagnostics/formatting clean.
  - **Failure:** Revert or split unrelated changes; reclassify if the fix requires a broader product/API decision.
- [ ] **C-05 — Prove GREEN and blast radius**
  - **Action:** Run the regression test, affected tests, compile/typecheck/lint/static analysis, proportional broader tests, and triggered race/cancellation/resource checks in dependency order.
  - **Evidence:** Fresh passing commands plus investigation of any retry-only or lifecycle-sensitive failure.
  - **Failure:** Return to diagnosis or implementation and rerun the complete affected proof sequence.
- [ ] **C-06 — Capture reusable learning when applicable**
  - **Action:** Write and index a lesson when the defect exposes a reusable rule, repeated failure mode, or workflow gap.
  - **Evidence:** Lesson path and indexing result, or concrete scope evidence proving a trivial-defect N/A.
  - **Failure:** Do not use an unexplained N/A or leave a required lesson untracked.
- [ ] **C-07 — Complete PR, review, and CI gates when authorized**
  - **Action:** Link and verify the PR, converge code review to P0/P1=0, resolve current threads, and wait for required CI evidence before any approved merge.
  - **Evidence:** Live issue/PR metadata and final `## DoD Status`, review convergence, and successful required checks; or concrete evidence delivery is outside scope.
  - **Failure:** Keep delivery blocked; pending, stale, missing, or unexplained skipped evidence is not PASS.
- [ ] **C-08 — Report the bug-fix DoD**
  - **Action:** Render all Type C rows with reproduction, root cause, RED/GREEN, files/commits, validation, lifecycle risk, lesson, delivery state, and remaining risk.
  - **Evidence:** `Required checks: X/Y; N/A: N; Blocked: 0` with X=Y and concrete evidence for every checked row.
  - **Failure:** Do not claim fixed or merged; identify the unchecked row and next repair action.

### 1. Diagnose

- Reproduce the failure with the smallest deterministic command.
- Trace data/control/resource lifecycle to the first incorrect assumption.
- Distinguish root cause from downstream symptoms.
- Record affected files, public contract, severity, and blast radius.
- If the issue is intermittent, capture timing/resource/lifecycle evidence; a
  retry pass alone is not proof that it is harmless.

### 2. Issue Gate

After parent plan approval and only when issue creation is in scope, create or
refresh one focused issue with summary, reproduction, root cause, fix plan,
assignee `debop`, precise labels, and milestone. Verify the live metadata.

Use `bug` for incorrect runtime behavior/regression, `testing` for an isolated
test infrastructure defect, and a precise domain label when available. Do not
mislabel readability-only cleanup as a bug.

### 3. Regression Test

- Add the smallest test that fails for the established root cause.
- Preserve the existing exception/API contract unless the issue explicitly
  changes it.
- Use project test helpers before ad hoc concurrency or infrastructure setup.
- Confirm RED for the intended reason, not compilation or fixture failure.

### 4. Surgical Fix

- Change only what is required to repair the root cause.
- Prefer existing utilities and patterns; do not add dependencies for a fix
  unless explicitly approved.
- Do not mix opportunistic refactoring into the patch.
- Run diagnostics/formatting required by the language skill before tests.

### 5. Verification

Run in dependency order:

1. the new regression test;
2. affected module/package tests;
3. lint/static analysis and compile/typecheck;
4. broader workspace tests proportional to blast radius;
5. race/cancellation/resource-lifecycle checks when the defect touches them.

Run Testcontainers, real DB, native/JNI, and similar heavyweight checks
sequentially. If a failure passes on retry, investigate the lifecycle risk and
record the conclusion.

### 6. Durable Learning

Create `docs/lessons/YYYY-MM-DD-{slug}.md` only when the defect exposes a
reusable project rule, repeated failure mode, or workflow gap. Include context,
root cause, decision, verification, and future-agent guidance. Reindex GNO when
the lesson is created. A trivial one-line defect may report `N/A` only with
concrete scope evidence proving that no reusable learning exists.

### 7. PR and Review

When PR creation is approved:

- link the issue with `Fixes #N`;
- mirror issue assignee, milestone, and relevant labels;
- explain root cause, fix, regression evidence, and remaining risk;
- end the body with `## DoD Status` using the central template;
- verify the live body and metadata with `gh pr view`.

Run a code-reviewer pass on the final diff. Do not enter the CI gate until P0/P1
is zero and actionable feedback is resolved or explicitly deferred with reason.

### 8. CI and Merge Gate

Inspect required checks and the latest review threads. `SUCCESS` passes;
`PENDING` waits; `FAILURE` returns to diagnosis. A `SKIPPED` required check is
not PASS: repair its trigger or record an evidence-backed `N/A` only when the
checklist contract proves the check inapplicable. New review feedback reopens
the gate. Merge only when the user explicitly requested merge or the
already-approved workflow includes it.

## Language-Specific Risk Checks

### Kotlin

- cancellation rethrow and structured concurrency
- Exposed operator/receiver correctness
- caller-validation exception type
- Spring conditional auto-configuration boundaries
- JUnit 5 and bluetape4k test helpers

### Go

- `context.Context` cancellation/deadline/retry contract
- goroutine, timer, body, rows, and container cleanup
- `errors.Is`/`errors.As`-compatible wrapping
- table-driven failure tests and `go test -race` when applicable

### Rust

- ownership/lifetime/API shape and typed error source chain
- panic-free caller-input handling
- async cancellation, shutdown, and resource cleanup
- feature-additivity plus fmt/test/clippy evidence

### Python

- async cancellation/resource cleanup
- exception chaining and stable public behavior
- deterministic tests and packaging/typecheck evidence

## Stop Conditions

Stop with `BLOCKED` rather than guessing when reproduction is not trustworthy,
the root cause remains unproven, required infrastructure is unavailable, or the
fix requires a materially broader product/API decision. Otherwise continue the
fix-test-review loop until all required evidence is PASS.

## Final DoD Additions

The parent final report must include: reproduction, root cause, impacted scope,
regression test RED/GREEN evidence, fix commit/files, targeted and broader test
commands, lifecycle/race checks when relevant, lesson path or evidence-backed N/A,
issue/PR metadata, review P0/P1 count, CI evidence, and remaining risks.
