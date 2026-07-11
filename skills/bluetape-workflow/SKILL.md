---
name: bluetape-workflow
description: Use when any task in a bluetape4k repository must be classified and routed to Type A full feature, B fast track, C bug fix, D review, E maintenance, P publish, or F benchmark self-improvement.
---

# bluetape4k Workflow Router

This is the first-stop router for every bluetape ecosystem repository. It owns
classification, the first-plan approval gate, step progression, and final DoD
evidence. Leaf skills own execution detail.

## Mandatory Router Checklist

**REQUIRED:** Read `references/checklist-contract.md` before creating any task
checklist. An unchecked required item blocks every dependent item.

- [ ] **WF-01 — Classify**
  - **Action:** Perform read-only discovery and select Type A/B/C/D/E/P/F.
  - **Evidence:** type, signals, repository, scope, and exclusions.
  - **Failure:** stop; do not plan an execution lane from an ambiguous type.
- [ ] **WF-02 — Write the first concrete plan**
  - **Action:** Give every step an `Action` and `Expected DoD`.
  - **Evidence:** ordered plan shown to the user.
  - **Failure:** stop before mutation or durable artifacts.
- [ ] **WF-03 — Obtain first-plan approval**
  - **Action:** Wait for explicit approval of the first concrete plan.
  - **Evidence:** exact user approval in the active thread.
  - **Failure:** remain read-only.
- [ ] **WF-04 — Load execution contracts**
  - **Action:** Read the selected leaf skill, `references/common-gates.md`, and
    only triggered references before the first mutation.
  - **Evidence:** loaded skill/reference names.
  - **Failure:** stop before editing.
- [ ] **WF-05 — Execute gates in dependency order**
  - **Action:** Complete one checklist item and record fresh evidence before its
    dependent item starts.
  - **Evidence:** checked item plus command/file/URL/result.
  - **Failure:** mark FAIL/PENDING and block downstream.
- [ ] **WF-06 — Repair any skipped or weak gate**
  - **Action:** reconstruct the missing checklist item, rerun its proof, and report
    the repair before continuing.
  - **Evidence:** repaired item and fresh proof.
  - **Failure:** final status is BLOCKED, never DONE.

Type D review stays read-only unless the user explicitly expands scope. Type P
stable release/tag/publish actions still require their irreversible-action gate
even after plan approval.

## Phase 0 - Classify

Explicit user labels win. Otherwise choose the lightest safe type.

| Type | Use when | Canonical execution surface |
|---|---|---|
| A - Full Feature | New module/service/subsystem; new dependency; broad public API; architecture or multi-layer change; large refactor | `bluetape-full-feature` |
| B - Fast Track | Small additive feature or extension with local impact and no architectural decision | `bluetape-fast-track` |
| C - Bug Fix | Reproducible defect, regression, exception, incorrect output, or failing test | `bluetape-bugfix` |
| D - Code Review | Review, audit, investigation, or verdict with no implementation request | `code-review` plus the matching language pattern skill |
| E - Maintenance | README, KDoc, docs, AGENTS, workflow, skill, config, CI hygiene, plugin, or harness change without production behavior change | `bluetape-maintenance` |
| P - Publish | Snapshot, release, BOM/catalog train, tag, Maven Central, or GitHub Release | `bluetape-publish-jvm`; use `bluetape-publish-go` for Go releases |
| F - Self Improve | Explicit benchmark-measured optimization loop with baseline, target, and stop condition | `bluetape-self-improve` |

### Classification Rules

- Public API plus README in one bounded change remains Type B when the API is
  local and additive; README-only work is Type E.
- A bug plus unrelated feature is two workflows. Split the plan unless the
  user explicitly requires one delivery unit.
- A review request never becomes an implementation task implicitly.
- A benchmark request without a repeatable metric, baseline command, or stop
  condition is planning/discovery only; do not mutate code.
- New modules, new dependencies, multi-repository trains, and architecture
  decisions cannot be downgraded to Type B by calling them small.
- When signals conflict, select the higher-risk type and record the basis.

Use this checkpoint before the approval question:

```markdown
Work type: Type-{A/B/C/D/E/P/F} - {name}
Basis: {classification signals}
Planned steps: {ordered compact list}
N/A: {items plus concrete scope evidence proving inapplicability}
```

## Conditional Reference Loading

Load only what the current step needs:

| Trigger | Required reference or skill |
|---|---|
| Before creating any workflow checklist | `references/checklist-contract.md` |
| Before any approved mutation | `references/common-gates.md` |
| Before native subagent dispatch | `references/model-routing.md`; resolve models from current `AGENTS.md`/installed agent catalog |
| Module add/move/remove, workflow YAML, shared catalog, Kover, benchmark harness, broad backend matrix, HTTP/Testcontainers growth, or nightly closeout | `references/repository-hazards.md` |
| Kotlin implementation or Kotlin review verdict | `bluetape-kotlin-patterns` |
| Go implementation/review/release preflight | `bluetape-go-patterns` |
| Rust implementation/review/release preflight | `bluetape-rs-patterns` |
| Python implementation/review/release preflight | `bluetape-py-patterns` |
| Blog/article or Korean README prose | `bluetape-writer` |
| Diagram, chart, benchmark visual, or README visual asset | `bluetape-diagram` |
| User-facing final report | `templates/final-report-step-dod.md` |
| Issue-linked PR body | `templates/pr-body-step-dod.md`; `## DoD Status` must be the final `##` section |

If a required leaf skill is missing or unreadable, stop before mutation and
report the missing workflow surface. Do not silently reconstruct a large
workflow from memory.

## Type-Specific Minimum Routes

### Type A - Full Feature

Load `bluetape-full-feature` and follow its 0 -> 10 gate sequence. New module,
new dependency, broad API, and architectural work require spec and plan review.
P0/P1 must be zero before implementation and again before PR/merge progression.

### Type B - Fast Track

Load `bluetape-fast-track`. Keep the approved plan, targeted tests, relevant
language patterns, affected review lenses, P0/P1 convergence, documentation
parity, PR metadata, and CI evidence. Never merge automatically.

### Type C - Bug Fix

Load `bluetape-bugfix`. Reproduce first, identify root cause, lock the
regression with a failing test, make the smallest fix, run targeted validation,
and update affected docs. Do not convert a failed reproduction into speculative
editing.

### Type D - Code Review

Do not edit. Reopen the current diff/files and report findings first, ordered by
P0/P1/P2/P3 with file/line evidence. Use the smallest triggered lenses:

- standard: code correctness/API plus test evidence;
- security-sensitive, concurrency/async, DB, external IO, public API, or >=300
  changed lines: add the matching independent security, performance,
  stability/Ops, developer/API, or user/caller lenses;
- architecture or module-scale review: use all relevant lenses and a main
  integration verdict.

Independently verify plausible P0/P1 findings. Review completion means known
P0/P1 findings are resolved or the verdict is explicitly blocked; it never
means silently omitting blockers.

### Type E - Maintenance

Load `bluetape-maintenance`. Keep production behavior unchanged. Guidance,
skill, hook, helper, config, or Codex/OMX changes must update the managed source
first, apply live, prove source/live parity, run `$self-audit`, and commit/push
the durable source when persistence is requested.

### Type P - Publish

Load `bluetape-publish-go` for Go module releases; otherwise load
`bluetape-publish-jvm`. Refresh the release checklist before mutation and pin the
target version, latest observed external version, target authority, consumer
scope, topology, and dispatch-hold evidence. Ask before any stable dispatch,
tag creation/rewrite, release creation, publication, or milestone closure not
already explicitly requested.

### Type F - Self Improve

Load `bluetape-self-improve`. Require objective, primary metric, benchmark
command, fresh baseline, sealed files, threshold, and stop condition before an
experiment. One measurable hypothesis per candidate; integrate only a winner
that passes tests, sealed-file validation, and the benchmark acceptance rule.

## Step Progression and Review

- Run dependent tasks sequentially and independent read-only lanes in parallel
  only when that improves evidence quality.
- State lane count, write scope, heavy-command limit, and stop condition before
  delegation. The main session owns mutation, integration, and final verdict.
- Testcontainers, real DB, native, JNI, emulator, and other heavyweight tests
  run sequentially across modules, worktrees, and agents.
- P0/P1 blocks the next gate. P2/P3 becomes a follow-up by default unless the
  fix is small, in-scope, and cheap to revalidate.
- Re-read current PR reviews and threads after CI turns green; newer unresolved
  feedback reopens the merge gate.
- Merge, tag, publish, workflow dispatch, release creation, and destructive
  cleanup happen only when explicitly requested or already approved in the
  active workflow scope.

## Reporting Contract

Every required item is maintained as a checkbox during execution and gets one
final row. `SKIPPED` is not a status; use `N/A` only under the checklist
contract. Report `Required checks: {checked}/{total}; N/A: {count};
Blocked: {count}`.

| Check | Action | Status | Evidence | Failure / Next Action |
|---|---|---|---|---|
| {id} - {name} | action performed | PASS / FAIL / PENDING / N/A | fresh command/file/URL/result; N/A requires concrete scope evidence | none, repair, rollback, blocker, or next action |

Final reports include:

- classification and approval evidence;
- P0/P1 gate status;
- targeted validation and known gaps;
- changed files;
- issue/PR milestone, labels, assignee, and CI when applicable; any N/A row
  includes concrete scope evidence, not a prose-only reason;
- merge/local-sync state;
- final status: done, pending explicit boundary, or blocked.

For PRs, verify the live body with `gh pr view <number> --json body`. Fix it if
empty or if its final Markdown `##` heading is not `## DoD Status` before
commenting, reviewing, merging, or reporting completion.

## Stop Conditions

Stop when all required gates are PASS, no known P0/P1 remains, evidence is
fresh, managed/live state is reconciled where applicable, and no requested
side effect remains. Otherwise continue the current safe branch or report the
specific blocker and last passing gate.
