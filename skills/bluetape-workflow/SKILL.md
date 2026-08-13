---
name: bluetape-workflow
description: Use when any task in a bluetape4k repository must be classified and routed to Type A full feature, B fast track, C bug fix, D review, E maintenance, P publish, or F benchmark self-improvement.
---

# bluetape4k Workflow Router

This is the first-stop router for every bluetape ecosystem repository. It owns
classification, the first-plan approval gate, step progression, and final DoD
evidence. Leaf skills own execution detail.

## AGENTS.md Guidance Hierarchy

Before classification, resolve and read every applicable `AGENTS.md` in this
order:

1. **User scope** — `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`.
2. **Workspace scope** — the nearest workspace-root `AGENTS.md`; for the
   bluetape4k workspace, use canonical `.github/docs/workspace/AGENTS.md` and
   verify the workspace-root copy or symlink.
3. **Repository/worktree scope** — every applicable repository or nested
   worktree `AGENTS.md` on the target path.

Apply all applicable instructions together. A narrower repository or worktree
file may add constraints but may not weaken a broader mandatory gate. Record
each path, scope, and read result in the checklist. In the bluetape4k
workspace, missing or unreadable user-scope, workspace, or repository guidance
blocks classification. Outside that workspace, mark a genuinely inapplicable
scope `N/A` with concrete path evidence; never assume an absent file was read.

When explaining this hierarchy in Korean, call governing guidance `기준 정보`
or `원본`; do not use the literal translation `권위`.

## Branch And Worktree Naming

When creating a branch or linked worktree, use a semantic prefix that matches
the change type, such as `feat/<slug>`, `fix/<slug>`, `docs/<slug>`,
`chore/<slug>`, or `refactor/<slug>`. Do not create `codex/<slug>` branches or
worktrees. Keep the branch and worktree names aligned with the same semantic
prefix wherever practical.

## Mandatory Router Checklist

**REQUIRED:** Read `references/checklist-contract.md` before creating any task
checklist. An unchecked required item blocks every dependent item.

- [ ] **WF-00 — Read the AGENTS.md hierarchy**
  - **Action:** Before classification, resolve and read the current user-scope,
    workspace, and target repository/worktree `AGENTS.md` files in order.
  - **Evidence:** Scope, path, read result, and applicable precedence recorded.
  - **Failure:** STOP before classification when any required guidance is
    missing or unreadable.
- [ ] **WF-01 — Classify**
  - **Action:** After the hierarchy gate passes, perform read-only discovery and
    select Type A/B/C/D/E/P/F.
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
  - **Action:** Resolve `bluetape-flow.py` using the Helper resolution contract,
    then initialize it with the current `CODEX_THREAD_ID`, repository root,
    workflow type, and components.
  - **Evidence:** run id, manifest hash, state root, and registered components.
  - **Failure:** remain on the documented checklist path and report the missing
    runtime surface; never write `.bluetape` files directly.

### Helper resolution contract

`bluetape-flow.py` is shipped with `$bluetape-workflow`; it is not normally a
repository-local script. Resolve the executable before runtime initialization
in this order:

1. `${CODEX_HOME:-$HOME/.codex}/skills/bluetape-workflow/scripts/bluetape-flow.py`
   — the live installed skill.
2. `$HOME/work/bluetape4k/bluetape-skills/skills/bluetape-workflow/scripts/bluetape-flow.py`
   — the workspace checkout of the public skill bundle.
3. `$HOME/.local/share/chezmoi/private_dot_codex/private_skills/bluetape-workflow/scripts/executable_bluetape-flow.py`
   — the managed source; inspect or update it through the source/apply chain,
   not as the live runtime path.
4. `<repo-root>/scripts/bluetape-flow.py` — only when the repository explicitly
   vendors the helper.

The workspace root `$HOME/work/bluetape4k/scripts` is not a canonical location
for the current bundle. Do not report the runtime surface as missing after
checking only the target repository. Record the resolved path and prove it with
`python3 <resolved-path> --help` or the read-only `state-root` command. Report
the runtime surface as missing only after every applicable candidate has been
checked.

### State-root selection contract

When `--state-root` is omitted, state discovery is scope-aware and follows this
order:

1. `BLUETAPE_STATE_ROOT`, when set;
2. the `.bluetape` directory at the current Git repository/worktree root;
3. the nearest ancestor `.bluetape` containing `config.json` for workspace-wide
   or non-Git paths;
4. `$HOME/work/bluetape4k/.bluetape` as the managed workspace fallback;
5. `$XDG_STATE_HOME/bluetape-skills` (or the platform default XDG state path).

Use a repository worktree's own `.bluetape` for repo-scoped work. Use the
workspace `.bluetape` for workspace-wide work started outside a Git worktree.
`bluetape-flow.py init` creates the selected missing state directory; never
write `.bluetape` files directly. An explicit `--state-root` is the supported
override when the task scope differs from the current working directory.
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
| Any Superpowers technical artifact: brainstorming/design discussion, specification/design, implementation plan, review, or lesson | `bluetape-writer`; complete `SPW-01`, `SPW-02`, `SPW-03`, `SPW-04`, and `SPW-05` for each new or materially revised artifact |
| Diagram, chart, benchmark visual, or README visual asset | `bluetape-diagram` |
| User-facing final report | `templates/final-report-step-dod.md` |
| Issue-linked PR body | `templates/pr-body-step-dod.md`; `## DoD Status` must be the final `##` section |

If a required leaf skill is missing or unreadable, stop before mutation and
report the missing workflow surface. Do not silently reconstruct a large
workflow from memory.

The Superpowers technical artifact route is a hard gate for transient
brainstorming/review prose as well as durable files. A language-policy reminder
or a generic editorial pass is not substitute evidence. A missing or unreadable
`bluetape-writer`, or any unchecked `SPW-*` item for the current artifact,
blocks the dependent workflow step.

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

### Native subagent model policy

For every native subagent dispatched under this workflow, set the model request
to `gpt-5.6-luna` with reasoning effort `max`, while keeping the installed
canonical `agent_type` and its lens. This workflow-local override takes
precedence over role defaults in `AGENTS.md`; do not silently fall back to
another model or effort. If the current runtime or agent catalog cannot honor
the pair, keep the lane `PENDING`, record the capability mismatch, and obtain
an explicit fallback before dispatch.

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
