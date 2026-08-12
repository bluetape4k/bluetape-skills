# Bluetape Skills 1.3.3 릴리스 체크리스트

## 릴리스 식별

| 항목 | 고정 값 |
| --- | --- |
| 저장소 | `bluetape4k/bluetape-skills` |
| 흐름 / 분류 | `stable-release` / Type P 단일 저장소 GitHub skill bundle patch release |
| 대상 버전 / 태그 | `1.3.3` / `v1.3.3` |
| 최신 외부 릴리스 | `v1.3.2`, 2026-08-08 공개, tag target `163df4ac7b6e14a7f7a8393c89d1ecf0c05ee6b9` |
| 후보 기준 | `origin/develop` `2a42404ecda122a7a60cb3f1cfc0a744c0cf714b` |
| 안정 기준 | `origin/main` `163df4ac7b6e14a7f7a8393c89d1ecf0c05ee6b9` (`v1.3.2`) |
| 준비 브랜치 | `release/bluetape-skills-1.3.3` -> `develop` |
| 승격 브랜치 | `release/promote-bluetape-skills-1.3.3` -> `main` |
| 권한 | 사용자가 2026-08-12 `v1.3.3` 계획과 두 PR 생성을 승인함. 각 PR 병합과 tag/GitHub Release는 별도 fresh approval 대상 |
| 산출물 | `bluetape-skills-1.3.3.tar.gz`, `bluetape-skills-1.3.3.zip`, `SHA256SUMS` |
| 소비자 범위 | 새 tag clone, archive extraction, 전체 validator, 14개 canonical skill의 격리된 fresh installation |
| Workflow dispatch | N/A — 저장소에 `.github/workflows`가 없음 |
| Catalog / Maven / BOM | N/A — source-only 공개 GitHub skill bundle |
| 연계 issue / milestone | N/A — live GitHub에 열린 issue와 milestone이 없음 |

## 범위와 제외

- Superpowers brainstorming, specification/design, plan, review, lesson마다
  `$bluetape-writer`의 `SPW-01..05`를 독립적으로 요구하는 공개 계약을 배포한다.
- CSS marker와 arrowhead의 전후 증거, release 문서의 한국어 독자 계약,
  `.bluetape/` runtime state 제외 규칙을 포함한다.
- 기존 public API나 canonical skill inventory 14개는 변경하지 않는다.
- Maven, Go package, container, workflow dispatch는 이번 릴리스에 포함하지 않는다.

## Router와 체크리스트 계약

- [x] **WF-01 — Type P로 분류**
  - **Action:** 최신 tag, GitHub Release, 저장소 배포 방식을 확인하고 Type P를 선택한다.
  - **Evidence:** 최신 외부 버전 `v1.3.2`, GitHub Release asset 3개, source-only bundle 확인.
  - **Failure:** 배포 방식이 다르면 계획을 다시 승인받는다.
- [x] **WF-02 — 첫 구체 계획 작성**
  - **Action:** 버전, 파일, 두 PR, 검증, tag/release 중단점을 포함한 계획을 제시한다.
  - **Evidence:** 2026-08-12 대화의 `v1.3.3` 승인 대상 계획.
  - **Failure:** mutation을 시작하지 않는다.
- [x] **WF-03 — 첫 계획 승인**
  - **Action:** 첫 구체 계획의 사용자 승인을 받는다.
  - **Evidence:** 사용자의 2026-08-12 `승인` 응답.
  - **Failure:** read-only 상태를 유지한다.
- [x] **WF-04 — 실행 계약 로드**
  - **Action:** `$bluetape-workflow`, `$release`, `$bluetape-writer`, checklist/common gate, worktree 계약을 읽는다.
  - **Evidence:** 현재 session에서 각 `SKILL.md`와 필수 reference를 다시 읽음.
  - **Failure:** 편집을 중단한다.
- [x] **WF-04A — machine-readable evidence 초기화**
  - **Action:** repo-local state root에 Type P run을 초기화하고 승인·실행 상태로 전환한다.
  - **Evidence:** run `20260812T091946Z-925480f2`, state root `.bluetape`, sequence 3, mutation target 5개 PASS.
  - **Failure:** 수동으로 receipt를 수정하지 않고 진단한다.
- [ ] **WF-05 — gate 순서대로 실행**
  - **Action:** 아래 `CG-*`, `REL-*`을 물리적 순서대로 실행한다.
  - **Evidence:** 각 항목의 fresh 결과.
  - **Failure:** 실패하거나 대기 중인 항목의 downstream을 중단한다.

- [x] **CL-01 — mutation 전 체크리스트 생성**
  - **Action:** release 문서와 README를 수정하기 전에 이 파일을 생성한다.
  - **Evidence:** 첫 tracked file mutation이 이 체크리스트 생성임.
  - **Failure:** 누락 시 downstream 증거를 모두 다시 검증한다.
- [x] **CL-02 — 항목 적용성 분류**
  - **Action:** required, conditional, N/A를 범위 근거와 함께 구분한다.
  - **Evidence:** 아래 N/A 표와 순서화된 required 항목.
  - **Failure:** 분류하지 않은 항목은 required unchecked로 처리한다.
- [x] **CL-03 — 의존 순서 준수**
  - **Action:** 체크리스트 위에서 아래 순서로 실행한다.
  - **Evidence:** 현재까지 preflight -> 문서 -> validator -> archive/fresh install -> review/lesson -> commit -> push -> PR 순서로 실행했다. merge와 publication branch는 아직 시작하지 않았다.
  - **Failure:** 순서를 건너뛴 downstream 증거를 다시 실행한다.
- [x] **CL-04 — 증거 즉시 기록**
  - **Action:** 각 명령과 live 결과를 확인한 직후 해당 항목에 기록한다.
  - **Evidence:** candidate SHA, test count, archive checksum, remote SHA, PR URL과 live metadata를 각 gate에서 기록했다.
  - **Failure:** 증거가 없는 항목은 unchecked로 둔다.
- [ ] **CL-05 — fail closed**
  - **Action:** 승인·검증·review 대기를 `PENDING`으로 유지한다.
  - **Evidence:** downstream 중단 상태.
  - **Failure:** 잘못 진행한 downstream 증거를 폐기하고 다시 실행한다.
- [ ] **CL-07 — irreversible hold 갱신**
  - **Action:** 각 merge와 tag/release 직전에 target, authority, SHA를 다시 확인한다.
  - **Evidence:** fresh approval과 hold 결과.
  - **Failure:** 해당 side effect를 실행하지 않는다.
- [ ] **CL-08 — 완료 전 count 정합성 확인**
  - **Action:** required, N/A, blocked, unchecked 수를 맞춘다.
  - **Evidence:** 최종 DoD count.
  - **Failure:** 완료 보고를 차단한다.

### 조건부·N/A 항목

| 항목 | 상태 | 근거 |
| --- | --- | --- |
| `WF-06`, `CL-06` repair | 조건부 N/A | 현재까지 skipped/weak gate가 없음. 발생하면 즉시 required로 전환 |
| `CG-05` abstraction/dependency | N/A | release metadata만 추가하며 새 abstraction이나 dependency가 없음 |
| `CG-08` heavyweight checks | N/A | Testcontainers, real DB, native/JNI, emulator, benchmark 범위가 없음 |
| issue/milestone mirror | N/A | live GitHub open issue와 milestone이 없음 |
| diagram 제작/수정 | N/A | release 후보에서 기존 SVG/PNG를 변경하지 않음 |

## 공통 preflight와 후보 준비

- [x] **CG-01 — 권한과 현재 상태 재확인**
  - **Action:** AGENTS, selected skills, approved plan, status와 diff를 다시 읽는다.
  - **Evidence:** clean `develop` `2a42404`, 사용자 승인, Type P 범위 확인.
  - **Failure:** 편집 전에 중단한다.
- [x] **CG-02 — 역사·현재 근거 확인**
  - **Action:** GNO와 live GitHub에서 이전 checklist, PR, tag, release를 확인한다.
  - **Evidence:** docs collection의 `1.3.0`/`1.3.1` checklist, PR #26/#27, live `v1.3.2` release.
  - **Failure:** 기존 배포 관례가 불명확하면 진행하지 않는다.
- [x] **CG-03 — 사용자 작업과 integration branch 보호**
  - **Action:** clean integration checkout을 보존하고 별도 worktree/branch를 만든다.
  - **Evidence:** `/Users/debop/work/bluetape4k/.worktrees/bluetape-skills-1.3.3`, branch `release/bluetape-skills-1.3.3`, base `2a42404`.
  - **Failure:** dirty·ambiguous 상태를 삭제하거나 덮어쓰지 않는다.
- [x] **CG-04 — 독자·언어·배포 경계 고정**
  - **Action:** README EN/KO parity와 한국어 CHANGELOG/release metadata 계약을 적용한다.
  - **Evidence:** `README.md` English, `README.ko.md` Korean, release docs와 GitHub metadata Korean.
  - **Failure:** locale drift를 수정하기 전 PR을 만들지 않는다.
- [x] **CG-06 — 공개 문서 계약 갱신**
  - **Action:** CHANGELOG, EN/KO README, release checklist를 `v1.3.3`으로 맞춘다.
  - **Evidence:** `CHANGELOG.md`, `README.md`, `README.ko.md`, 이 checklist의 `v1.3.3` 정렬과 README version token count 5/5.
  - **Failure:** 불일치한 상태로 검증하지 않는다.
- [x] **CG-07 — 대상 검증 실행**
  - **Action:** validator, diff check, archive checksum·추출·fresh install을 실행한다.
  - **Evidence:** candidate `f3f0dc9647ae59c6495dad088fd932a07462baaf`에서 validator PASS, archive SHA-256 2개 OK, tar/zip 추출본 validator PASS, 격리 설치 14/14 각각 확인.
  - **Failure:** 수정 후 전체 영향 검증을 다시 실행한다.
- [x] **CG-09 — lesson gate 평가**
  - **Action:** task/diff와 기존 release lesson을 대조한다.
  - **Evidence:** 새 lesson N/A. `docs/lessons/2026-07-27-live-skill-bundle-sync-workflow-gates.md`의 공개 bundle 경계·fresh install 규칙과 `docs/lessons/2026-08-12-superpowers-writer-hard-gate.md`의 writer gate 결정을 그대로 재사용했다. 이번 release metadata diff에는 novel failure, recovery, design, operational guidance가 없다.
  - **Failure:** lesson 근거 없이는 pre-PR proof로 진행하지 않는다.
- [x] **CG-10 — pre-PR proof 수렴**
  - **Action:** 최종 diff review, P0/P1=0, 검증 재실행 후 commit한다.
  - **Evidence:** candidate `7d2489e09c4d372af83ef9e0966881bbeff56dd3`에서 final scoped review P0=0/P1=0, `./scripts/validate.sh` workflow 146/1 skip/164 subtests와 diagram 50개 PASS, `git diff --check` PASS. 이 체크 상태를 기록한 최종 PR head는 push 직전 다시 검증해 live PR에 고정한다.
  - **Failure:** PR 생성을 차단한다.

## Release 전용 게이트

- [x] **REL-01 — 대상과 권한 고정**
  - **Action:** 최신 외부 버전, 목표 버전, 대상 저장소와 side-effect authority를 고정한다.
  - **Evidence:** 최신 `v1.3.2`, 목표 `v1.3.3`, repository/branch/asset/approval 표.
  - **Failure:** 버전이나 대상이 바뀌면 계획을 다시 승인받는다.
- [x] **REL-02 — 공개 릴리스 메타데이터 준비**
  - **Action:** CHANGELOG, EN/KO README, checklist를 일치시킨다.
  - **Evidence:** EN/KO README의 `v1.3.3` install/update 예시, CHANGELOG의 추가/변경/버그 수정과 compare link.
  - **Failure:** metadata drift를 수정한다.
- [x] **REL-03 — develop 후보 검증**
  - **Action:** exact candidate에서 public bundle validator와 diff check를 실행한다.
  - **Evidence:** `./scripts/validate.sh`에서 workflow `146 passed, 1 skipped, 164 subtests`, diagram 50개, canonical skill 14개와 public boundary PASS. `git diff --check` PASS.
  - **Failure:** commit/push를 중단한다.
- [x] **REL-03A — archive 소비자 사전 검증**
  - **Action:** candidate-derived tar.gz/zip/checksum과 추출본·fresh install을 검증한다.
  - **Evidence:** candidate `f3f0dc9`에서 tar `5eb8f6c1ba3854bf3dd0334aea82806223e3dee71030fac8489d707a5c28fbd7`, zip `bd12030f51c9c22c6468f47b15f1a310348d357d66e6014a2d0745ec2911fa4d`; checksum OK, 두 추출본 validator PASS, 두 격리 설치 14/14.
  - **Failure:** PR 생성을 중단한다.
- [x] **REL-04 — develop 준비 PR 전달**
  - **Action:** exact branch를 push하고 `develop` 대상 Korean PR을 만들고 live read-back한다.
  - **Evidence:** PR #32 `https://github.com/bluetape4k/bluetape-skills/pull/32`, initial exact head `3f282c96d66764c31020c6aa29f4a651b1290068`, assignee `debop`, final heading `## DoD Status`, `MERGEABLE`.
  - **Failure:** live PR을 복구한다.
- [ ] **REL-05 — develop 병합 승인 대기**
  - **Action:** exact-head merge-ready를 보고하고 fresh approval을 기다린다.
  - **Evidence:** 보고 이후의 사용자 승인.
  - **Failure:** `PENDING`; auto-merge를 사용하지 않는다.
- [ ] **REL-06 — main exact tree 승격**
  - **Action:** approved develop merge tree와 같은 tree인 promotion branch/PR을 만든다.
  - **Evidence:** tree SHA parity와 live promotion PR.
  - **Failure:** divergence를 복구하기 전 tag 단계로 가지 않는다.
- [ ] **REL-07 — promotion 병합 승인 대기**
  - **Action:** exact promotion PR/head merge-ready를 보고하고 fresh approval을 기다린다.
  - **Evidence:** 보고 이후의 사용자 승인.
  - **Failure:** `PENDING`; tag/release를 만들지 않는다.
- [ ] **REL-08 — immutable publication hold 갱신**
  - **Action:** exact main SHA, tag/release 부재, SSH signing, artifact 계획과 fresh authority를 확인한다.
  - **Evidence:** `v1.3.3`, main SHA, signing verification, timestamp와 승인.
  - **Failure:** publication을 차단한다.
- [ ] **REL-09 — signed tag와 GitHub Release 생성**
  - **Action:** SSH-signed annotated tag를 push하고 tag-derived asset 3개를 공개한다.
  - **Evidence:** tag object/target/signature, release URL/body/assets.
  - **Failure:** immutable tag를 덮어쓰지 않고 corrective patch로 재계획한다.
- [ ] **REL-10 — published consumer 검증과 closeout**
  - **Action:** live download, checksum, extraction, validator, fresh install과 local parity를 확인한다.
  - **Evidence:** URL, SHA-256, validator 결과, 14/14 설치, final SHA.
  - **Failure:** partial 상태를 보고하고 모호한 local state를 삭제하지 않는다.

## PR 전달 게이트

- [x] **CG-11 — PR 생성 권한 확인**
  - **Action:** 승인된 repo/base/head와 모든 pre-PR prerequisite를 다시 확인한다.
  - **Evidence:** 사용자가 `bluetape4k/bluetape-skills`의 `release/bluetape-skills-1.3.3` -> `develop` PR 생성과 후속 promotion PR 생성을 승인함. CG-01..10과 REL-01..03A PASS.
  - **Failure:** PR 생성을 중단한다.
- [x] **CG-12 — exact head push**
  - **Action:** force 없이 push하고 local/remote SHA를 대조한다.
  - **Evidence:** initial push에서 local/remote `3f282c96d66764c31020c6aa29f4a651b1290068` 일치. 이 live evidence 기록 commit을 포함한 final head도 force 없이 다시 push하고 대조한다.
  - **Failure:** PR 생성을 중단한다.
- [x] **CG-13 — PR 생성과 live 검증**
  - **Action:** assignee `debop`, Korean body, final `## DoD Status`를 확인한다.
  - **Evidence:** PR #32, base `develop`, head `release/bluetape-skills-1.3.3`, assignee `debop`, final `## DoD Status`, issue/milestone/labels N/A.
  - **Failure:** CI/review 진행 전에 수정한다.
- [x] **CG-14 — CI와 live review 확인**
  - **Action:** exact head의 checks, reviews, threads를 읽는다.
  - **Evidence:** repository workflow와 branch protection이 없어 `statusCheckRollup=[]`; live reviews 0, review threads 0, final scoped review P0=0/P1=0, PR `MERGEABLE`.
  - **Failure:** 대기는 `PENDING`, 실패는 repair로 되돌린다.
- [ ] **CG-15 — merge-ready 보고**
  - **Action:** exact PR/head, 검증, lesson, count를 사용자에게 보고한다.
  - **Evidence:** user-visible merge-ready DoD.
  - **Failure:** merge 승인을 요청하지 않는다.
- [ ] **CG-16 — fresh merge approval**
  - **Action:** CG-15 이후 exact PR/head 승인을 받는다.
  - **Evidence:** fresh user approval.
  - **Failure:** `PENDING`.
- [ ] **CG-17 — 승인된 merge 실행·검증**
  - **Action:** rebase merge 후 live merge SHA를 확인한다.
  - **Evidence:** merged state와 SHA.
  - **Failure:** 다른 SHA나 auto-merge로 대체하지 않는다.
- [ ] **CG-18 — local sync와 보수적 정리**
  - **Action:** integration checkout을 ff-only sync하고 proven merged 상태만 정리한다.
  - **Evidence:** local/upstream SHA와 preserved/cleanup 목록.
  - **Failure:** 모호한 worktree/branch를 보존한다.
- [ ] **CG-X01 — non-PR irreversible action 승인**
  - **Action:** tag와 GitHub Release 직전에 exact authority와 hold를 다시 확인한다.
  - **Evidence:** publication 직전 fresh approval, target/version/SHA/timestamp.
  - **Failure:** tag와 release를 실행하지 않는다.

## Dispatch hold

| Hold | 현재 상태 |
| --- | --- |
| `v1.3.3` tag와 GitHub Release 부재 | publication 직전 fresh 확인 필요 |
| exact `main` 후보 | promotion merge 전 `PENDING` |
| SSH-signed annotated tag | `gpg.format=ssh`, public signing key, `tag.gpgSign=true` 확인; temporary allowed-signers 검증 필요 |
| tag-derived archive와 checksum | exact tag 생성 후 build 필요 |
| extracted validator와 fresh install | exact candidate와 publication 뒤 각각 검증 필요 |

## 중단 조건

적용 가능한 gate나 hold가 unchecked, pending, stale, failed이면 dependent
작업을 실행하지 않는다. 특히 각 PR merge와 tag/GitHub Release는 fresh
approval 없이는 실행하지 않는다. 공개 후에는 live tag, release body, asset
3개, archive digest, extracted validator, 격리된 fresh installation을 모두
확인한 뒤에만 릴리스 완료로 보고한다.
