# Bluetape Skills 1.3.1 Release Checklist

## Release identity

| Field | Pinned value |
| --- | --- |
| Repository | `bluetape4k/bluetape-skills` |
| Flow / class | `stable-release` / single-repository GitHub skill bundle patch release |
| Target version / tag | `1.3.1` / `v1.3.1` |
| Latest observed external version | `v1.3.0`, published 2026-07-30 |
| Integration candidate | `develop` at `f07328ce241565035ea344af77a39b3c1da06c50` |
| Stable base | `main` at `8f1ae761cff03988004c7ccc9c0c732c62985225` (`v1.3.0`) |
| Preparation branch | `release/bluetape-skills-1.3.1` -> `develop` |
| Promotion branch | `release/promote-bluetape-skills-1.3.1` -> `main` |
| Authority | User approved the exact `v1.3.1` plan on 2026-08-07 |
| Artifact matrix | `bluetape-skills-1.3.1.tar.gz`, `bluetape-skills-1.3.1.zip`, `SHA256SUMS` |
| Consumer scope | Fresh tagged clone, archive extraction, full validator, and isolated fresh installation of all 14 canonical skills |
| Workflow dispatch | N/A — no `.github/workflows` publication workflow exists |
| Catalog / Maven / BOM role | N/A — source-only public GitHub skill bundle |

## Scope and release boundary

- The release promotes the already merged Korean-first project, contributor, code-comment, changelog, and release-note language policy.
- README.md and README.ko.md remain paired locale artifacts; identifiers, commands, URLs, exact errors, and machine tokens remain unchanged.
- The public distribution contains exactly 14 canonical `bluetape-*` skills and excludes private runtime state, hooks, memories, caches, secrets, and compatibility aliases.
- No open issue or pull request currently blocks this release.

## Required gates

- [x] **REL-01 — Pin live target and authority**
  - **Evidence:** `v1.3.0` is the latest release; `develop` and `main` SHAs are pinned above; user approved `v1.3.1`.
- [x] **REL-02 — Prepare release metadata**
  - **Evidence:** Korean `CHANGELOG.md` 1.3.1 entry, paired README v1.3.1 stable/update examples, this checklist, and the cached `.omx/RELEASE_RULE.md` are aligned; `git diff --check` and stale README version checks pass.
- [x] **REL-03 — Validate the develop candidate**
  - **Evidence:** Candidate commit `525f90d3adced49a15735fe93870cbec80383496` passed `./scripts/validate.sh` with `145 passed, 1 skipped, 159 subtests` plus 22 diagram tests; `git diff --check` and targeted stale-reference checks passed; tag-shaped tar.gz/zip archives passed SHA256SUMS verification, extraction, and the same validator; both archive installs yielded 14/14 canonical skills in isolated fresh Codex homes.
- [ ] **REL-04 — Deliver and merge the develop preparation PR**
  - **Action:** Push the exact branch, create a Korean PR ending in `## DoD Status`, wait for checks/review, and obtain fresh merge approval.
- [ ] **REL-05 — Promote the exact develop tree to main**
  - **Action:** Create the promotion PR from `main`, prove tree parity, wait for checks/review, and obtain fresh merge approval.
- [ ] **REL-06 — Refresh the immutable publication hold**
  - **Action:** Re-read `main` SHA, tag/release absence, signing configuration, and artifact plan immediately before tagging.
- [ ] **REL-07 — Create the signed tag and GitHub Release**
  - **Action:** Create/push signed annotated `v1.3.1`, build the three tag-derived assets, and create a non-prerelease GitHub Release with Korean notes.
- [ ] **REL-08 — Verify published consumers and close out**
  - **Action:** Verify live downloads, SHA256SUMS, extracted validators, fresh tagged clone installation, local branch parity, and safe cleanup.

## Dispatch hold

Refresh immediately before tag and release creation.

| Hold | State |
| --- | --- |
| `v1.3.1` tag absent locally and remotely | PASS before preparation; refresh required before tag |
| `v1.3.1` GitHub Release absent | PASS before preparation; refresh required before release |
| Exact `main` candidate | PENDING promotion merge |
| SSH-signed annotated tag capability | PASS: local SSH signing configuration present; verification required on candidate tag |
| Tag-derived archives and checksums | PENDING exact-tag build |
| Extracted validators and fresh installs | PENDING exact-tag proof |

## Stop condition

Do not tag or create the GitHub Release while an applicable gate or hold is unchecked, pending, stale, or failed. After publication, verify the exact live tag, release body, all three assets, both archive digests/downloads, extracted validators, and isolated fresh installs before reporting completion.
