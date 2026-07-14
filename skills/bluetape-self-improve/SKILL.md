---
name: bluetape-self-improve
description: Use when the user explicitly requests repeated benchmark-driven improvement, a target metric, candidate tournament, plateau loop, or measurable self-improvement in a bluetape4k repository.
---

# bluetape4k Self Improve

## Parent Contract

Use `bluetape-workflow` first for Type F classification, first-plan approval,
Step DoD, and side-effect boundaries. Do not use this skill for a one-off
`perf:` edit without an iterative benchmark target.

This loop may continue autonomously after the plan and benchmark command are
approved, but the loop itself may not push, open a PR, perform a GitHub PR
merge, publish, or edit sealed files. After the loop stops, remote branch/PR
delivery may proceed only through CG-11 through CG-15 when the current request
or approved plan establishes exact repository/base/head/action authority.
Every GitHub PR merge still requires the fresh post-report approval at CG-16.
Defaults keep `auto_push=false`, `auto_pr=false`, and `auto_merge=false`.

## Hard Benchmark Gate

Do not create candidates until all fields are concrete:

1. objective and allowed modules/files;
2. primary metric, direction, target/minimum improvement, plateau threshold,
   regression threshold, and secondary guards;
3. repeatable repo-local benchmark command and result parser/format;
4. fresh baseline (prefer three runs for noisy metrics) with environment;
5. sealed harness, fixture, parser, and baseline-report paths;
6. max iterations, plateau window, circuit-breaker threshold, and user stop;
7. explicit trust confirmation for repeated execution of repository code.

Use repo-local Gradle `kotlinx-benchmark` tasks for Kotlin/JVM benchmark modules.
Verify generated task names with `./gradlew :<module>:tasks --all`. Do not create
raw-JMH-only modules or make a generated JMH jar the default path. Load
`bluetape-diagram` when charts are part of the output.

## State Initialization

Initialize `.omx/self-improve/` only after plan approval. Migrate legacy state
first, then copy any still-missing templates; never overwrite an active run:

| Template | Destination | Write semantics |
|---|---|---|
| `templates/settings.json` | `config/settings.json` | Fill gate values before baseline |
| `templates/goal.md` | `config/goal.md` | Record objective, scope, metric, candidate ideas |
| `templates/harness.md` | `config/harness.md` | Add benchmark/parser/guard details |
| `templates/state.json` | `state/state.json` | Create after legacy migration; update after every gate and transition |

Also maintain `tracking/baseline.json`, `tracking/raw_data.json`,
`tracking/events.json`, and bounded `state/iteration_history/`, `merge_reports/`,
and `plan_archive/` artifacts.

### Legacy State Migration

For one compatibility window, if `state/state.json` is absent but legacy
`state/agent-settings.json` or `state/iteration_state.json` exists, migrate
before copying `templates/state.json`.

1. Start from the new state template defaults.
2. From `agent-settings.json`, map status, iteration counts, best score/round,
   plateau/circuit counts, goal slug, and trust/benchmark confirmations.
3. From `iteration_state.json`, map current iteration, step, candidate, status,
   and timestamps; these current-iteration fields take precedence.
4. Reject unknown non-object JSON. Preserve original files.
5. Write `state.json.tmp`, validate with `jq`, rename to `state.json`, append a
   `legacy_state_migrated` event, and record `last_valid_checkpoint`.

All subsequent writes use the same temp -> parse -> rename protocol and target
only `state/state.json`.

## Branch and Worktree Isolation

- Base: `develop` unless repo/user policy specifies another branch.
- Accepted branch: `improve/{goal_slug}` contains winners only.
- Candidate branch: `experiment/{goal_slug}/round-{n}-{candidate}`.
- Worktree: `.omx/self-improve/worktrees/round-{n}-{candidate}`.
- Never edit sealed files in a candidate.
- One candidate per iteration is the default. Use 2-3 distinct candidates only
  when worktree isolation, benchmark cost, and machine resources make a bounded
  tournament safe.
- Prepare independent edits in parallel only when useful; run
  Testcontainers/real DB/native benchmarks and tests sequentially.

## Loop

Apply `bluetape-workflow/references/checklist-contract.md`. Re-render this
checklist after every iteration; only checked rows permit the next transition.

- [ ] **F-01 — Lock the benchmark contract**
  - **Action:** Complete every Hard Benchmark Gate field and obtain plan, benchmark-command, and repeated-code-execution approval.
  - **Evidence:** Objective/scope, metric direction and thresholds, guards, parser, three-run baseline when noisy, environment, sealed paths, budgets, stop rules, and trust confirmation.
  - **Failure:** Do not initialize candidates or claim a measurable objective.
- [ ] **F-02 — Initialize recoverable state**
  - **Action:** Migrate legacy state when present, materialize missing templates without overwrite, validate atomic state writes, and register tracking artifacts.
  - **Evidence:** Valid config/state/tracking files, migration event when applicable, and last valid checkpoint.
  - **Failure:** Stop before candidate work; repair state integrity or recover from the last valid checkpoint.
- [ ] **F-03 — Isolate branches, worktrees, and sealed inputs**
  - **Action:** Create the accepted and candidate branches/worktrees from the trusted base, protect sealed files, and serialize heavyweight benchmarks/tests.
  - **Evidence:** Branch/worktree map, trusted candidate base, clean ownership boundaries, and sealed path inventory.
  - **Failure:** Discard the contaminated candidate or repair isolation before measurement.
- [ ] **F-04 — Approve a distinct measurable hypothesis**
  - **Action:** Run the stop check, inspect current evidence, define one measurable mechanism, reject repeated failed families without new evidence, and review rollback/scope.
  - **Evidence:** Candidate plan tied to the bottleneck, measurement path, distinct approach family, rollback point, and allowed files.
  - **Failure:** Do not execute an untestable, repeated, public-API-changing, or sealed-file hypothesis.
- [ ] **F-05 — Verify the candidate before comparison**
  - **Action:** Implement with TDD, pass targeted checks, validate sealed files against the trusted base, then run the exact benchmark and parser.
  - **Evidence:** RED/GREEN, diagnostics/tests, sealed validation PASS, raw benchmark output, parsed metrics, and environment identity.
  - **Failure:** Reject or repair the candidate; never benchmark a test failure or compare invalid output.
- [ ] **F-06 — Apply the acceptance rule**
  - **Action:** Normalize direction, compare against the same fresh baseline/best, enforce minimum improvement and secondary guards, and verify scope/docs/API/module rules.
  - **Evidence:** Baseline/candidate/best, normalized delta, guard results, scoped diff, and explicit accept/reject decision.
  - **Failure:** Reject unmeasured, below-threshold, regressing, or out-of-scope candidates; do not integrate them.
- [ ] **F-07 — Integrate and checkpoint the iteration**
  - **Action:** Merge only one accepted winner locally between the isolated self-improve branches, without remote mutation or GitHub PR merge; archive rejected evidence and atomically record results, decision, files, family, and next stop state.
  - **Evidence:** Winner commit or rejection archive, updated raw/event/state files, and valid recovery checkpoint.
  - **Failure:** Keep the improvement branch unchanged and recover state before another iteration.
- [ ] **F-08 — Stop and report truthfully**
  - **Action:** Evaluate every stop condition, render iteration and final DoD evidence, preserve raw results, add durable learning when substantial, and respect unapproved external side effects.
  - **Evidence:** `Required checks: X/Y; N/A: N; Blocked: 0` for a completed iteration, explicit stop reason, baseline/final/delta history, winner branch/commit, tests, risks, and side-effect state.
  - **Failure:** Preserve the last valid baseline/best and classify a repairable proof failure as FAIL, a valid external wait as PENDING, and only no safe continuation as BLOCKED; never label unavailable or incomparable measurements as improvement.
- [ ] **F-09 — Deliver and report through the common PR gates**
  - **Action:** With a PR, complete CG-11 through CG-15 after F-08: verify authority, publish the exact winner head, create or update and verify the PR, pass exact-head CI/current review and human artifacts, then report merge-ready. Without a PR, record CG-11 through CG-18 N/A and render the final no-delivery report.
  - **Evidence:** With a PR, matching local/remote/PR head, live metadata and final `## DoD Status`, successful checks, current review, applicable human artifacts, phase-aware counts, and exact-head merge-ready report; without a PR, concrete N/A evidence and every other applicable row PASS.
  - **Failure:** CI/review waits remain PENDING. Do not publish from an active candidate loop, report merge-ready before CG-15, or treat earlier benchmark/plan approval as merge authority.
- [ ] **F-10 — Close out only after fresh merge approval**
  - **Action:** With a PR, after fresh user approval of the current F-09 report, complete CG-16 through CG-18: record approval, merge and verify live state, then sync and clean only proven merged worktrees/branches. Without a PR, record F-10 N/A from the common no-PR branch.
  - **Evidence:** With a PR, fresh approval tied to the exact head, merge result/SHA, integration-branch sync, and cleanup result; without a PR, the same concrete CG-11 through CG-18 N/A evidence used at F-09.
  - **Failure:** Waiting at CG-16 is PENDING; refusal or invalid authority is BLOCKED. CG-17 failure returns to repair; CG-18 ambiguity remains PENDING with state preserved.

1. **Recover**: inspect state and registered worktrees. Remove only proven stale
   self-improve worktrees, then prune.
2. **Refresh**: read settings, goal, harness, state, baseline, and prior failed
   approach families.
3. **Stop check**: evaluate target, plateau, iteration budget, circuit breaker,
   hard blocker, and user stop before new work.
4. **Research**: inspect current code/profile/result and GNO/GitHub/lesson
   evidence relevant to the bottleneck.
5. **Hypothesize**: one measurable mechanism per candidate; do not repeat a
   failed family without new evidence.
6. **Review plan**: reject sealed-file edits, casual public API changes,
   untestable hypotheses, missing rollback, or changes the benchmark cannot
   measure.
7. **Execute**: use TDD and matching language/domain patterns inside the isolated
   candidate worktree.
8. **Verify**: targeted compile/tests, then
   `scripts/validate-sealed.sh --base <trusted-candidate-base>`, then the exact
   benchmark command. Never benchmark a test failure. The trusted base is the
   commit from which the candidate worktree was created, not candidate `HEAD`.
9. **Compare**: normalize metric direction and compare against the same fresh
   baseline/best plus secondary regressions.
10. **Integrate**: merge one accepted winner locally into the improvement
    branch; archive rejected plans/results without merging their code.
11. **Record**: update state, raw results, delta, changed files, decision,
    approach family, and next stop state atomically enough for recovery.

## Acceptance Rule

A candidate wins only when all are true:

- targeted tests and required diagnostics pass;
- `scripts/validate-sealed.sh` passes;
- benchmark command and parser succeed;
- primary metric improves in the configured direction by the minimum threshold;
- no guarded metric/behavior exceeds the regression threshold;
- diff matches the approved hypothesis and scope;
- affected public API/KDoc/README locales/CI/module rules pass.

If no candidate wins, record each rejection and continue only if the next stop
check allows it. Never integrate an unmeasured “looks faster” change.

## Stop Conditions

Stop on target reached, plateau window, max iterations, circuit breaker, user
stop, benchmark trust/parser failure, unrecoverable environment failure, or no
remaining distinct hypothesis. Do not call an unavailable benchmark an
improvement. Keep repairable benchmark/parser proof failures as FAIL, valid
external waits as PENDING, and use BLOCKED only when no safe continuation
exists; always preserve the last valid baseline/best.

## Verification and Reporting

Each iteration reports hypothesis, branch/worktree, changed files, test command,
sealed result, benchmark command, baseline/candidate/best, normalized delta,
decision, and stop state.

The final parent Step DoD includes objective, environment, benchmark command,
baseline/final score, delta, iteration/rejection history, sealed validation,
tests, winner commit/branch, public docs impact, stop condition, and remaining
risks. PR bodies use the central template and end with `## DoD Status`.

Add a durable lesson after substantial work. Preserve raw evidence and describe
local short-window results as comparable snapshots, not universal production
rankings.

With a PR, the normal pre-merge state is F-09 PASS and CG-16 PENDING; report
DONE only after F-10 completes CG-16 through CG-18. Without a PR, report DONE
after CG-11 through CG-18 and F-10 are evidence-backed N/A and every other
applicable row passes.
