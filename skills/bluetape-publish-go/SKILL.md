---
name: bluetape-publish-go
description: Use when planning, validating, executing, recovering, or closing a Go module tag, GitHub Release, milestone, main promotion, or downstream Go consumer update in the bluetape ecosystem.
---

# bluetape4k Publish Go

## Parent and Safety Contract

Use `bluetape-workflow` for Step DoD, first-plan approval, GitHub metadata,
and side-effect authority; use `bluetape-go-patterns` for Go P0/P1 preflight.
This skill is for Go modules without Maven/Gradle/BOM/catalog/snapshot trains.

Tag creation/push, GitHub Release, PR delivery/merge, milestone/issue close, and
remote branch deletion are external side effects. PR authority, head publish,
creation, review, and merge-ready reporting use CG-11 through CG-15. Every PR
merge requires fresh post-report approval through CG-16 before CG-17/18,
regardless of earlier release scope. Other irreversible actions use CG-X01
immediately before the exact action and only when explicitly requested or
included in current approved release scope. Never rewrite a remote tag without
an explicit old-object/new-object retag plan.

## Reference Routing

| Phase | Required reference |
| --- | --- |
| stable release or release PR | `references/stable-release.md` |
| direct `develop -> main` PR is conflicting | `references/protected-branch-fallback.md` in addition |
| downstream consumers, cleanup, or existing-tag repair | `references/downstream-and-recovery.md` |

Read repo-local `docs/release.md`, `Makefile`, workflows, tags, releases, and
branch protection. Never import JVM release assumptions.

## Flow Classifier

- `release-preflight`: assess/prepare gates without publishing.
- `milestone-close`: close completed issue/Epic/milestone scope.
- `stable-release`: promote, tag, and create a non-prerelease GitHub Release.
- `release-hygiene-backfill`: existing tag lacks release/changelog hygiene.

## Mandatory Preflight Checklist

Apply `bluetape-workflow/references/checklist-contract.md` and collect fresh
evidence.

- [ ] **GO-PRE-01 — Pin repository state**
  - **Action:** Inspect status, fetch `main`/`develop`/tags, and compare `origin/main..origin/develop`.
  - **Evidence:** Clean/preserved tree, exact branch SHAs, commit range, and intended tag commit.
  - **Failure:** Dirty, unknown, or ambiguous target state blocks release work.
- [ ] **GO-PRE-02 — Close live release work**
  - **Action:** Inspect the milestone, open issues, open PRs, and release-affecting unmilestoned work.
  - **Evidence:** Live URLs/results with every relevant item closed or dispositioned.
  - **Failure:** Keep milestone/tag/release actions blocked.
- [ ] **GO-PRE-03 — Prove tag and release absence**
  - **Action:** Check local tags, remote tags including dereferenced refs, and GitHub Releases for the exact version.
  - **Evidence:** Fresh absence results from all three authorities.
  - **Failure:** Treat an existing tag as immutable and route to hygiene recovery.
- [ ] **GO-PRE-04 — Verify changelog on the target commit**
  - **Action:** Read the target `CHANGELOG.md` section from the exact commit that would be tagged.
  - **Evidence:** `## [v<version>] - <date>` and reader-usable content on the target SHA.
  - **Failure:** Create the history fix before tagging; do not rely on another branch's working tree.
- [ ] **GO-PRE-05 — Load repository release policy**
  - **Action:** Read repo-local release guide, Make targets, workflows, and branch protection.
  - **Evidence:** Exact paths and resolved promotion/tag rules.
  - **Failure:** Do not import JVM or remembered release assumptions.
- [ ] **GO-PRE-06 — Converge Go P0/P1 review**
  - **Action:** Apply `bluetape-go-patterns` to the exact release commit and repair blockers.
  - **Evidence:** Latest review with P0=0 and P1=0.
  - **Failure:** Keep promotion and tagging blocked.
- [ ] **GO-PRE-07 — Pass local release validation**
  - **Action:** Run `make ci` or the repository-defined formatter, lint, vet, test, and race commands, serializing heavyweight infrastructure.
  - **Evidence:** Fresh successful local command outputs on the target commit.
  - **Failure:** Diagnose and repair; a retry-only pass needs lifecycle evidence.
- [ ] **GO-PRE-08 — Match GitHub CI to the release commit**
  - **Action:** Inspect required GitHub checks for the exact target SHA and current reviews/threads.
  - **Evidence:** Successful required checks and no unresolved blocking review on the target commit.
  - **Failure:** Pending, stale, missing, failed, or superseded CI blocks release.

Serialize Testcontainers-backed validation. Do not tag `develop` when policy
requires `main`, and do not create a release whose source archive lacks the
matching changelog without explicitly documenting an approved hygiene backfill.

## Milestone Close

Instantiate these rows when milestone close is selected:

- [ ] **GO-MILE-01 — Verify close prerequisites and authority**
  - **Action:** Prove milestone issues=0 except the closing Epic, implementation PRs merged, no open PR closes scoped issues, changelog gate satisfied or a history PR exists, and exact current authority exists for the planned Epic update/comment and close targets.
  - **Evidence:** Live milestone/issue/PR results, changelog state, exact Epic and milestone targets, and authority record.
  - **Failure:** Stop all milestone mutations until scope, prerequisites, and authority are current.
- [ ] **GO-MILE-02 — Update and verify the Epic checklist**
  - **Action:** Update only the authorized Epic checklist with final child-issue state, then read back the live body.
  - **Evidence:** Epic URL, before/after checklist state, and verified live body.
  - **Failure:** Repair the Epic body before posting or closing anything else.
- [ ] **GO-MILE-03 — Post and verify the closure comment**
  - **Action:** Post the authorized closure comment with child issues, local/CI evidence, and changelog/tag/release state, then read it back live.
  - **Evidence:** Comment URL/body and verified live issue timeline.
  - **Failure:** Repair the comment before closing the Epic or milestone.
- [ ] **GO-MILE-04 — Close and verify the Epic**
  - **Action:** After a new CG-X01 instance passes for the exact Epic close, close the Epic and read back its live state.
  - **Evidence:** Exact-action hold, Epic URL, closed state, and close timestamp.
  - **Failure:** Keep the Epic open/PENDING without current authority; repair any failed close before the milestone.
- [ ] **GO-MILE-05 — Close and verify the milestone**
  - **Action:** After a new CG-X01 instance passes for the exact milestone close, close the milestone and read back its live state.
  - **Evidence:** Exact-action hold, milestone URL, closed state, and close timestamp.
  - **Failure:** Keep the milestone open/PENDING without current authority; never infer it from the Epic close.

## Stable Release Summary

Load `stable-release.md` and execute its exact promotion/tag/release order. The
irreversible hold immediately before tagging re-verifies target commit,
changelog, tag/release absence, CI, and user authority. Signed annotated tags
must carry a concise Lore decision record. Verify the tag object and dereferenced
commit independently from GitHub Release metadata.

GitHub Release notes use the public quality contract from
`bluetape-publish-jvm/references/release-notes.md`: highlights, reader-meaningful
groups, traceability, validation, and correct final compare link.

## Fail-Closed Rules

- Dirty/unknown target tree, open release-affecting work, missing changelog,
  failed P0/P1/CI, existing tag/release, or ambiguous target commit blocks tag.
- A conflicting direct release PR uses the documented protected-branch fallback;
  never force-push or add a merge commit to protected `develop` by improvising.
- GitHub `targetCommitish` is not tag proof; compare the dereferenced tag SHA.
- Existing published tag is immutable by default; repair missing GitHub metadata
  around it rather than moving it.

## Completion

Report preflight, milestone state, changelog, P0/P1, local validation, CI,
promotion PR, tag object/dereferenced SHA, GitHub Release URL/target, downstream
status, local sync/cleanup, residual risk, and whether any tag was created,
pushed, rewritten, or left untouched. Use the parent Step DoD table.

Completion requires all applicable GO-PRE rows and every selected reference
row to be checked, with `Required checks: X/Y; N/A: N; Blocked: 0` and X=Y.
