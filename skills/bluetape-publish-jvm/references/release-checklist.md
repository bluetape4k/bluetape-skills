# Release Checklist and Recovery

Create or refresh a durable checklist before any stable tag/dispatch,
publication, GitHub Release, or milestone close. Chat/WIP history is not the
checklist.

## Required Checklist

- [ ] **REL-01 — Pin the target inventory**
  - **Action:** Record repo, version, release class, branch/SHA, artifact/BOM matrix, catalog role, generated-POM MIT license or written exception, target authority, and consumer scope.
  - **Evidence:** Fresh values from the authoritative source for every field.
  - **Failure:** Unknown, inferred, or stale identity blocks every downstream row.
- [ ] **REL-02 — Close issue and PR state**
  - **Action:** Inspect the matching milestone plus all release/version/catalog/BOM issues, target-branch PRs, and release-affecting unmilestoned PRs.
  - **Evidence:** Milestone open issues=0 and every other live item closed or explicitly dispositioned.
  - **Failure:** Keep release blocked until live work is resolved or removed from approved scope.
- [ ] **REL-03 — Prove the snapshot train**
  - **Action:** Test the complete upstream-to-downstream topology with the same catalog/dependency state using local resolution, compile/tests, required Nightly/full, and snapshots.
  - **Evidence:** Exact SHAs, catalog state, commands, run URLs, metadata timestamps, and complete snapshot artifact matrix.
  - **Failure:** Do not promote mismatched, incomplete, or unverifiable snapshot evidence.
- [ ] **REL-04 — Validate stable batches**
  - **Action:** Confirm every DAG prerequisite is public, shared catalog mutation is absent, and downstream stable consumers wait for Central HTTP 200.
  - **Evidence:** Acyclic batch plan and public prerequisite URLs/statuses.
  - **Failure:** Serialize or reorder the batch; never release downstream from portal acceptance alone.
- [ ] **REL-05 — Pass the dependencies final gate**
  - **Action:** Verify every internal BOM is non-SNAPSHOT and Central-visible, generated catalog/artifacts are valid, workspace-root sync was correct, and publication matrix is complete.
  - **Evidence:** Central POM/artifact checks plus generated output and workspace-root evidence; catalog ref recorded only as a build-contract source.
  - **Failure:** Block final BOM publication on any SNAPSHOT, missing version/artifact, invalid license, or catalog/version authority confusion.
- [ ] **REL-06 — Synchronize consumers**
  - **Action:** After dependencies BOM HTTP 200, inspect the five named consumers or record concrete exclusions, align governed aliases/coordinates, and run resolution plus repo-level tests.
  - **Evidence:** Per-consumer target version, diff, resolution, tests, and explicit exclusions.
  - **Failure:** Gradle `help` alone is partial; retarget superseded branches and complete repository tests.
- [ ] **REL-07 — Open the next development line**
  - **Action:** After stable closeout, set the approved next `baseVersion`, keep `snapshotVersion=` empty, publish the exact `develop` SHA snapshot, verify metadata, and update direct unreleased consumers.
  - **Evidence:** Source diff/SHA, workflow URL, snapshot metadata, and consumer mapping, or concrete evidence that this row is outside approved scope.
  - **Failure:** Never leave stable dependency branches on SNAPSHOT or point consumers at a future stable version.
- [ ] **REL-08 — Complete the public docs handoff**
  - **Action:** Update current install/baseline content and both locale indexes to the settled BOM and live Latest releases while preserving historical articles.
  - **Evidence:** Stale-version searches, Central POM, live Releases, diff check, and site build.
  - **Failure:** Keep documentation closeout blocked until current public guidance matches published reality.
- [ ] **REL-09 — Refresh the irreversible hold**
  - **Action:** Immediately before tag/dispatch, recheck open work, tag/release absence, workflow inputs, POM license/versions, SNAPSHOT absence, and artifact matrix.
  - **Evidence:** Timestamped live evidence gathered after the last mutable release event.
  - **Failure:** Any unknown, stale, changed, pending, or failed row blocks the irreversible action.

If a later immutable corrective patch appears, refresh the checklist and
retarget consumer branches before more tests/PRs. Do not silently keep the old
train version.

## Partial Publish Recovery

- Maven Central success consumes the version even if the workflow is cancelled.
  Never republish or move that tag.
- If artifacts are correct but GitHub Release creation failed, verify HTTP 200
  and create the release from the same tag when authorized.
- If POM/artifact metadata is wrong, document the partial state and publish the
  smallest corrective patch. That patch becomes the default consumer target
  unless the user selects another already-published version.

## Pressure Tests

- Corrective patch supersedes stale consumer branches: stop and retarget before
  validation.
- Consumer only ran Gradle `help`: mark partial and run repo tests.
- Consumer changed only the BOM while governed aliases drift: align actionable
  duplicates, then test.
- Site shows stale install/latest values: update current snippets and both
  locale indexes, while preserving historical narratives.
- User says the procedure is in the skill: reread and repair the named gate.
- Immutable POM mistake: never retag; use a corrective patch.
