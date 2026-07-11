# Go Stable Release Procedure

Use when repo policy promotes `develop -> main -> tag`. Apply the parent
checklist contract.

- [ ] **GO-REL-01 — Pass preflight**
  - **Action:** Complete all GO-PRE rows for milestone/open work, changelog, target SHA, absence, validation, review, and CI.
  - **Evidence:** Preflight X=Y with Blocked=0 on the exact candidate.
  - **Failure:** Do not open or merge the release PR.
- [ ] **GO-REL-02 — Open the promotion PR**
  - **Action:** Open `main <- develop` with scope, validation, milestone, tag plan, metadata, and final `## DoD Status`.
  - **Evidence:** Live verified PR body, assignee, labels, milestone, base, and head.
  - **Failure:** Repair live metadata/body before review or merge.
- [ ] **GO-REL-03 — Pass the promotion review gate**
  - **Action:** Wait for required checks and clean mergeability, then reread current reviews and unresolved threads.
  - **Evidence:** Live successful checks, mergeability, and no blocking review.
  - **Failure:** Fix/review again; route `CONFLICTING` to the fallback checklist.
- [ ] **GO-REL-04 — Merge only with authority**
  - **Action:** Merge the promotion PR only when the approved release scope explicitly authorizes it.
  - **Evidence:** Authority record and live merged PR state.
  - **Failure:** Stop at PR-ready state without merge authority.
- [ ] **GO-REL-05 — Synchronize and revalidate main**
  - **Action:** Fetch, fast-forward local `main`, and re-read the target changelog section from `origin/main`.
  - **Evidence:** Local/origin main SHA parity and matching changelog section.
  - **Failure:** Do not tag a stale or mismatched checkout.
- [ ] **GO-REL-06 — Refresh the irreversible tag hold**
  - **Action:** Immediately recheck `origin/main` SHA, clean state, changelog, CI, tag/release absence, and tag authority.
  - **Evidence:** Timestamped live evidence newer than the merge.
  - **Failure:** Any stale, unknown, missing, pending, or failed row blocks tag creation.
- [ ] **GO-REL-07 — Create the signed annotated tag**
  - **Action:** Create `v<version>` on `main` with a concise Lore decision record.
  - **Evidence:** Local annotated tag object, message, and dereferenced SHA equal to `HEAD` and `origin/main`.
  - **Failure:** Delete only the unpushed local tag created in this attempt; never move a remote tag.
- [ ] **GO-REL-08 — Push and verify the immutable tag**
  - **Action:** Push the exact tag and verify local/remote tag object plus dereferenced commit.
  - **Evidence:** `git ls-remote --tags` object and `^{}` SHA matching the checked commit.
  - **Failure:** Stop and recover without force-updating the remote ref.
- [ ] **GO-REL-09 — Create consumer-quality release notes**
  - **Action:** Create the GitHub Release from the changelog using the shared release-notes checklist.
  - **Evidence:** Live release with highlights, grouped changes, links, validation, tag commit, and correct compare link.
  - **Failure:** Keep GitHub closeout incomplete; do not move the tag to repair metadata.
- [ ] **GO-REL-10 — Verify release and tag identity**
  - **Action:** Compare release metadata with the independently dereferenced remote tag commit.
  - **Evidence:** `gh release view` plus remote annotated tag/object proof.
  - **Failure:** Edit release target metadata when needed; never normalize it by retagging.
- [ ] **GO-REL-11 — Report the release state**
  - **Action:** Report every release row, promotion evidence, tag object/SHA, release URL, side effects, and remaining downstream work.
  - **Evidence:** X=Y, Blocked=0 for completed scope and explicit tag status: untouched, created, pushed, or rewritten.
  - **Failure:** Do not claim released while any required row is unchecked.

For annotated tags, `targetCommitish` may initially show a branch. Verify:

- `git ls-remote --tags origin refs/tags/v<version> refs/tags/v<version>^{}`
- `gh release view v<version> --json tagName,targetCommitish,isDraft,isPrerelease,url`

If metadata target differs from the dereferenced commit, edit the release target
to that commit; never move the tag to normalize metadata.
