# Go Downstream, Cleanup, and Recovery

## Downstream Consumers

After the tag and GitHub Release exist, discover `go.mod` consumers of the
released module. In each clean repo, create a narrow branch, run `go get
<module>@v<version>`, `go mod tidy`, and repo tests; commit only `go.mod`/
`go.sum` unless code adaptation is required. Open/merge/sync PRs only within the
approved release scope.

- [ ] **GO-DOWN-01 — Discover and scope consumers**
  - **Action:** After tag and release existence, discover `go.mod` consumers and select only approved targets.
  - **Evidence:** Consumer inventory, current versions, clean repos, and explicit exclusions.
  - **Failure:** Do not mutate an unapproved or dirty consumer.
- [ ] **GO-DOWN-02 — Update and verify each consumer**
  - **Action:** On a narrow branch run `go get`, `go mod tidy`, and repository tests; limit changes to module files unless adaptation is required.
  - **Evidence:** Per-consumer diff, commands, tests, commit/PR state, and adaptation rationale when present.
  - **Failure:** Keep that consumer incomplete and report the exact test or adaptation blocker.

## Local Closeout

- release repo local `main`/`develop` match origin and are clean;
- merged temporary release/doc branches are removed locally/remotely only when
  deletion is authorized and ancestry proves safety;
- downstream default branches match origin and consume the target version;
- report remaining open PRs rather than claiming complete.

- [ ] **GO-DOWN-03 — Prove local and downstream closeout**
  - **Action:** Synchronize release and downstream default branches, remove temporary branches only with authority and ancestry proof, and enumerate remaining PRs.
  - **Evidence:** Local/origin SHA parity, clean status, consumer target versions, deletion proof, and open-PR list.
  - **Failure:** Preserve unsafe branches/worktrees and report partial closeout.

## Hygiene Backfill

- Existing remote tag with no GitHub Release: create the release on that tag
  when authorized.
- Tag archive lacks changelog: do not rewrite by default; state the gap in
  notes and record where changelog was corrected.
- Current `develop` lacks the section: create a narrow changelog PR before any
  future tag.

Always report whether the tag was untouched, created, pushed, or rewritten.

- [ ] **GO-DOWN-04 — Repair immutable release hygiene**
  - **Action:** For an existing tag, create only missing authorized GitHub metadata, document changelog archive gaps, and fix current develop before future tags.
  - **Evidence:** Existing tag identity, release/backfill URL, changelog correction path, and explicit tag status.
  - **Failure:** Never rewrite the tag by default; stop without explicit old/new object authority.
