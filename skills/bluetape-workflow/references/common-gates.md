# Common Workflow Checklist

Create this checklist after plan approval and before the first mutation. Apply
the status semantics from `checklist-contract.md`.

## Scope and Evidence

- [ ] **CG-01 — Re-read authority**
  - **Action:** Read applicable `AGENTS.md`, selected leaf skill, current status,
    and current diff.
  - **Evidence:** paths plus status/diff summary.
  - **Failure:** STOP before editing.
- [ ] **CG-02 — Query historical/current evidence**
  - **Action:** For issue/PR/workflow/release/module/guidance work, query current
    GNO GitHub/docs and fall back to direct live evidence when stale.
  - **Evidence:** queries and decisive results or documented unavailability.
  - **Failure:** STOP decisions that depend on missing history/current state.
- [ ] **CG-03 — Protect user work and boundaries**
  - **Action:** Identify repo/worktree/base/upstream and exclude unrelated dirty
    changes from the task.
  - **Evidence:** status, worktree, base, and scoped files.
  - **Failure:** preserve/stash safely or BLOCK; never discard user work.

## Language, API, and Documentation

- [ ] **CG-04 — Apply audience language policy**
  - **Action:** Use Korean chat, concise English agent guidance, English public
    contributor artifacts, and synchronized README locales.
  - **Evidence:** touched artifact list with chosen language/locale parity.
  - **Failure:** repair inconsistent artifacts before review.
- [ ] **CG-05 — Prove public contract documentation**
  - **Action:** Add/update English KDoc and representative usage evidence for
    public API changes; store durable specs/plans/lessons in repo paths.
  - **Evidence:** API/doc paths or scope proof for N/A.
  - **Failure:** block delivery of undocumented public behavior.

## Implementation and Tests

- [ ] **CG-06 — Reuse ecosystem patterns**
  - **Action:** Search repo/siblings/catalog before adding raw JDK, third-party, or
    ad hoc utilities; load the language pattern skill.
  - **Evidence:** anchors reused or explicit fallback rationale.
  - **Failure:** stop new abstraction/dependency work.
- [ ] **CG-07 — Lock behavior and run targeted proof**
  - **Action:** Use regression tests before cleanup/behavior change, then run the
    smallest compile/lint/static/test commands that prove the contract.
  - **Evidence:** RED/GREEN when applicable plus commands/results.
  - **Failure:** return to implementation; a retry-only pass requires lifecycle
    investigation.
- [ ] **CG-08 — Serialize heavyweight checks**
  - **Action:** Run Testcontainers, real DB, native/JNI, emulator, and shared-state
    integration checks sequentially across repos/worktrees/agents.
  - **Evidence:** command order and results or N/A scope proof.
  - **Failure:** discard ambiguous parallel evidence and rerun safely.

## GitHub and Delivery

- [ ] **CG-09 — Verify issue/PR metadata live**
  - **Action:** Assign `debop`; inspect/mirror milestone and relevant labels; query
    the created/edited issue and PR live.
  - **Evidence:** `gh issue view`/`gh pr view` fields.
  - **Failure:** repair metadata before downstream review/merge.
- [ ] **CG-10 — Verify PR body and reviews live**
  - **Action:** Confirm why/what/validation sections, final `## DoD Status`, and
    reread reviews/threads after CI becomes green.
  - **Evidence:** live body final heading, review/thread state, P0/P1=0.
  - **Failure:** update/review/retest; merge remains blocked.
- [ ] **CG-11 — Enforce side-effect authority**
  - **Action:** Match merge/tag/publish/dispatch/release/deletion to an explicit
    request or approved active scope.
  - **Evidence:** exact authority and target ref/version/action.
  - **Failure:** STOP at the boundary.
- [ ] **CG-12 — Synchronize after merge**
  - **Action:** Sync the real local checkout; preserve dirty state with
    include-untracked stash when necessary.
  - **Evidence:** local/upstream SHAs and clean/preserved status.
  - **Failure:** final status remains PENDING.

## Guidance and Harness

- [ ] **CG-13 — Update managed source first**
  - **Action:** Resolve chezmoi source/target, edit source, targeted apply, and prove
    source/rendered/live parity without touching Claude surfaces.
  - **Evidence:** resolved paths, apply result, byte/recursive parity.
  - **Failure:** repair source chain; live-only edits do not pass.
- [ ] **CG-14 — Audit durable Codex changes**
  - **Action:** Run `sync-codex.sh --status`, self-audit, and intentional commit/
    push when persistence is requested.
  - **Evidence:** audit counts, dirty/ahead/behind, commit/upstream SHA.
  - **Failure:** repair WARN/FAIL/parity or report BLOCKED.
- [ ] **CG-15 — Preserve global policy boundaries**
  - **Action:** Leave permission/sandbox/network/hook trust/update defaults and
    Claude surfaces unchanged unless explicitly included with rollback.
  - **Evidence:** scoped diff and policy-change authority or N/A proof.
  - **Failure:** revert unauthorized policy changes.

## Shell, Workflow, and Exit

- [ ] **CG-16 — Use authoritative tooling safely**
  - **Action:** Use raw reads/commands for policy, skills, checklists, failures,
    logs, git/GitHub, and mutation; avoid zsh variable `path`.
  - **Evidence:** commands/scripts inspected; `actionlint` for workflow YAML.
  - **Failure:** rerun with complete authoritative output; zero-job run is FAIL.
- [ ] **CG-17 — Prove completion line by line**
  - **Action:** Re-read this checklist and the leaf checklist; verify requested
    steps, behavior, fresh checks, P0/P1=0, and claimed external/local state.
  - **Evidence:** checked/total count, N/A scope evidence, unchecked list, final status.
  - **Failure:** report PENDING/BLOCKED and continue the recoverable branch.
