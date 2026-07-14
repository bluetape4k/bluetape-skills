# Go Downstream, Cleanup, and Recovery

## Downstream Consumers

After the tag and GitHub Release exist, discover `go.mod` consumers of the
released module. In each clean repo, create a narrow branch, run `go get
<module>@v<version>`, `go mod tidy`, and repo tests; commit only `go.mod`/
`go.sum` unless code adaptation is required. Instantiate a separate CG-11
through CG-18 checklist for each consumer PR. Release scope may authorize PR
publication through CG-15, but every consumer merge needs fresh exact-head
approval at CG-16.

- [ ] **GO-DOWN-01 — Discover and scope consumers**
  - **Action:** After tag and release existence, discover `go.mod` consumers and select only approved targets.
  - **Evidence:** Consumer inventory, current versions, clean repos, and explicit exclusions.
  - **Failure:** Do not mutate an unapproved or dirty consumer.
- [ ] **GO-DOWN-02 — Update and verify each consumer**
  - **Action:** On a narrow branch run `go get`, `go mod tidy`, and repository tests; limit changes to module files unless adaptation is required, complete the lesson decision, review, and local commit before remote delivery.
  - **Evidence:** Per-consumer diff, commands, tests, lesson result, review, local commit, and adaptation rationale when present.
  - **Failure:** Keep that consumer incomplete and report the exact test or adaptation blocker.
- [ ] **GO-DOWN-03 — Deliver each authorized consumer PR**
  - **Action:** For each consumer independently, complete CG-11 through CG-15: verify authority, publish/read back the exact head, create or update and verify the PR, pass exact-head CI/current review and artifacts, then report merge-ready. Record CG-11 through CG-18 N/A when that consumer has no PR delivery.
  - **Evidence:** Per-consumer matching local/remote/PR head, live metadata/body, successful checks, review/artifacts, phase-aware counts, and user-visible merge-ready report; or concrete no-PR N/A evidence.
  - **Failure:** Keep only the affected consumer PENDING or FAIL; do not reuse another consumer's authority or evidence.
- [ ] **GO-DOWN-04 — Merge each consumer only after fresh approval**
  - **Action:** For each delivered consumer PR, complete CG-16 through CG-18 only after fresh approval of its current GO-DOWN-03 report: record approval, merge/verify, then sync and clean proven merged state. Record N/A for consumers without PR delivery.
  - **Evidence:** Per-consumer exact-head post-report approval, merge result/SHA, default-branch sync, and cleanup result; or matching no-PR N/A evidence.
  - **Failure:** Waiting at CG-16 is PENDING; invalid authority is BLOCKED, merge failure returns to repair, and cleanup ambiguity remains PENDING with state preserved.

## Local Closeout

- release repo local `main`/`develop` match origin and are clean;
- merged temporary release/doc branches are removed locally only when ancestry
  proves safety; remote deletion is handled separately by GO-DOWN-10;
- downstream default branches match origin and consume the target version;
- report remaining open PRs rather than claiming complete.

- [ ] **GO-DOWN-05 — Prove local and downstream closeout**
  - **Action:** Synchronize release and downstream default branches, remove only proven merged local temporary branches/worktrees, and enumerate remaining PRs and remote cleanup candidates.
  - **Evidence:** Local/origin SHA parity, clean status, consumer target versions, local ancestry/cleanup proof, remote candidate list, and open-PR list.
  - **Failure:** Preserve unsafe branches/worktrees and report partial closeout.

## Hygiene Backfill

- Existing remote tag with no GitHub Release: create the release on that tag
  when authorized.
- Tag archive lacks changelog: do not rewrite by default; state the gap in
  notes and record where changelog was corrected.
- Current `develop` lacks the section: create a narrow changelog PR before any
  future tag.

Always report whether the tag was untouched, created, pushed, or rewritten.

- [ ] **GO-DOWN-06 — Assess immutable release hygiene**
  - **Action:** For an existing tag, verify tag identity, missing GitHub metadata, archive changelog gaps, and whether current `develop` needs a correction; record the exact repair plan without mutation.
  - **Evidence:** Existing tag identity, live release result, changelog gap locations, correction target/base/head, and explicit tag status.
  - **Failure:** Never rewrite the tag by default; stop without an evidence-backed repair plan.
- [ ] **GO-DOWN-07 — Backfill and verify missing GitHub Release metadata**
  - **Action:** When GO-DOWN-06 proves metadata missing, create only that metadata on the immutable tag and read it back live after a new CG-X01 instance passes for the exact GitHub Release creation; otherwise record N/A.
  - **Evidence:** Exact-action hold, release/backfill URL and metadata, independently verified tag identity, or concrete N/A evidence.
  - **Failure:** Keep backfill PENDING/BLOCKED without authority; never move the tag to repair metadata.
- [ ] **GO-DOWN-08 — Deliver a required changelog correction PR**
  - **Action:** When current `develop` needs correction, instantiate a separate PR checklist and complete CG-11 through CG-15 for its exact repo/base/head; otherwise record CG-11 through CG-18 and GO-DOWN-08 N/A.
  - **Evidence:** Matching local/remote/PR head, live body, checks/review/artifacts, exact-head merge-ready report, or concrete no-correction N/A evidence.
  - **Failure:** Keep the correction PENDING at its applicable gate; do not fold it into release metadata backfill.
- [ ] **GO-DOWN-09 — Merge the changelog correction only after fresh approval**
  - **Action:** For a delivered correction PR, complete CG-16 through CG-18 only after fresh approval of its current GO-DOWN-08 report; otherwise record N/A.
  - **Evidence:** Post-report exact-head approval, merge result/SHA, develop sync/cleanup, or matching N/A evidence.
  - **Failure:** Waiting at CG-16 is PENDING; invalid authority is BLOCKED, merge failure returns to repair, and cleanup ambiguity remains PENDING.
- [ ] **GO-DOWN-10 — Delete each authorized remote temporary branch**
  - **Action:** For each remote cleanup candidate independently, delete only after ancestry/ownership proof and a new CG-X01 instance passes naming the exact remote ref, then read back remote absence; otherwise retain and report it.
  - **Evidence:** Per-ref ancestry and ownership proof, exact-action hold, deletion result, remote absence check, and retained-ref list.
  - **Failure:** Preserve any ambiguous or unauthorized ref as PENDING; never batch-delete under generic release scope.
