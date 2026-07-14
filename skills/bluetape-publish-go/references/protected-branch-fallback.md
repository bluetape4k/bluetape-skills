# Protected Branch Release Fallback

Use only when a direct release PR passed CI but is `CONFLICTING` because `main`
contains equivalent earlier release commits with different SHAs, or protection
rejects merge commits on `develop`.

- [ ] **GO-FB-01 — Prove fallback applicability**
  - **Action:** Confirm the direct release PR passed CI but is `CONFLICTING` for equivalent-history/protection reasons.
  - **Evidence:** Live PR state, CI, conflict cause, and protected-branch rule.
  - **Failure:** Repair the ordinary PR path; do not use fallback for unrelated conflicts.
- [ ] **GO-FB-02 — Close the failed path visibly**
  - **Action:** Close the conflicting PR with a replacement-path comment.
  - **Evidence:** Live closed PR and comment linking the planned replacement.
  - **Failure:** Do not leave two active promotion paths.
- [ ] **GO-FB-03 — Project develop from main**
  - **Action:** Create `release/v<version>-main-promotion` from `origin/main` and project the `origin/develop` tree onto it.
  - **Evidence:** Branch base and staged tree construction commands.
  - **Failure:** Stop on user changes or an unproven source tree.
- [ ] **GO-FB-04 — Prove exact tree equivalence**
  - **Action:** Run diff checks and prove staged stat/diff against `origin/develop` is empty.
  - **Evidence:** Exact tree equality and clean diff check.
  - **Failure:** Do not commit or open the replacement PR.
- [ ] **GO-FB-05 — Commit the fallback decision**
  - **Action:** Record why direct promotion failed, why merge/force alternatives were rejected, and why the projected tree is equivalent.
  - **Evidence:** Lore commit containing the decision and equality proof.
  - **Failure:** Repair the decision record before external delivery.
- [ ] **GO-FB-06 — Publish and open the replacement PR**
  - **Action:** After parent CG-01 through CG-10 pass for the replacement path, complete CG-11 through CG-13: verify authority for the exact fallback base/head, publish/read back the head, and create or update and live-verify the replacement PR to `main`.
  - **Evidence:** Common gate evidence, matching local/remote/PR head, and live metadata/body ending in `## DoD Status`.
  - **Failure:** Stop at the applicable common gate and repair authority, publication, or PR metadata.
- [ ] **GO-FB-07 — Pass replacement CI and review**
  - **Action:** Complete CG-14 on the exact replacement head, including required checks, current reviews/threads, mergeability, and applicable human artifacts.
  - **Evidence:** Successful exact-head checks, clean mergeability, no unresolved blocker, and artifact decisions.
  - **Failure:** PENDING waits; failed or stale evidence returns to repair.
- [ ] **GO-FB-08 — Report the replacement PR merge-ready**
  - **Action:** Complete CG-15 with the exact fallback PR/head, replacement rationale, equality proof, CI/review, lesson, artifacts, phase-aware counts, and unchecked CG-16 through CG-18.
  - **Evidence:** User-visible merge-ready report with reconciled counts and Blocked=0.
  - **Failure:** Repair the report before requesting merge approval.
- [ ] **GO-FB-09 — Obtain fresh replacement merge approval**
  - **Action:** Complete CG-16 only after GO-FB-08 is visible; wait for fresh explicit user approval of the exact replacement PR/head.
  - **Evidence:** Post-report approval and refreshed irreversible hold.
  - **Failure:** Waiting is PENDING; refusal or invalid authority is BLOCKED. Earlier release/fallback scope never counts.
- [ ] **GO-FB-10 — Merge and verify the replacement PR**
  - **Action:** Complete CG-17 after CG-16 passes by merging with the approved strategy and reading back the live merged state/SHA.
  - **Evidence:** Merge command/URL, strategy, live merged state, and merge SHA.
  - **Failure:** Stop and repair; never enable auto-merge or merge another head.
- [ ] **GO-FB-11 — Synchronize safely**
  - **Action:** Complete CG-18 by fast-forwarding `main`, cleaning only proven merged fallback state, and restoring a failed local `develop` attempt only when this fallback created it and no user work can be lost.
  - **Evidence:** Local/origin parity and ancestry/ownership proof for any restoration.
  - **Failure:** Preserve ambiguous local state and report PENDING rather than deleting it.

Never push a merge commit to protected `develop` or force-update a ref without
explicit named-ref approval.
