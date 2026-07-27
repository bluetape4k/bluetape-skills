# Bluetape Skills 1.2.2 Release Checklist

## Release identity

| Field | Pinned value |
|---|---|
| Repository | `bluetape4k/bluetape-skills` |
| Flow / class | `stable-release` / single-repository GitHub bundle patch release |
| Target version | `1.2.2` |
| Target tag | `v1.2.2` |
| Latest observed external version | `v1.2.1` |
| Stable base | `main` at `fae0d7c0dcf971ef1856746dde002d2a595e2ba2` |
| Integration candidate | PR #14 head `a1accee5acf64a9368ca740c14300b090a5a89f3`, squash-merged as `92d8a1f907db6d1bb804928153308983df085780` |
| Release branch | `release/bluetape-skills-1.2.2` |
| Release authority | User explicitly requested PR #14 merge and `1.2.2` release on 2026-07-27 |
| Artifact matrix | `bluetape-skills-1.2.2.tar.gz`, `bluetape-skills-1.2.2.zip`, `SHA256SUMS` |
| Consumer scope | Fresh tagged clone, full validator, archive extraction, and fresh install of all 14 canonical skills |
| Catalog / Maven / BOM role | N/A — source-only public GitHub skill bundle |
| Signing | Signed release candidate commit and signed annotated immutable tag |
| Workflow dispatch | N/A — repository has no `.github/workflows` publication workflow |

## Live planning and topology

- Latest live release: `v1.2.1`, published 2026-07-16.
- Open release issues and milestones: none.
- PR #14 was approved at exact head `a1accee5` and merged into `develop` as
  `92d8a1f`.
- PR #13 remains open and is explicitly excluded from `v1.2.2`: it has a
  separate head and has not received fresh merge approval in this release
  request.
- Release graph has one repository and no Maven, catalog, snapshot, or
  downstream stable dependency edges.
- `main` remains aligned with `v1.2.1` until the reviewed release-promotion PR
  is merged.

## Candidate and public documentation scope

- PR #14 was merged only after exact-head review, thread, and check
  verification.
- This branch was refreshed from exact merged `develop` SHA `92d8a1f`.
- Move `CHANGELOG.md` Unreleased entries into a dated `1.2.2` section.
- Update stable installation and upgrade examples in `README.md` and
  `README.ko.md` from `v1.2.1` to `v1.2.2`.
- Update changelog comparison links to `v1.2.1...v1.2.2` and
  `v1.2.2...develop`.
- Preserve the committed workflow lesson from PR #14.

## Required release gates

| Check | Status | Evidence / next action |
|---|---|---|
| REL-01 Target inventory | PASS | Identity table above pins version, repo, branch, artifacts, authority, and consumers |
| REL-02 Issue and PR state | PASS | PR #14 merged as `92d8a1f`; PR #13 retained as an explicit exclusion |
| REL-03 Snapshot train | N/A | No snapshot publication exists |
| REL-04 Stable batches | N/A | One repository with no release edges |
| REL-05 Dependencies final gate | N/A | No Maven, BOM, catalog, or POM |
| REL-06 Consumer synchronization | N/A | No governed downstream release consumer; fresh installer proof is in-scope validation |
| REL-07 Next development line | N/A | No source version or snapshot line |
| REL-08 Public docs handoff | PASS | EN/KO stable install guidance and changelog identify `v1.2.2` |
| REL-09 Irreversible hold | PENDING | Refresh after release PR merge and immediately before tag/release creation |
| PRE-01 Release eligibility | PASS | Public canonical bundle patch release `1.2.2` |
| PRE-02 Live closeout | PASS | PR #14 is live as MERGED at exact approved head; PR #13 remains open and excluded |
| PRE-03 Release documentation | PASS | Dated reader-facing `1.2.2` changelog groups workflow, diagrams, patterns, and portability |
| PRE-04 Candidate execution | PASS | Full validator passed on candidate HEAD and both extracted archives; each fresh install produced 14/14 skills |
| PRE-05 Version state | PASS | README and changelog consistently identify `v1.2.2`; no stale `v1.2.1` README examples |
| PRE-06 Internal references | N/A | No internal artifact coordinates |
| PRE-07 BOM/POM audit | N/A | No generated BOM or POM |
| PRE-08 Signing diagnostics | PENDING | Candidate commit has a verified Good SSH signature; signed annotated tag remains gated on promotion merge |
| PRE-09 Artifact matrix | PASS | Candidate HEAD generated both pinned archives and `SHA256SUMS`; extraction and checksum inputs verified |
| PRE-10 Workflow inputs | N/A | No publication workflow |
| NOTE-01 Release purpose | PASS | Patch release publishes the maintained live skill improvements as a verified public bundle |
| NOTE-02 Reader organization | PASS | Changelog groups workflow, diagrams, language patterns, and maintenance guidance |
| NOTE-03 Traceability | PASS | Candidate includes PR #14 and its durable workflow lesson |
| NOTE-04 Corrective target | N/A | `1.2.2` is not an immutable-artifact corrective release |
| NOTE-05 Live body | PENDING | Verify final body and `v1.2.1...v1.2.2` comparison after publication |

## Dispatch hold

Refresh this block immediately before every irreversible action.

| Hold | Current evidence |
|---|---|
| `v1.2.2` tag absent | Pending live refresh |
| `v1.2.2` GitHub Release absent | Pending live refresh |
| Exact release PR merge SHA | Pending |
| `main` equals reviewed release candidate | Pending |
| Signed commit and tag diagnostics | Candidate commit Good SSH signature; tag pending promotion merge |
| Candidate archives and checksums | PASS for candidate HEAD; regenerate from immutable tag before upload |
| Extracted archive validators | PASS for both `tar.gz` and `.zip`: 144 passed, 1 source-only skip, 159 subtests |
| Fresh 14/14 installs | PASS from both extracted candidate archives |
| Open release-affecting work dispositioned | PR #14 merged; PR #13 retained outside scope |

## Stop condition

Do not create `v1.2.2` or publish a GitHub Release while any applicable
candidate, documentation, signing, archive, consumer, or hold row is pending or
failed. After publication, verify the live tag, release body, three asset
digests, HTTP downloads, extracted validators, and fresh tagged-clone install
before reporting the release complete.
