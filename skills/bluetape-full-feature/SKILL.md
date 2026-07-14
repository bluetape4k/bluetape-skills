---
name: bluetape-full-feature
description: Use when an approved bluetape4k Type A change adds a module, dependency, service, subsystem, broad public API, architecture, multi-layer behavior, or large refactor and needs the full spec-to-PR lifecycle.
---

# bluetape4k Full Feature

## Parent Contract

**REQUIRED SUB-SKILL:** Use `bluetape-workflow` first for Type A
classification, first-plan approval, common gates, step progression, and DoD
reporting. Do not use this skill to bypass that approval gate.

This skill owns the Type A sequence from worktree through PR and knowledge
capture. Every required step begins with `Action` and `Expected DoD`, ends with
`Step DoD: PASS|FAIL|PENDING`, and blocks dependent steps until PASS.

## Required Skill and Reference Loading

Load only at the step that needs it:

| Trigger | Required surface |
|---|---|
| Step 0 worktree | `using-git-worktrees` when installed/required by the workspace |
| Step 2 design | `using-superpowers` and `brainstorming` |
| Step 3 plan | `writing-plans` |
| Step 4 code | `test-driven-development` plus the matching language/domain pattern skill |
| Step 4-S cleanup | `ai-slop-cleaner` only when cleanup triggers |
| Step 5/6 completion claims | `verification-before-completion` |
| Any native review dispatch | `../bluetape-workflow/references/model-routing.md` |
| Step 2-R or 3-R | `references/review-perspectives.md`; Step 3-R also loads `references/step-3r-plan-review.md` |
| Step 4-P or performance/stability review | `references/performance-stability-scan.md` |
| Step 5 | `references/step-5-verifier-checklist.md` |
| Step 6-R and 7-R | `references/step-6r-code-review.md` |
| Module/workflow/catalog/Kover/benchmark/backend/nightly hazards | `../bluetape-workflow/references/repository-hazards.md` |

If a required skill/reference is missing or unreadable, stop that gate and
report the exact gap. Do not reconstruct a substitute from memory. New modules,
dependencies, architecture, and multi-layer work must not proceed without the
required design and planning skills.

## Review and Convergence Contract

Steps 2-R, 3-R, 6-R, and 7-R use six independent perspective lanes plus one
main-session integration review:

1. performance;
2. stability;
3. security;
4. operator/Ops;
5. developer/API;
6. user/caller;
7. main-session integration for deduplication, documentation/release/evidence,
   severity normalization, critic challenge, and final verdict.

Use canonical installed roles from the workflow model-routing reference; lens
names are not `agent_type` values. Schedule lanes in waves if the session has
fewer than six free slots. Each lane is read-only, has one lens, exact scope,
command limits, output contract, and stop condition. The main session owns all
edits and the final gate.

- Normalize findings to P0/P1/P2/P3.
- P0/P1 blocks progression. Apply the approved repair, rerun validation, then
  rerun only affected lanes and integration.
- P2/P3 is fixed, deferred with rationale, or filed as follow-up.
- Close a gate only when the latest integrated table shows P0=0 and P1=0.
- Use bounded waits and replace an unresponsive lane; after bounded retries,
  record the timeout and perform that perspective in the main session.
- Testcontainers/real DB/native/JNI/emulator commands remain sequential.

## Ordered Workflow

```text
0 worktree -> 1 requirements -> 1-R research -> 2 spec -> 2-R spec review
-> 3 plan -> 3-R plan review -> 3-P risk prediction when triggered
-> 4 implementation -> 4-T tests -> 4-S cleanup when triggered
-> 4-P performance/stability when triggered -> 5 spec/plan verification
-> 6 final checklist -> 6-R pre-PR review -> 7 lessons commit
-> 7-P PR -> 7-R PR review -> 8 CI/review gate -> 9 knowledge capture
-> 10 merge-ready DoD report -> 11 approved merge closeout
```

Do not reorder dependent steps or mark a required step N/A merely because the
change feels obvious. If a procedural miss is found, stop downstream work,
repair the missed gate, report its DoD, then resume.

## Mandatory Type A Checklist

Apply `bluetape-workflow/references/checklist-contract.md`. The detailed
steps below define how to execute each item; only this checked state controls
progression.

- [ ] **A-01 — Isolate and confirm requirements**
  - **Action:** Create the worktree, preserve unrelated changes, inspect the current issue/evidence, and define outcome, boundaries, compatibility, side effects, and stop condition.
  - **Evidence:** Repository, branch, worktree, base, cwd, approved requirements, exclusions, and authority boundaries.
  - **Failure:** Stop before research or artifacts; recover missing files or clarify material ambiguity.
- [ ] **A-02 — Ground the design in current evidence**
  - **Action:** Inspect repository patterns and history, query relevant knowledge sources, verify unfamiliar external behavior from primary sources, and resolve dependency/catalog authority.
  - **Evidence:** Concrete local anchors, prior-decision evidence, source citations, and adopt/borrow/reject rationale.
  - **Failure:** Do not design from recall; repair the evidence gap first.
- [ ] **A-03 — Approve and review the design spec**
  - **Action:** Use the required design skills, compare viable alternatives, obtain user approval, write the spec, and run all six review perspectives plus integration.
  - **Evidence:** Approved spec path, alternatives and failure modes, review table, and latest P0=0/P1=0.
  - **Failure:** Revise and reapprove material changes; keep planning blocked.
- [ ] **A-04 — Approve and review the implementation plan**
  - **Action:** Write an ordered executable plan mapping every acceptance criterion to files, pattern skills, tests, docs, hazards, rollback, and commands; run all plan review perspectives.
  - **Evidence:** Plan path, committed spec/plan, traceability map, review table, and latest P0=0/P1=0.
  - **Failure:** Repair missing ordering, proof, ownership, or hazard coverage before code.
- [ ] **A-05 — Predict triggered risks**
  - **Action:** For high-complexity or sensitive work, record risks, signals, mitigations, and rollback/rerun points; otherwise prove a scoped N/A.
  - **Evidence:** Risk entries attached to implementation tasks or concrete evidence that no trigger applies.
  - **Failure:** Do not use a generic skip; complete risk prediction before implementation.
- [ ] **A-06 — Implement with test-first proof**
  - **Action:** Use TDD and the language/domain skills for each behavior, keep delegated writes disjoint, integrate the diff, and run cleanup/performance scans when triggered.
  - **Evidence:** RED/GREEN sequence, scoped diff, integration inspection, diagnostics, and triggered cleanup/performance results or evidence-backed N/A.
  - **Failure:** Return to the failing behavior or violated boundary; do not advance with stale or partial proof.
- [ ] **A-07 — Verify tests, spec, plan, and repository hazards**
  - **Action:** Run targeted then proportional broader validation, verify against the exact approved spec/plan, and complete every triggered module/docs/workflow/catalog hazard check.
  - **Evidence:** Fresh commands and results, verifier verdict PASS, complete acceptance mapping, and all conditional hazards PASS or valid N/A.
  - **Failure:** Return to implementation or reopen the approved artifact when the verifier reports a gap.
- [ ] **A-08 — Converge the final pre-PR review**
  - **Action:** Run the final checklist, all six code-review perspectives plus integration, fix blockers, and rerun affected proof.
  - **Evidence:** Final branch diff, optional tracked review artifact, clean diagnostics/diff check, and latest P0=0/P1=0.
  - **Failure:** Keep PR creation blocked until repaired evidence converges.
- [ ] **A-09 — Commit durable learning**
  - **Action:** Commit the lesson before PR creation, using a concise evidence-backed N/A lesson only when genuinely appropriate.
  - **Evidence:** Tracked lesson commit containing context, decision, outcome, proof, misses, and future guard.
  - **Failure:** An untracked, stashed, or evidence-only lesson does not satisfy this gate.
- [ ] **A-10 — Complete authorized PR delivery through live CI and review**
  - **Action:** Complete common gates CG-11 through CG-14: confirm PR authority, publish the exact head, create or update and verify the live PR, rerun review, resolve threads, and wait for required CI conclusions.
  - **Evidence:** CG-11 authority, matching remote head, live PR metadata and final `## DoD Status`, latest review convergence, required checks successful, and all required human-inspection artifacts complete; or concrete evidence that CG-11 through CG-18 are N/A.
  - **Failure:** Keep delivery PENDING or FAIL as the common gate requires; stale, missing, or unexplained skipped evidence is not PASS.
- [ ] **A-11 — Capture knowledge and report merge readiness**
  - **Action:** Capture durable knowledge. With a PR, complete CG-15 by rendering every Type A row with phase-aware counts, evidence, risks, exact PR/head state, and unchecked CG-16 through CG-18; stop at CG-16. Without a PR, record CG-15 N/A under the common no-PR branch and render the final no-delivery DoD.
  - **Evidence:** Knowledge/index result or valid N/A plus reconciled `Required checks: X/Y; N/A: N; Blocked: 0`; with a PR, a user-visible merge-ready report tied to the current head and explicit pending IDs; without a PR, concrete CG-11 through CG-18 N/A evidence.
  - **Failure:** Do not claim DONE or treat an earlier approval as merge authority; expose the blocking row and repair action.
- [ ] **A-12 — Close out only after fresh merge approval**
  - **Action:** With a PR, after the user explicitly approves the current merge-ready report, complete CG-16 through CG-18: record the approval, merge and verify live state, then sync and clean local worktrees/branches. Without a PR, record A-12 N/A from the common no-PR branch.
  - **Evidence:** With a PR, fresh approval tied to the current head, merge result and SHA, clean integration branch sync, and cleanup result; without a PR, the same concrete CG-11 through CG-18 N/A evidence used at A-11.
  - **Failure:** Waiting at CG-16 is normal PENDING; refusal or invalid authority is BLOCKED. A CG-17 merge failure returns to repair as FAIL. CG-18 ambiguity or incomplete cleanup remains PENDING with state preserved.

## Step 0 - Worktree

Create the feature worktree before writing spec, plan, or code. Base long-lived
work on current `origin/develop` unless the repo-local guide says otherwise.
Write all durable artifacts inside the worktree so they remain visible to the
feature branch.

Required evidence:

- repository, branch, worktree path, and upstream base;
- clean separation from unrelated changes;
- subsequent command working directory.

If a required spec/plan/evidence file is missing, stop and report paths tried,
cwd, branch, and whether the file may exist untracked in another checkout. Do
not recreate it from memory or continue on assumptions.

## Step 1 - Requirements

Confirm target repo, user outcome, boundaries, compatibility constraints,
public API/docs impact, external side effects, and stop condition. Inspect any
concrete issue, PR, error, CI run, or report before designing. Clarify material
ambiguity one question at a time; do not implement during clarification.

## Step 1-R - Research

Ground the design in current evidence:

- current repository structure, similar implementations, tests, and reusable
  bluetape4k APIs;
- GNO/GitHub/lessons/specs/plans when prior decisions may matter;
- official docs or primary source/jar evidence for unfamiliar or versioned
  external APIs;
- dependency/catalog source of truth and compatibility lines;
- adopt, borrow, or reject decisions with rationale.

Use `explore` for repo facts, `researcher` for official external behavior, and
`dependency-expert` for dependency comparison. Preserve web research according
to the workspace SOP when it materially affects the decision.

## Step 2 - Design Spec

Load and follow `using-superpowers` and `brainstorming` completely. For each
material architecture/API/behavior/migration section, present 2-3 viable
approaches when choices exist, recommend one, and obtain user approval before
finalizing it.

Write `docs/superpowers/specs/YYYY-MM-DD-{slug}-design.md` inside the worktree.
Include problem, constraints, current evidence, chosen approach, rejected
alternatives, boundaries, at least three failure modes for non-trivial work,
compatibility/migration, acceptance criteria, and DoD. Code/API/test examples
must already follow the matching Kotlin/Go/Rust/domain pattern skills.

## Step 2-R - Spec Review

Read `references/review-perspectives.md` with `artifact_kind=spec`. Run all six
perspectives plus main integration against the exact spec and research basis.
Revise every P0/P1. If a repair materially changes the approved design, return
to the user for approval, then rerun affected lanes. Exit only at P0=0/P1=0.

## Step 3 - Implementation Plan

Load `writing-plans` and write
`docs/superpowers/plans/YYYY-MM-DD-{slug}-plan.md`. Each task includes:

- complexity, dependency order, exact files/modules, and disjoint write scope;
- matching pattern skill and TDD behavior;
- concrete validation command and expected evidence;
- public KDoc/README locale/diagram/CHANGELOG/AGENTS impact;
- rollback or rerun point for migrations, dependency, and cross-module risk;
- triggered repository-hazard checks.

Test plans name success, failure, edge, lifecycle, cancellation/concurrency,
and backend capability cases when relevant. Use bluetape4k test helpers and
assertions; record why a raw fallback is necessary. Commit the approved spec and
plan to the feature branch before Step 4.

## Step 3-R - Plan Review

Read `references/review-perspectives.md` with `artifact_kind=plan` and
`references/step-3r-plan-review.md`. Run all six perspectives plus main
integration. Verify every spec acceptance criterion maps to an ordered task and
command, no task depends on a later artifact, and hazards/docs/rollback are
assigned. Exit only at P0=0/P1=0.

## Step 3-P - Risk Prediction

Run when high-complexity tasks or concurrency, caching, security, DB
consistency, external APIs, architecture boundaries, or performance hot paths
exist. Add the top risks, signals, mitigations, and rollback/rerun points to the
relevant Step 4 tasks. Otherwise record concrete scope evidence for `N/A`.

## Step 4 - Implementation

Load `test-driven-development` and the matching language/domain skills. For
each behavior: add a failing test, observe the expected failure, implement the
minimum change, observe PASS, then refactor while green. Inspect symbol impact
before Kotlin edits when tools are available and clear diagnostics before
compilation.

Parallelize only independent tasks with disjoint write ownership. Inspect the
integrated diff, untracked files, module registration, and workflow references
after delegated work. No lane may perform unapproved commits or external side
effects.

## Step 4-T - Tests

Run targeted affected-module tests first and capture fresh command/result
evidence. Run Testcontainers/real DB/native checks sequentially; use one Gradle
invocation or explicit sequential commands. Verify each affected repository
independently. For concurrency risks, use existing bluetape4k testers when
applicable. For benchmark modules, use verified `kotlinx-benchmark` Gradle task
names.

On failure, stop, inspect raw failure evidence, diagnose root cause, return to
Step 4, then rerun Step 4-T from the beginning. A retry PASS does not erase a
lifecycle/timing failure without investigation.

## Step 4-S - Cleanup

Run only when the approved implementation introduces substantial verbosity,
duplication, generated slop, or broad refactor residue. Write a cleanup plan,
preserve behavior with tests, make one smell-focused pass, then rerun targeted
validation. Otherwise record concrete scope evidence for `N/A`.

## Step 4-P - Performance and Stability

Run when the diff changes hot-path allocation, regex/serialization, blocking or
async behavior, lifecycle/resources, external servers, DB/cache/HTTP, or more
than a small implementation surface. Read
`references/performance-stability-scan.md`, fix P0/P1, and rerun affected tests.

## Step 5 - Verify Against Spec and Plan

After Step 4-T is green, read `references/step-5-verifier-checklist.md`. Verify
the exact approved spec, plan, current diff, tests, and docs. Outcomes:

- `PASS`: continue;
- `NEEDS FIX`: return to Step 4 and 4-T;
- `NEEDS REVIEW SCOPE`: update/approve the spec or plan and rerun its review.

Missing spec/plan files invoke the Step 0 stop protocol, not a best-effort pass.

## Step 6 - Final Checklist

Load `verification-before-completion` and prove:

- affected compile, tests, lint/static checks, and `git diff --check` pass;
- public API names, KDoc, README locales, diagrams, and examples match source;
- module/workflow/Nightly/Kover/BOM/catalog registration is complete when
  triggered;
- no unresolved deprecation/diagnostic issue remains in touched code;
- Lore commits include only intended files;
- no completion claim, PR, or merge boundary is crossed early.

## Step 6-R - Pre-PR Review

Read `references/step-6r-code-review.md` and the performance/stability reference
when triggered. Review the current branch diff in dependency-ordered module
slices. Run all six perspectives plus main integration; store a concise tracked
review artifact under `docs/review/` when it will support PR/merge evidence.
Fix and revalidate P0/P1, rerun affected lanes, and exit only at zero blockers.

## Step 7 - Lessons Commit

Before PR creation, create and commit
`docs/lessons/YYYY-MM-DD-{slug}.md` with context, decision, surprise/failure,
outcome, verification evidence, review misses, and future guard. If genuinely
no durable lesson exists, commit the file with concrete scope evidence proving
`N/A`; do not invent filler. An untracked, stashed, or evidence-only lesson does
not unblock Step 7-P.

## Step 7-P - Pull Request

Complete CG-11 through CG-13 only after Step 7. PR creation may proceed without a
separate approval only when the approved plan or current request names the
repository, base, head, and creation action. Read linked issue metadata first.
Assign `debop`, mirror milestone and relevant labels, use an English title/body,
and use the central PR template. The body explains why/what before validation
and ends with `## DoD Status`. Verify live metadata and body with `gh pr view`;
comments are not substitutes.

## Step 7-R - Post-PR Review

Rerun the six perspectives plus main integration against the actual PR diff,
reviews, and current CI state. `REQUEST_CHANGES` or any P0/P1 returns to Step 4,
4-T, and affected review lanes. Record acceptance/deferral rationale for
non-blocking findings. Refresh the PR body DoD after gate changes.

## Step 8 - CI and Review Gate

Complete CG-14. Read required check conclusions from the live PR. `SUCCESS` passes; a genuinely
inapplicable check needs evidence-backed N/A under the checklist contract;
`PENDING` waits and `FAILURE` returns to diagnosis/fix. After CI is green, re-read
reviews and unresolved threads. New feedback reopens Step 7-R. Do not dismiss a
zero-job run as a test failure; validate workflow syntax first.

## Step 9 - Knowledge Capture

For significant work, update GNO/indexes and promote durable decisions to the
repo's spec/plan/lesson/reference surfaces. Use transient OMX notepad/state only
for session continuity. Update user memory only when explicitly asked. For new
modules, update the repo/module guidance overlay. If no new durable knowledge
exists, record N/A with concrete scope evidence.

## Step 10 - Merge-Ready DoD

Complete CG-15 with the workflow final-report template. Include all steps,
P0/P1 convergence, spec/plan acceptance, test commands/results, PR metadata,
CI/review and human-inspection evidence, commits, changed files, knowledge
capture, and residual risks. Tie the report to the exact live PR head, report
the PR pending merge, and request a fresh merge decision. At this phase, report
CG-16 through CG-18 as unchecked PENDING IDs rather than claiming X=Y. CG-16
remains normal `PENDING` until the user replies; never run `gh pr merge`
automatically. When PR delivery is N/A, record CG-11 through CG-18 N/A and
render the no-delivery DoD instead of requiring PR/head evidence.

## Step 11 - Approved Merge Closeout

Only after the user explicitly approves the current Step 10 report, complete
CG-16 through CG-18. Verify the live merge result and merge SHA, sync the local
integration branch, and delete the merged worktree and local feature branch
unless the user asked to retain them. A prior plan, implementation approval, PR
creation authority, or create-and-merge request does not satisfy CG-16.

## Stop Conditions

The normal pre-merge terminal state is Step 10 delivered with Step 9 PASS/N/A
and `PENDING - PR ready for fresh explicit merge decision` at CG-16. Report
`DONE` only after Step 11 completes CG-16 through CG-18 with live merge, sync,
and cleanup evidence. When PR delivery is outside scope, report `DONE` after
Step 9 is PASS/N/A, Step 10 renders the no-delivery DoD, CG-11 through CG-18
and A-12 are evidence-backed N/A, and every other applicable row passes.
