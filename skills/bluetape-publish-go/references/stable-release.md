# Go Stable Release Procedure

Use when repo policy promotes `develop -> main -> tag`. Apply the parent
checklist contract.

- [ ] **GO-REL-01 — Pass preflight**
  - **Action:** Complete all GO-PRE rows for milestone/open work, changelog, target SHA, absence, validation, review, and CI.
  - **Evidence:** Preflight X=Y with Blocked=0 on the exact candidate.
  - **Failure:** Do not open or merge the release PR.
- [ ] **GO-REL-02 — Publish and open the promotion PR**
  - **Action:** After parent CG-01 through CG-10 pass, complete CG-11 through CG-13 for `main <- develop`: verify exact authority, publish/read back the head, then create or update and live-verify the promotion PR with scope, validation, milestone, tag plan, metadata, and final `## DoD Status`.
  - **Evidence:** Common gate evidence, matching local/remote/PR head, and live verified PR body, assignee, labels, milestone, base, and head.
  - **Failure:** Stop at the applicable common gate and repair authority, publication, or live PR metadata before review.
- [ ] **GO-REL-03 — Pass the promotion review gate**
  - **Action:** Complete CG-14: wait for exact-head required checks and clean mergeability, then reread current reviews, unresolved threads, and applicable human artifacts.
  - **Evidence:** Live successful checks, exact head, mergeability, no blocking review, and artifact decisions.
  - **Failure:** PENDING waits; fix/review again on failure and route `CONFLICTING` to the fallback checklist.
- [ ] **GO-REL-04 — Report the promotion PR merge-ready**
  - **Action:** Complete CG-15 with a user-visible exact-head report containing preflight, CI, current review, lesson, release artifacts, phase-aware counts, and unchecked CG-16 through CG-18.
  - **Evidence:** Merge-ready report for the exact PR/head with reconciled counts and Blocked=0.
  - **Failure:** Repair missing/stale evidence before requesting merge approval.
- [ ] **GO-REL-05 — Obtain fresh promotion merge approval**
  - **Action:** Complete CG-16 only after GO-REL-04 is visible; wait for fresh explicit approval of the exact promotion PR/head.
  - **Evidence:** Post-report user approval and refreshed irreversible hold.
  - **Failure:** Waiting is PENDING; refusal or invalid authority is BLOCKED. Earlier release scope never counts.
- [ ] **GO-REL-06 — Merge and verify the promotion PR**
  - **Action:** Complete CG-17 after CG-16 passes by merging with the approved strategy and reading back the live merged state/SHA.
  - **Evidence:** Merge command/URL, strategy, live merged state, and merge SHA.
  - **Failure:** Stop and repair; never enable auto-merge or merge another head.
- [ ] **GO-REL-07 — Synchronize and revalidate main**
  - **Action:** Complete CG-18 by fetching, fast-forwarding local `main`, cleaning only proven merged branch/worktree state, and rereading the target changelog section from `origin/main`.
  - **Evidence:** Local/origin main SHA parity and matching changelog section.
  - **Failure:** Do not tag a stale or mismatched checkout.
- [ ] **GO-REL-08 — Refresh the irreversible tag hold**
  - **Action:** Immediately recheck `origin/main` SHA, clean state, changelog, CI, tag/release absence, and tag authority through CG-X01 for the exact local tag action.
  - **Evidence:** Timestamped live evidence newer than the merge.
  - **Failure:** Any stale, unknown, missing, pending, or failed row blocks tag creation.
- [ ] **GO-REL-09 — Create the signed annotated tag**
  - **Action:** Create `v<version>` on `main` with a concise Lore decision record.
  - **Evidence:** Local annotated tag object, message, and dereferenced SHA equal to `HEAD` and `origin/main`.
  - **Failure:** Delete only the unpushed local tag created in this attempt; never move a remote tag.
- [ ] **GO-REL-10 — Push and verify the immutable tag**
  - **Action:** After a new CG-X01 instance passes for the exact remote tag push, push the tag and verify local/remote tag object plus dereferenced commit.
  - **Evidence:** `git ls-remote --tags` object and `^{}` SHA matching the checked commit.
  - **Failure:** Stop and recover without force-updating the remote ref.
- [ ] **GO-REL-11 — Create consumer-quality release notes**
  - **Action:** After a new CG-X01 instance passes for the exact GitHub Release action, create the release from the changelog using the shared release-notes checklist.
  - **Evidence:** Live release with highlights, grouped changes, links, validation, tag commit, and correct compare link.
  - **Failure:** Keep GitHub closeout incomplete; do not move the tag to repair metadata.
- [ ] **GO-REL-12 — Inspect release and tag identity**
  - **Action:** Compare release metadata with the independently dereferenced remote tag commit and classify exact match or the metadata-only correction needed.
  - **Evidence:** `gh release view`, remote annotated tag/object proof, and match or correction decision.
  - **Failure:** Stop on unknown tag identity or a mismatch not repairable by metadata alone; never normalize by retagging.
- [ ] **GO-REL-13 — Repair mismatched release metadata when authorized**
  - **Action:** When GO-REL-12 identifies a metadata-only mismatch, edit only the GitHub Release target after a new CG-X01 instance passes for that exact edit and read it back; otherwise record N/A.
  - **Evidence:** Exact-action hold, before/after release metadata and live readback, or concrete no-mismatch N/A evidence.
  - **Failure:** Keep the repair PENDING/BLOCKED without authority; never move the tag or continue to final identity proof.
- [ ] **GO-REL-14 — Verify final release and tag identity**
  - **Action:** Compare the final live release metadata with the independently dereferenced remote tag commit after GO-REL-13 PASS/N/A.
  - **Evidence:** Final `gh release view`, remote annotated tag/object proof, and exact commit match.
  - **Failure:** Keep release closeout incomplete; return to a newly authorized forward repair plan rather than retagging.
- [ ] **GO-REL-15 — Report the release state**
  - **Action:** Report every release row, promotion evidence, tag object/SHA, release URL, side effects, and remaining downstream work.
  - **Evidence:** X=Y, Blocked=0 for completed scope and explicit tag status: untouched, created, pushed, or rewritten.
  - **Failure:** Do not claim released while any required row is unchecked.

For annotated tags, `targetCommitish` may initially show a branch. Verify:

- `git ls-remote --tags origin refs/tags/v<version> refs/tags/v<version>^{}`
- `gh release view v<version> --json tagName,targetCommitish,isDraft,isPrerelease,url`

If metadata target differs from the dereferenced commit, use GO-REL-13 and then
GO-REL-14; never move the tag to normalize metadata.
