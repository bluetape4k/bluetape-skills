# Bluetape Skills 1.3.1 release checklist

## Release 식별 정보

| 항목 | 고정 값 |
| --- | --- |
| Repository | `bluetape4k/bluetape-skills` |
| Flow / class | `stable-release` / 단일 저장소 GitHub skill bundle patch release |
| Target version / tag | `1.3.1` / `v1.3.1` |
| Latest observed external version | `v1.3.0`, 2026-07-30 공개 |
| Integration candidate | `develop` at `f07328ce241565035ea344af77a39b3c1da06c50` |
| Stable base | `main` at `8f1ae761cff03988004c7ccc9c0c732c62985225` (`v1.3.0`) |
| Preparation branch | `release/bluetape-skills-1.3.1` -> `develop` |
| Promotion branch | `release/promote-bluetape-skills-1.3.1` -> `main` |
| Authority | 사용자가 2026-08-07에 정확한 `v1.3.1` 계획을 승인 |
| Artifact matrix | `bluetape-skills-1.3.1.tar.gz`, `bluetape-skills-1.3.1.zip`, `SHA256SUMS` |
| Consumer scope | tag clone, archive 추출, 전체 validator, 14개 canonical skill의 격리 fresh 설치 |
| Workflow dispatch | N/A — `.github/workflows` 공개 workflow 없음 |
| Catalog / Maven / BOM role | N/A — source-only 공개 GitHub skill bundle |

## 범위와 release 경계

- 이 release는 이미 merge된 프로젝트·contributor·code-comment·changelog·release-note의
  한국어 우선 언어 정책을 승격합니다.
- README.md와 README.ko.md는 paired locale artifact로 유지하며, identifier, command,
  URL, exact error, machine token은 변경하지 않습니다.
- 공개 배포에는 정확히 14개 canonical `bluetape-*` skill이 포함되고 private
  runtime state, hook, memory, cache, secret, compatibility alias는 제외됩니다.
- 현재 열린 issue나 pull request 중 이 release를 block하는 항목은 없습니다.

## 필수 gate

- [x] **REL-01 — Pin live target and authority**
  - **Evidence:** `v1.3.0`이 최신 release이며 `develop`과 `main` SHA를 위에
    고정했고 사용자가 `v1.3.1`을 승인했습니다.
- [x] **REL-02 — Prepare release metadata**
  - **Evidence:** 한국어 `CHANGELOG.md` 1.3.1 entry, paired README의 v1.3.1
    stable/update 예시, 이 checklist, cached `.omx/RELEASE_RULE.md`가 정렬됐고
    `git diff --check`와 stale README version check를 통과했습니다.
- [x] **REL-03 — Validate the develop candidate**
  - **Evidence:** candidate commit `525f90d3adced49a15735fe93870cbec80383496`가
    `./scripts/validate.sh`에서 `145 passed, 1 skipped, 159 subtests`와 diagram
    test 22개를 통과했습니다. `git diff --check`와 targeted stale-reference
    check도 통과했고, tag 형태 tar.gz/zip archive가 SHA256SUMS 검증·추출·동일
    validator를 통과했으며 두 archive 설치 모두 격리된 fresh Codex home에서
    canonical skill 14/14개를 만들었습니다.
- [ ] **REL-04 — Deliver and merge the develop preparation PR**
  - **Action:** 정확한 branch를 push하고 `## DoD Status`로 끝나는 한국어 PR을
    생성하며 check/review를 기다린 뒤 새 merge 승인을 받습니다.
- [ ] **REL-05 — Promote the exact develop tree to main**
  - **Action:** `main`에서 promotion PR을 만들고 tree parity를 증명하며
    check/review를 기다린 뒤 새 merge 승인을 받습니다.
- [ ] **REL-06 — Refresh the immutable publication hold**
  - **Action:** tag 직전에 `main` SHA, tag/release 부재, signing 설정, artifact
    계획을 다시 읽습니다.
- [ ] **REL-07 — Create the signed tag and GitHub Release**
  - **Action:** signed annotated `v1.3.1`을 만들고 push하며 세 tag 기반 asset를
    빌드하고 한국어 note가 있는 non-prerelease GitHub Release를 만듭니다.
- [ ] **REL-08 — Verify published consumers and close out**
  - **Action:** live download, SHA256SUMS, 추출한 validator, fresh tagged clone
    설치, local branch parity, 안전한 cleanup을 검증합니다.

## Dispatch hold

Refresh immediately before tag and release creation.

| Hold | 상태 |
| --- | --- |
| `v1.3.1` tag absent locally and remotely | PASS before preparation; refresh required before tag |
| `v1.3.1` GitHub Release absent | PASS before preparation; refresh required before release |
| Exact `main` candidate | PENDING promotion merge |
| SSH-signed annotated tag capability | PASS: local SSH signing configuration present; verification required on candidate tag |
| Tag-derived archives and checksums | PENDING exact-tag build |
| Extracted validators and fresh installs | PENDING exact-tag proof |

## 중단 조건

적용 가능한 gate 또는 hold가 unchecked, pending, stale, failed 상태인 동안에는
tag를 만들거나 GitHub Release를 생성하지 않습니다. 공개 후에는 exact live tag,
release body, asset 3개, 두 archive의 digest/download, 추출한 validator, 격리
fresh-install을 검증한 뒤에만 완료를 보고합니다.
