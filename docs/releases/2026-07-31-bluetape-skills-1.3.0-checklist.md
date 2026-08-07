# Bluetape Skills 1.3.0 Release Checklist

## Release identity

| Field | Pinned value |
| --- | --- |
| Repository | `bluetape4k/bluetape-skills` |
| Flow / class | `stable-release` / single-repository GitHub skill bundle minor release |
| Target version / tag | `1.3.0` / `v1.3.0` |
| Latest observed external version | `v1.2.2`, published 2026-07-27 |
| Integration candidate | `develop` at `e278d7ab7c0b166e0a262b312e6007e9a21943a8` before release preparation |
| Stable base | `main` at `1f1c677ff8b885687be83e1cc924449a88aa212a` (`v1.2.2`) |
| Preparation branch | `release/bluetape-skills-1.3.0` -> `develop` |
| Promotion branch | `release/promote-bluetape-skills-1.3.0` -> `main` |
| Authority | User requested a new release and approved this exact `v1.3.0` plan on 2026-07-31 |
| Artifact matrix | `bluetape-skills-1.3.0.tar.gz`, `bluetape-skills-1.3.0.zip`, `SHA256SUMS` |
| Consumer scope | Fresh tagged clone, archive extraction, full validator, and isolated fresh installation of all 14 canonical skills |
| Catalog / Maven / BOM role | N/A — source-only public GitHub skill bundle |
| Workflow dispatch | N/A — no `.github/workflows` publication workflow exists |

## Scope and topology

- The public distribution contains exactly 14 canonical `bluetape-*` skills. `bluetape-publish-kotlin` remains a local compatibility alias and is excluded.
- The public `develop` bundle is content-equivalent to the maintained live canonical directories, except for the intentional public-only portability guard in `bluetape-workflow/tests/test_manifest_contract.py`.
- PR #13 (`docs/repository-authority-boundary`) remains open and out of scope because it has a separate head and lacks fresh merge approval.
- The release has one repository and no Maven, catalog, snapshot, or downstream stable dependency edges.
- `v1.2.2` release metadata exists on `main` but was not synchronized back to `develop`; this release restores that historical changelog entry before adding the `1.3.0` record.

## Required gates

- [x] **REL-01 — Pin target inventory**
  - **Action:** Preserve the identity table values in every release action.
  - **Evidence:** This checklist pins `1.3.0`, `v1.3.0`, `v1.2.2`, the candidate/base SHAs, three assets, authority, and 14-skill consumer scope.
  - **Failure:** Stop before release preparation or publication.
- [x] **REL-02 — Reconfirm live release state**
  - **Action:** Re-read releases, tags, PRs, branch/ruleset state, and exclusions.
  - **Evidence:** Fresh `gh release list` reports `v1.2.2` as Latest; local/remote tag and GitHub Release lookups for `v1.3.0` are absent; PR #13 remains open at `9912fbef` and excluded.
  - **Failure:** Replan if live state changes.
- [x] **REL-03 — Export canonical bundle**
  - **Action:** Export the 14 live canonical skills and restore the intentional public portability guard.
  - **Evidence:** `export-bluetape-skills` exported 14 directories; after restoring the public-only manifest guard, `git diff --name-only` contains no `skills/` paths.
  - **Failure:** Stop on unexpected content or boundary drift.
- [x] **REL-04 — Prepare public release metadata**
  - **Action:** Restore `1.2.2` history, add `1.3.0` release notes, update both README install examples, and preserve EN/KO parity.
  - **Evidence:** `CHANGELOG.md` contains dated `1.2.2` and `1.3.0` entries/links; README EN/KO stale-version searches are empty and matching `v1.3.0` examples were reviewed.
  - **Failure:** Repair stale or mismatched public documentation.
- [x] **REL-05 — Validate candidate**
  - **Action:** Run `./scripts/validate.sh`, `git diff --check`, and targeted release-reference checks.
  - **Evidence:** `./scripts/validate.sh`: 144 passed, 1 skipped, 159 subtests; 22 diagram tests passed; `git diff --check` and target-version reference checks passed.
  - **Failure:** Repair and rerun affected proof.
- [x] **REL-06 — Verify archive consumers**
  - **Action:** Build both archives from the exact candidate, verify checksums, extract, validate, and fresh-install all canonical skills into isolated homes.
  - **Evidence:** Both exact-candidate archives passed `144 passed, 1 skipped, 159 subtests` plus 22 diagram tests after extraction; SHA-256 verification and isolated fresh installation each produced 14/14 canonical skills.
  - **Failure:** Do not open the release-preparation PR.
- [ ] **REL-07 — Deliver preparation PR**
  - **Action:** Push the exact preparation head and create/verify its `develop` PR with a Korean body ending in `## DoD Status`.
  - **Evidence:** Live PR metadata, exact head, current reviews/threads, and validator result.
  - **Failure:** Repair live delivery before merge-ready reporting.
- [ ] **REL-08 — Hold for preparation merge approval**
  - **Action:** Report the exact PR/head merge-ready and wait for fresh user approval.
  - **Evidence:** Approval issued after the merge-ready report.
  - **Failure:** PENDING; never merge or auto-merge.
- [ ] **REL-09 — Promote exact develop tree**
  - **Action:** Create the promotion branch from `main`, materialize the approved merged `develop` tree, and prove tree parity.
  - **Evidence:** Exact merge SHA and empty tree diff against merged `develop`.
  - **Failure:** Repair divergence before promotion PR creation.
- [ ] **REL-10 — Deliver promotion PR**
  - **Action:** Push and verify the `main` promotion PR, then report exact-head merge-ready.
  - **Evidence:** Live PR metadata, exact head, ruleset compliance, no blockers.
  - **Failure:** PENDING or repair; no auto-merge.
- [ ] **REL-11 — Hold for promotion merge approval**
  - **Action:** Wait for fresh user approval after promotion merge-ready reporting.
  - **Evidence:** Approval issued for the exact promotion PR/head.
  - **Failure:** PENDING; do not tag or publish.
- [ ] **REL-12 — Refresh irreversible hold**
  - **Action:** Immediately before tagging, re-read main SHA, tag/release absence, signing configuration, assets, and release authority.
  - **Evidence:** Timestamped fresh hold with all rows PASS.
  - **Failure:** Block tag and GitHub Release.
- [ ] **REL-13 — Create immutable release**
  - **Action:** Create and push an SSH-signed annotated `v1.3.0` tag, build tag-derived assets, and create the non-prerelease GitHub Release.
  - **Evidence:** Tag object/target/signature, live release body, and three uploaded assets.
  - **Failure:** Never retag; use a corrective patch if immutable content is wrong.
- [ ] **REL-14 — Verify published consumers and close out**
  - **Action:** Download assets, verify digests, extract/validate, fresh-install, synchronize local branches, and remove only approved proven-merged release worktrees/branches.
  - **Evidence:** Live downloads, validation results, synchronized SHAs, and cleanup list.
  - **Failure:** Keep release status partial and preserve ambiguous local state.

## Dispatch hold

Refresh immediately before tag and release creation.

| Hold | Current state |
| --- | --- |
| `v1.3.0` tag absent locally and remotely | PASS before preparation; refresh required before tag |
| `v1.3.0` GitHub Release absent | PASS before preparation; refresh required before release |
| Exact `main` candidate | PENDING promotion merge |
| Signed annotated tag capability | PENDING candidate-signing check |
| Tag-derived archives and checksums | PENDING exact-tag build |
| Extracted validators and fresh installs | PENDING exact-tag proof |
| Open release-affecting work dispositioned | PASS: PR #13 excluded |

## Stop condition

Do not tag or create the GitHub Release while an applicable gate or hold is unchecked, pending, stale, or failed. After publication, verify the exact live tag, release body, all three assets, both archive digests/downloads, extracted validators, and isolated fresh installs before reporting release completion.
