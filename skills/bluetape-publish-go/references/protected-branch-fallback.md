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
- [ ] **GO-FB-06 — Deliver the replacement PR**
  - **Action:** Open the replacement PR to `main`, pass CI/reviews, and merge only with approved authority.
  - **Evidence:** Live PR metadata/body/checks/reviews and merge authority/state.
  - **Failure:** Keep the fallback unmerged until all live gates pass.
- [ ] **GO-FB-07 — Synchronize safely**
  - **Action:** Fast-forward `main`; restore a failed local `develop` attempt only when this fallback created it and no user work can be lost.
  - **Evidence:** Local/origin parity and ancestry/ownership proof for any restoration.
  - **Failure:** Preserve ambiguous local state and report the blocker.

Never push a merge commit to protected `develop` or force-update a ref without
explicit named-ref approval.
