# Common Workflow Checklist

Create this checklist after plan approval and before the first mutation. Apply
the status semantics from `checklist-contract.md`.

## Canonical Mainline

Execute the applicable rows below in physical order. Do not jump forward and
return to an earlier row. If PR delivery is outside scope, record concrete N/A
evidence for CG-11 through CG-18. CG-X01 is a separate conditional branch and
never substitutes for the PR mainline.

### Stage 1 - Preflight

- [ ] **CG-01 — Re-read authority**
  - **Action:** Read applicable `AGENTS.md`, selected leaf skill, current status,
    current diff, and the approved plan or request.
  - **Evidence:** Paths, status/diff summary, classification, and exact authority.
  - **Failure:** STOP before editing.
- [ ] **CG-02 — Query historical/current evidence**
  - **Action:** Query current GNO GitHub/docs for workflow, issue, PR, release,
    module, or guidance work; use direct live evidence when an index is stale.
  - **Evidence:** Queries and decisive results or documented unavailability.
  - **Failure:** STOP decisions that depend on missing history/current state.
- [ ] **CG-03 — Protect user work and boundaries**
  - **Action:** Identify repo/worktree/base/upstream and exclude unrelated dirty
    changes from the task.
  - **Evidence:** Status, worktree, base, upstream, and scoped files.
  - **Failure:** Preserve safely or BLOCK; never discard user work.
- [ ] **CG-04 — Apply policy and audience boundaries**
  - **Action:** Apply language/locale rules and preserve permission, sandbox,
    network, hook-trust, update, and vendor-surface boundaries unless explicitly
    included with rollback.
  - **Evidence:** Touched surfaces, language/locale decision, and policy scope.
  - **Failure:** Repair language drift or revert unauthorized policy changes.

### Stage 2 - Implementation and Verification

- [ ] **CG-05 — Reuse ecosystem patterns**
  - **Action:** Search repo/siblings/catalog before adding an abstraction or
    dependency and load the matching language/domain skill.
  - **Evidence:** Anchors reused or explicit fallback rationale.
  - **Failure:** Stop new abstraction/dependency work.
- [ ] **CG-06 — Prove public and documentation contracts**
  - **Action:** Update required public API docs, representative usage, README
    locales, durable artifacts, and registration surfaces.
  - **Evidence:** Paths and parity/registration proof, or scoped N/A evidence.
  - **Failure:** Block delivery of undocumented or unregistered behavior.
- [ ] **CG-07 — Lock behavior and run targeted proof**
  - **Action:** Use RED/GREEN for behavior changes, then run the smallest
    diagnostics, compile, lint, static, and test commands proving the contract.
  - **Evidence:** RED/GREEN when applicable plus fresh commands/results.
  - **Failure:** Return to implementation; investigate retry-only passes.
- [ ] **CG-08 — Serialize heavyweight checks**
  - **Action:** Run Testcontainers, real DB, native/JNI, emulator, benchmark,
    and shared-state checks sequentially across repos/worktrees/agents.
  - **Evidence:** Command order and results or N/A scope proof.
  - **Failure:** Discard ambiguous parallel evidence and rerun safely.
- [ ] **CG-09 — Evaluate the lesson gate**
  - **Action:** Apply the selected leaf's lesson rule. Create a committed lesson
    when required and a durable lesson for reusable learning. Use `N/A` only
    after reviewing the task and diff, naming the reused existing rule, and
    confirming no novel failure, recovery, design, or operational guidance.
  - **Evidence:** Lesson path/index result, or reviewed task/diff, reused rule,
    and all four absence categories for N/A.
  - **Failure:** Repair the lesson evidence before pre-PR review.
- [ ] **CG-10 — Converge the final pre-PR proof**
  - **Action:** Complete every applicable leaf pre-PR row, run the final scoped
    review, fix P0/P1 findings, rerun affected verification, and commit the
    converged scoped branch.
  - **Evidence:** Leaf rows, final diff, fresh checks, P0=0/P1=0, CG-09 result,
    and the exact local head commit SHA.
  - **Failure:** Keep PR creation blocked until the proof converges.

### Stage 3 - PR Delivery

- [ ] **CG-11 — Verify PR delivery authority**
  - **Action:** Verify that the current request or approved plan explicitly names
    PR creation and the target repository, base branch, and head branch. Confirm
    CG-01 through CG-10 and applicable leaf pre-PR rows are PASS. No additional
    approval is required after this authority is established.
  - **Evidence:** Exact authority, repo/base/head refs, and completed prerequisites.
  - **Failure:** STOP before PR creation and obtain or repair delivery authority.
- [ ] **CG-12 — Publish the exact head branch**
  - **Action:** Push the converged exact authorized head branch without force
    unless the approved repair requires it, then read back the remote head SHA.
  - **Evidence:** Commit SHA, push result, remote branch, and matching local and
    remote head SHAs.
  - **Failure:** STOP before PR creation; repair rejected, stale, or mismatched
    head publication without overwriting unrelated remote work.
- [ ] **CG-13 — Create and verify the PR**
  - **Action:** Create or update the PR, assign `debop`, mirror issue milestone
    and labels, write the required body ending in `## DoD Status`, then query it
    live.
  - **Evidence:** PR URL/number, head SHA, metadata, and verified final heading.
  - **Failure:** Repair the live PR before starting CI/review progression.
- [ ] **CG-14 — Pass CI and live human review**
  - **Action:** Wait for required CI on the exact PR head, reread current reviews
    and threads after green, and complete applicable diagram, visual, lesson,
    and other human-review artifacts.
  - **Evidence:** Successful checks, exact head SHA, no unresolved blockers,
    P0=0/P1=0, and applicable artifact decisions.
  - **Failure:** `PENDING` waits; failed/stale evidence returns to repair and
    reopens affected verification.
- [ ] **CG-15 — Report merge-ready**
  - **Action:** Re-read router/common/leaf rows, reconcile counts, and report the
    exact PR/head as merge-ready with CI, review, lesson, and artifact evidence.
  - **Evidence:** User-visible merge-ready report, `Required checks: X/Y`, N/A
    evidence, Blocked=0, exact PR, and exact head SHA.
  - **Failure:** Repair missing evidence; do not request merge approval yet.
- [ ] **CG-16 — Obtain fresh merge approval**
  - **Action:** After CG-15 is visible to the user, wait for fresh explicit merge
    approval for the exact PR/head and refresh CL-07. Earlier plan approval,
    create-and-merge wording, active scope, or PR permission never counts.
  - **Evidence:** User approval issued after CG-15 and refreshed target/hold.
  - **Failure:** Waiting is normal `PENDING`; refusal or invalid authority is
    `BLOCKED`. Never enable auto-merge or advance while pending.
- [ ] **CG-17 — Execute and verify the merge**
  - **Action:** Merge using the approved strategy only after CG-16 PASS, then
    verify the live merged state and merge commit.
  - **Evidence:** Merge command/URL, strategy, merged state, and merge SHA.
  - **Failure:** STOP and diagnose; never substitute auto-merge or another SHA.
- [ ] **CG-18 — Synchronize and clean up**
  - **Action:** Sync the real local checkout, preserve dirty state, and remove
    only proven merged worktrees/branches authorized by workspace policy.
  - **Evidence:** Local/upstream SHAs, clean/preserved status, and cleanup list.
  - **Failure:** Report `PENDING` with preserved state; never delete ambiguous work.

## Conditional Non-PR Irreversible Branch

- [ ] **CG-X01 — Authorize another irreversible action**
  - **Action:** Immediately before tag, publish, dispatch, release, deletion, or
    another non-PR irreversible action, complete its leaf prerequisites, verify
    explicit current authority, and refresh CL-07.
  - **Evidence:** Completed prerequisite IDs, exact authority, target
    ref/version/action, timestamp, and refreshed hold.
  - **Failure:** Waiting is `PENDING`; stale, missing, refused, or invalid
    authority blocks only this branch.
