# Bluetape Skills 1.3.0 release checklist

## Release 식별 정보

| 항목 | 고정 값 |
| --- | --- |
| Repository | `bluetape4k/bluetape-skills` |
| Flow / class | `stable-release` / 단일 저장소 GitHub skill bundle minor release |
| Target version / tag | `1.3.0` / `v1.3.0` |
| Latest observed external version | `v1.2.2`, 2026-07-27 공개 |
| Integration candidate | release 준비 전 `e278d7ab7c0b166e0a262b312e6007e9a21943a8`의 `develop` |
| Stable base | `v1.2.2`의 `main` (`1f1c677ff8b885687be83e1cc924449a88aa212a`) |
| Preparation branch | `release/bluetape-skills-1.3.0` -> `develop` |
| Promotion branch | `release/promote-bluetape-skills-1.3.0` -> `main` |
| Authority | 사용자가 2026-07-31에 새 release와 정확한 `v1.3.0` 계획을 승인 |
| Artifact matrix | `bluetape-skills-1.3.0.tar.gz`, `bluetape-skills-1.3.0.zip`, `SHA256SUMS` |
| Consumer scope | tag clone, archive 추출, 전체 validator, 14개 canonical skill의 격리 fresh 설치 |
| Catalog / Maven / BOM role | N/A — source-only 공개 GitHub skill bundle |
| Workflow dispatch | N/A — `.github/workflows` 공개 workflow 없음 |

## 범위와 topology

- 공개 배포에는 정확히 14개 canonical `bluetape-*` skill이 포함됩니다.
  `bluetape-publish-kotlin`은 local compatibility alias로 남기고 제외합니다.
- 공개 `develop` bundle은 유지 중인 live canonical directory와 내용이 같으며,
  `bluetape-workflow/tests/test_manifest_contract.py`의 의도된 공개 전용
  portability guard만 예외입니다.
- PR #13 (`docs/repository-authority-boundary`)은 별도 head이고 새 merge 승인이
  없어 계속 열어 두며 범위에서 제외합니다.
- 이 release는 한 저장소만 다루며 Maven, catalog, snapshot, downstream stable
  dependency edge가 없습니다.
- `v1.2.2` release metadata가 `main`에는 있지만 `develop`으로 동기화되지 않아,
  이 release에서 기존 changelog 기록을 복원한 뒤 `1.3.0` 기록을 추가합니다.

## 필수 gate

- [x] **REL-01 — Pin target inventory**
  - **Action:** 모든 release 작업에서 식별 정보 표의 값을 보존합니다.
  - **Evidence:** 이 checklist가 `1.3.0`, `v1.3.0`, `v1.2.2`, candidate/base SHA,
    세 asset, authority, 14-skill consumer scope를 고정합니다.
  - **Failure:** release 준비 또는 공개 전에 중단합니다.
- [x] **REL-02 — Reconfirm live release state**
  - **Action:** release, tag, PR, branch/ruleset 상태와 제외 항목을 다시 읽습니다.
  - **Evidence:** fresh `gh release list`가 `v1.2.2`를 Latest로 보고했고,
    `v1.3.0` local/remote tag와 GitHub Release는 없으며 PR #13은 `9912fbef`에서
    열린 채 제외되었습니다.
  - **Failure:** live 상태가 바뀌면 계획을 다시 세웁니다.
- [x] **REL-03 — Export canonical bundle**
  - **Action:** live canonical skill 14개를 export하고 공개 portability guard를
    복원합니다.
  - **Evidence:** `export-bluetape-skills`가 14개 directory를 export했으며,
    공개 전용 manifest guard 복원 후 `git diff --name-only`에 `skills/` path가
    없습니다.
  - **Failure:** 예상하지 못한 내용 또는 경계 drift가 있으면 중단합니다.
- [x] **REL-04 — Prepare public release metadata**
  - **Action:** `1.2.2` 이력을 복원하고 `1.3.0` release note를 추가하며 두 README
    설치 예시를 갱신하고 EN/KO parity를 보존합니다.
  - **Evidence:** `CHANGELOG.md`에 날짜가 있는 `1.2.2`, `1.3.0` entry/link가 있고,
    README EN/KO의 stale-version 검색 결과가 없으며 `v1.3.0` 예시를 대조했습니다.
  - **Failure:** 오래되거나 불일치하는 공개 문서를 수정합니다.
- [x] **REL-05 — Validate candidate**
  - **Action:** `./scripts/validate.sh`, `git diff --check`, targeted release-reference
    check를 실행합니다.
  - **Evidence:** `./scripts/validate.sh`: 144 passed, 1 skipped, 159 subtests;
    diagram test 22개 통과; `git diff --check`와 target-version reference check도
    통과했습니다.
  - **Failure:** 영향받은 증거를 수정하고 다시 실행합니다.
- [x] **REL-06 — Verify archive consumers**
  - **Action:** 정확한 candidate에서 두 archive를 만들고 checksum 검증, 추출,
    validation, 모든 canonical skill의 격리 home fresh 설치를 수행합니다.
  - **Evidence:** 두 exact-candidate archive가 추출 후 `144 passed, 1 skipped,
    159 subtests`와 diagram test 22개를 통과했으며, SHA-256 검증과 격리 fresh
    설치에서 각각 canonical skill 14/14개가 생성됐습니다.
  - **Failure:** release-preparation PR을 열지 않습니다.
- [ ] **REL-07 — Deliver preparation PR**
  - **Action:** 정확한 preparation head를 push하고 `## DoD Status`로 끝나는
    한국어 `develop` PR을 생성·검증합니다.
  - **Evidence:** live PR metadata, exact head, 현재 review/thread, validator 결과.
  - **Failure:** merge-ready 보고 전에 live delivery를 복구합니다.
- [ ] **REL-08 — Hold for preparation merge approval**
  - **Action:** 정확한 PR/head가 merge-ready임을 보고하고 새 사용자 승인을 기다립니다.
  - **Evidence:** merge-ready 보고 후 발급된 승인.
  - **Failure:** PENDING; merge 또는 auto-merge를 실행하지 않습니다.
- [ ] **REL-09 — Promote exact develop tree**
  - **Action:** `main`에서 promotion branch를 만들고 승인된 `develop` merge tree를
    materialize한 뒤 tree parity를 증명합니다.
  - **Evidence:** exact merge SHA와 merged `develop` 대비 빈 tree diff.
  - **Failure:** promotion PR 생성 전에 divergence를 수정합니다.
- [ ] **REL-10 — Deliver promotion PR**
  - **Action:** `main` promotion PR을 push·검증하고 exact-head merge-ready를
    보고합니다.
  - **Evidence:** live PR metadata, exact head, ruleset 준수, blocker 없음.
  - **Failure:** PENDING 또는 복구; auto-merge 금지.
- [ ] **REL-11 — Hold for promotion merge approval**
  - **Action:** promotion merge-ready 보고 후 새 사용자 승인을 기다립니다.
  - **Evidence:** 정확한 promotion PR/head에 대한 승인.
  - **Failure:** PENDING; tag 또는 공개를 실행하지 않습니다.
- [ ] **REL-12 — Refresh irreversible hold**
  - **Action:** tag 직전에 main SHA, tag/release 부재, signing 설정, asset, release
    authority를 다시 읽습니다.
  - **Evidence:** 모든 행이 PASS인 timestamped fresh hold.
  - **Failure:** tag와 GitHub Release를 차단합니다.
- [ ] **REL-13 — Create immutable release**
  - **Action:** SSH-signed annotated `v1.3.0` tag를 만들고 push하며 tag 기반
    asset를 빌드하고 non-prerelease GitHub Release를 만듭니다.
  - **Evidence:** tag object/target/signature, live release body, 업로드된 asset 3개.
  - **Failure:** 절대 retag하지 말고 immutable 내용이 잘못되면 corrective patch를
    사용합니다.
- [ ] **REL-14 — Verify published consumers and close out**
  - **Action:** asset를 다운로드하고 digest를 검증하며 추출/validation,
    fresh-install, local branch 동기화를 수행한 뒤 승인되고 merge가 증명된
    release worktree/branch만 제거합니다.
  - **Evidence:** live download, validation 결과, 동기화된 SHA, cleanup 목록.
  - **Failure:** release 상태를 partial로 유지하고 모호한 local 상태를 보존합니다.

## Dispatch hold

Refresh immediately before tag and release creation.

| Hold | 현재 상태 |
| --- | --- |
| `v1.3.0` tag absent locally and remotely | PASS before preparation; refresh required before tag |
| `v1.3.0` GitHub Release absent | PASS before preparation; refresh required before release |
| Exact `main` candidate | PENDING promotion merge |
| Signed annotated tag capability | PENDING candidate-signing check |
| Tag-derived archives and checksums | PENDING exact-tag build |
| Extracted validators and fresh installs | PENDING exact-tag proof |
| Open release-affecting work dispositioned | PASS: PR #13 excluded |

## 중단 조건

적용 가능한 gate 또는 hold가 unchecked, pending, stale, failed 상태인 동안에는
tag를 만들거나 GitHub Release를 생성하지 않습니다. 공개 후에는 exact live tag,
release body, asset 3개, 두 archive의 digest/download, 추출한 validator, 격리
fresh-install을 검증한 뒤에만 release 완료를 보고합니다.
