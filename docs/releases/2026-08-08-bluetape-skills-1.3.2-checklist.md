# Bluetape Skills 1.3.2 릴리스 체크리스트

## 릴리스 식별

| 항목 | 고정 값 |
| --- | --- |
| 저장소 | `bluetape4k/bluetape-skills` |
| 흐름 / 분류 | `stable-release` / 단일 저장소 GitHub skill bundle patch release |
| 대상 버전 / 태그 | `1.3.2` / `v1.3.2` |
| 최신 외부 릴리스 | `v1.3.1`, 2026-08-07 공개 |
| 통합 후보 | `release/bluetape-skills-1.3.2` `84aa8a8` (diagram 개선 후보 `0cdfd661b67a8d2f939e3ed695226499b5c77ecc` 포함) |
| 안정 기준 | `main` `963c46ae8595a893f1d0466c23f54f70e527e37b` (`v1.3.1`) |
| 준비 브랜치 | `release/bluetape-skills-1.3.2` -> `develop` |
| 승격 브랜치 | `release/promote-bluetape-skills-1.3.2` -> `main` |
| 권한 | 사용자가 2026-08-08 `bluetape-skills` 저장소만 배포하고 다른 기기의 diagram 재렌더링은 제외하도록 요청함. 최신 안정 버전 다음 patch인 `v1.3.2`를 배포 대상으로 선택함 |
| 산출물 | `bluetape-skills-1.3.2.tar.gz`, `bluetape-skills-1.3.2.zip`, `SHA256SUMS` |
| 소비자 범위 | 새 tag clone, archive extraction, 전체 validator, 14개 canonical skill의 격리된 fresh installation |
| Workflow dispatch | N/A — `.github/workflows` 공개 릴리스 workflow 없음 |
| Catalog / Maven / BOM | N/A — source-only 공개 GitHub skill bundle |

## 범위와 제외

- `$bluetape-diagram`의 semantic ledger, semantic/arrowhead/visual/asset-pair
  audit와 rounded orthogonal connector 제작 계약을 공개 bundle에 포함한다.
- README workflow asset은 현재 bundle에 포함된 검증된 SVG/PNG만 배포한다.
  `bluetape4k` workspace의 기존 diagram 전체 재렌더링은 다른 기기에서 별도로
  수행하며 이번 릴리스 작업에는 포함하지 않는다.
- 공개 배포본은 14개 canonical `bluetape-*` skill만 포함하고 개인 runtime
  state, hook, memory, cache, secret, compatibility alias는 제외한다.

## 필수 게이트

- [x] **REL-01 — 대상과 권한 고정**
  - **증거:** live GitHub에서 `v1.3.1`이 최신이고, 후보 HEAD·안정 기준·사용자 범위 요청을 위 표에 고정했다.
- [x] **REL-02 — 공개 릴리스 메타데이터 준비**
  - **증거:** `CHANGELOG.md`의 `1.3.2` 항목, EN/KO README의 `v1.3.2` install/update 예시, 이 체크리스트가 일치한다.
- [x] **REL-03 — develop 후보 검증**
  - **조치:** `./scripts/validate.sh`, `git diff --check`, diagram audit 회귀 테스트와 공개 경계 검사를 실행했다.
  - **증거:** exact candidate `60cf68ef35c7bbc082622aabc8a6f92ebddff17d`에서 `145 passed, 1 skipped, 159 subtests passed`, diagram audit `49 tests OK`, `git diff --check` PASS, public boundary PASS.
  - **실패:** 실패한 검사를 먼저 복구하고 PR 생성을 중단한다.
- [x] **REL-03A — archive 소비자 사전 검증**
  - **조치:** exact candidate로 tar.gz/zip과 `SHA256SUMS`를 만들고 추출본 validator 및 격리된 fresh install을 실행했다.
  - **증거:** 두 archive checksum `OK`, 두 추출본 validator `PASS: 14 canonical skills...`, 두 fresh install 모두 14/14 canonical skills.
  - **실패:** archive 또는 fresh install이 실패하면 PR 생성을 중단한다.
- [ ] **REL-04 — develop 준비 PR 전달**
  - **조치:** exact preparation branch를 push하고 Korean PR body가 `## DoD Status`로 끝나는지 확인한 뒤 CI와 review를 기다린다.
  - **증거:** live PR URL, base/head SHA, metadata, checks, reviews.
  - **실패:** live PR을 복구하고 merge-ready 보고 전에는 진행하지 않는다.
- [ ] **REL-05 — develop 병합 승인 대기**
  - **조치:** exact PR/head의 merge-ready 결과를 사용자에게 보고하고 fresh merge approval을 기다린다.
  - **증거:** merge-ready 보고 이후 발행된 승인.
  - **실패:** `PENDING`; 자동 병합이나 임의 병합을 사용하지 않는다.
- [ ] **REL-06 — main으로 exact tree 승격**
  - **조치:** 승인된 develop merge tree로 promotion branch와 PR을 만들고 tree parity를 증명한다.
  - **증거:** develop merge SHA와 main promotion tree의 빈 diff, live promotion PR.
  - **실패:** divergence를 복구하기 전에는 tag 단계로 가지 않는다.
- [ ] **REL-07 — promotion 병합 승인 대기**
  - **조치:** exact promotion PR/head의 merge-ready 결과를 보고하고 fresh merge approval을 기다린다.
  - **증거:** promotion merge-ready 보고 이후 발행된 승인.
  - **실패:** `PENDING`; tag나 release를 만들지 않는다.
- [ ] **REL-08 — immutable publication hold 갱신**
  - **조치:** tag 직전에 main SHA, tag/release 부재, SSH signing, artifact 계획과 현재 권한을 다시 읽는다.
  - **증거:** 대상 `v1.3.2`, exact main SHA, 부재 확인, signing 확인, timestamp.
  - **실패:** tag와 GitHub Release를 차단한다.
- [ ] **REL-09 — signed tag와 GitHub Release 생성**
  - **조치:** SSH-signed annotated `v1.3.2`를 만들고 push한 뒤 tag-derived archive 2개와 `SHA256SUMS`를 업로드한다.
  - **증거:** tag object/target/signature, live release notes, 세 asset.
  - **실패:** immutable tag를 덮어쓰지 말고 corrective patch로 재계획한다.
- [ ] **REL-10 — published consumer 검증과 closeout**
  - **조치:** live download, checksum, extraction, validator, fresh install, local branch parity를 확인한다.
  - **증거:** 다운로드 URL, SHA-256, validator 결과, 14/14 설치, 최종 SHA.
  - **실패:** 릴리스 상태를 partial로 유지하고 모호한 로컬 상태를 삭제하지 않는다.

## Dispatch hold

tag와 release 직전에 반드시 갱신한다.

| Hold | 상태 |
| --- | --- |
| `v1.3.2` tag와 GitHub Release 부재 | 릴리스 직전 fresh 확인 필요 |
| exact `main` 후보 | promotion 병합 전 `PENDING` |
| SSH-signed annotated tag | local signing 설정 확인 후 candidate 검증 필요 |
| tag-derived archive와 checksum | exact tag 생성 후 빌드 필요 |
| extracted validator와 fresh install | exact tag 생성 후 검증 필요 |

## 중단 조건

적용 가능한 게이트나 hold가 unchecked, pending, stale, failed이면 tag 또는
GitHub Release를 만들지 않는다. 공개 후에는 live tag, release body, 세 asset,
archive digest, extracted validator, 격리된 fresh installation을 모두 확인한
뒤에만 릴리스 완료로 보고한다.
