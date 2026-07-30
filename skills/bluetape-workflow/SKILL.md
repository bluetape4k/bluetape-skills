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
- [ ] **WF-04A — Initialize machine-readable evidence when available**
  - **Action:** Initialize `scripts/bluetape-flow.py` with the current
    `CODEX_THREAD_ID`, repository root, workflow type, and components.
  - **Evidence:** run id, manifest hash, state root, and registered components.
  - **Failure:** remain on the documented checklist path and report the missing
    runtime surface; never write `.bluetape` files directly.
- [ ] **WF-05 — Execute gates in dependency order**
  - **Action:** Follow the physical row order in `common-gates.md` and the leaf;
    complete one item and record fresh evidence before its dependent starts.
  - **Evidence:** checked item plus command/file/URL/result.
  - **Failure:** mark FAIL/PENDING and block downstream.
- [ ] **WF-06 — Repair any skipped or weak gate**
  - **Action:** reconstruct the missing checklist item, rerun its proof, and report
    the repair before continuing.
  - **Evidence:** repaired item and fresh proof.
  - **Failure:** keep a recoverable wait/repair `PENDING`; use `BLOCKED` only
    when no safe continuation is available. Never report DONE.

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
| Before machine-readable run initialization | `references/workflow-manifest.json` and `references/topology-contract.md` |
| Before evaluating native sub-agent liveness | `references/liveness-contract.md` |
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

## Native Coordinator Boundary

Use `scripts/bluetape-flow.py` as the only writer for `.bluetape` run, lane,
heartbeat, report, and receipt state. Owner authority is a contained 0600
`--owner-file`; never pass or print its fencing value.

Python validates policy and records bounded receipts. It cannot invoke
`spawn_agent`, `send_message`, `list_agents`, `wait_agent`, or
`interrupt_agent`. The main session alone performs those native actions and
then records observed results. Follow `references/topology-contract.md` for
state transitions and `references/liveness-contract.md` for native-agent
lifecycle; do not duplicate those protocols here. A helper recommendation is
not execution evidence.

Before mutation, `mutation-check` must identify exactly one verified running
receipt bound to the current session and covering every target path. An empty
write scope is read-only. Collect `git status --porcelain=v1 -z` plus the branch
diff and validate canonical changed paths before `lane-complete`. Diagnose
corrupt receipt chains rather than truncating or continuing them. After
applying guidance, write a fresh-session handoff and validate it in a separate
Codex process.

## Type-Specific Minimum Routes

Load the canonical leaf and follow its type-specific gates. The router adds only
these invariants:

- Type D remains read-only and reports findings by severity with file/line
  evidence.
- Type C reproduces and locks a regression before the smallest fix.
- Type E preserves production behavior, reconciles managed source with live
  state, and runs `$self-audit`.
- Type P pins release authority and external version evidence before any
  irreversible action.
- Type F requires a repeatable baseline, acceptance threshold, and stop
  condition.
- Types A and B reach zero known P0/P1 findings before PR progression.

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
- Evaluate the lesson gate for every task before declaring merge-ready. Create
  the required committed lesson file when the selected workflow requires one,
  and create a durable lesson when the work produced reusable learning.
  Otherwise record an evidence-backed `N/A`; never create filler prose.
- Use the CG-11 through CG-18 PR path from `common-gates.md`; do not restate or
  weaken it in a leaf. CG-16 fresh merge approval is not transferable from plan
  or PR-creation approval. Non-PR irreversible actions use CG-X01.

## Reporting Contract

Use `references/checklist-contract.md` for status semantics and
`templates/final-report-step-dod.md` for output shape. `SKIPPED` is invalid.

Final reports include:

- classification and approval evidence;
- P0/P1 gate status;
- targeted validation and known gaps;
- changed files;
- issue/PR milestone, labels, assignee, and CI when applicable; any N/A row
  includes concrete scope evidence, not a prose-only reason;
- merge/local-sync state;
- final status: done, pending explicit boundary, or blocked.

For PRs, use `templates/pr-body-step-dod.md` and verify the live body before
reporting completion.

## Stop Conditions

Stop when all required gates are PASS, no known P0/P1 remains, evidence is
fresh, managed/live state is reconciled where applicable, and no requested
side effect remains. Otherwise continue the current safe branch or report the
specific blocker and last passing gate.
