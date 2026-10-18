# Bluetape Skills 1.3.4 릴리스 체크리스트

## 증거 시점

- 기존 후보 준비 항목은 2026-08-13 당시 상태를 보존한다. 아래 `2026-10-19 후속 closeout read-back`은 이후 GitHub에서 확인한 병합·게시 상태이며, 두 시점의 체크를 혼합하지 않는다.

## 릴리스 식별

| 항목 | 고정 값 |
| --- | --- |
| 저장소 | `bluetape4k/bluetape-skills` |
| 흐름 / 분류 | `stable-release` / Type E 유지보수 + Type P GitHub skill bundle patch release |
| 대상 버전 / 태그 | `1.3.4` / `v1.3.4` |
| 최신 외부 릴리스 (초기 후보 준비 시점) | `v1.3.3`, 2026-08-12 공개, tag target `bfb5c1bbb542933501944908fb95fae040027198` |
| 후보 기준 | PR #34 마지막 head `22892eccbbf4d3aee4d6af025bd69990d6064f37`, branch `chore/agents-pr-guidance-gate` |
| 안정 기준 (초기) | `origin/main` `bfb5c1bbb542933501944908fb95fae040027198` |
| 준비 브랜치 | `chore/agents-pr-guidance-gate` -> `develop` |
| 승격 브랜치 | `release/promote-bluetape-skills-1.3.4` -> `main` |
| 승인 | 사용자가 `chezmoi` main 반영과 공개 `v1.3.4` 계획을 승인함. 각 PR 병합과 tag/GitHub Release는 별도 fresh approval 대상 |
| 산출물 | `bluetape-skills-1.3.4.tar.gz`, `bluetape-skills-1.3.4.zip`, `SHA256SUMS` |
| 소비자 범위 | 새 tag clone, archive extraction, 전체 validator, 14개 canonical skill의 격리된 fresh installation |
| Workflow dispatch | N/A — 저장소에 `.github/workflows`가 없음 |
| Catalog / Maven / BOM | N/A — source-only 공개 GitHub skill bundle |
| 연계 issue / milestone | 연계 issue 없음; PR #34와 #35는 milestone `1.3.4` (#2) |

## 범위와 제외

- `$bluetape-workflow`가 분류 전에 user-scope, workspace, repository/worktree
  `AGENTS.md` 기준 정보를 읽는 `WF-00`을 배포한다.
- PR 생성 직전 현재 guidance와 linked issue metadata를 다시 읽는 `CG-12A`와
  PR DoD template 회귀 검증을 배포한다.
- 운영 문서의 guidance를 `기준 정보` 또는 `원본`으로 표현하는 규칙을 공개
  workflow에 포함한다.
- 기존 public API, canonical skill inventory 14개, diagram asset은 변경하지
  않는다. 새 dependency, workflow dispatch, Maven, Go package는 포함하지 않는다.

## Router·공통 gate 상태

- [x] `WF-00` — user-scope, workspace, repository/worktree `AGENTS.md` 계층을
  확인하고 공개 skill에 순서와 실패 조건을 반영했다.
- [x] `WF-01`~`WF-04A` — Type E + Type P로 분류하고 leaf/common/release/writer
  계약을 읽었으며 repo-local `.bluetape` run을 초기화했다.
- [x] `CG-01`~`CG-05` — 현재 기준 정보, GNO 직접 검색 결과, live GitHub 상태,
  격리 worktree, 한국어 문서 범위를 확인했다.
- [x] `CG-06`~`CG-10` — 공개 문서 parity, validator, lesson gate, 최종 diff를
  확인했다. PR #34의 마지막 head는
  `22892eccbbf4d3aee4d6af025bd69990d6064f37`이다.
- [x] `CG-09` — 재사용 가능한 운영 교훈이 있어
  `docs/lessons/2026-08-13-agents-hierarchy-pr-guidance-gate.md`를 작성하고
  `SPW-01`~`SPW-05`를 확인했다.
- [x] `CG-11`~`CG-15` — PR #34를 `develop`에 생성하고 마지막 head
  `22892eccbbf4d3aee4d6af025bd69990d6064f37`로 live read-back·merge-ready
  확인을 마쳤다. merge 전 checks 0, reviews 0, `MERGEABLE`, assignee
  `debop`, milestone `1.3.4` (#2)였다.
- [x] `CG-16`~`CG-18` — PR #34는 2026-08-13 rebase merge되어 merge commit
  `29f68b01c7d2ff55e635d21d3e327ae2b0b8d9cf`를 만들었다. 현재 `develop`에
  이 merge commit이 포함되어 있음을 확인했다.
- [ ] `CG-X01` / `REL-08`~`REL-10` — exact `main` SHA와 fresh publication
  authority를 다시 확인한 뒤 signed tag·release·소비자 검증을 실행한다.

## 현재 증거

| 항목 | 결과 |
| --- | --- |
| public worktree | `.worktrees/bluetape-skills-agents-pr-gate`, `chore/agents-pr-guidance-gate` |
| machine-readable run | `20260813T133445Z-9a1259d1`, Type E, repo-local `.bluetape`, running |
| 승인·실행 전환 | `run-approve`와 `run-start` PASS, sequence 3 |
| 대상 변경 | `SKILL.md`, `workflow-manifest.json`, `common-gates.md`, PR template, contract test |
| 초기 contract check | 공개 bundle의 외부 companion skill(`code-review`, `self-audit`) 경고만 보고; exit 0 |
| 초기 workflow test | `147 passed, 1 skipped, 164 subtests passed` |
| develop PR | #34, `https://github.com/bluetape4k/bluetape-skills/pull/34`, 마지막 head `22892eccbbf4d3aee4d6af025bd69990d6064f37`, merge commit `29f68b01c7d2ff55e635d21d3e327ae2b0b8d9cf` |
| live PR 상태 | `MERGED` (2026-08-13), base `develop`, assignee `debop`, milestone `1.3.4` (#2) |
| 현재 중단점 | main 승격은 완료됐고 `v1.3.4` tag/GitHub Release와 산출물 검증은 미실행 |

## Release holds

| Hold | 상태 |
| --- | --- |
| PR #34 final head SHA | `22892eccbbf4d3aee4d6af025bd69990d6064f37` |
| PR #34 `develop` merge commit | `29f68b01c7d2ff55e635d21d3e327ae2b0b8d9cf` |
| `develop` PR merge | PASS — PR #34 merge 완료 |
| `main` promotion | PASS — PR #35 merge commit `fca08654a685927da0c6d87159315f65b6d6970b` |
| `v1.3.4` signed tag / GitHub Release | PENDING — 2026-10-19 조회에서 `v1.3.4` tag와 Release를 찾지 못함 |
| archive 3종 / checksum / fresh install | PENDING — exact tag 생성 뒤 순차 검증 |

## 2026-10-19 후속 closeout read-back

- PR #34 (`chore/agents-pr-guidance-gate` -> `develop`)은 마지막 head
  `22892eccbbf4d3aee4d6af025bd69990d6064f37`에서 2026-08-13 14:03:26 UTC에
  병합됐다. merge commit은
  `29f68b01c7d2ff55e635d21d3e327ae2b0b8d9cf`다. 2026-10-19 현재
  `develop`과 `origin/develop`은 `1156a0ffbcdd25edd4be97f6dc1a4c0092737b03`에서
  일치하며 이 merge commit을 포함한다.
- PR #35 (`release/promote-bluetape-skills-1.3.4` -> `main`)은 head
  `bb49f229985729f19ce90a06b78cedce16f6c5ef`에서 2026-08-13 15:07:35 UTC에
  병합됐다. merge commit은
  `fca08654a685927da0c6d87159315f65b6d6970b`이며 현재 `main`의 조상이다.
- GitHub Release 목록과 원격 tag를 확인한 2026-10-19 시점에 `v1.3.4`
  tag/Release는 없다. 따라서 main 승격 완료를 `v1.3.4` 공개 완료로 간주하지
  않으며 `CG-X01`, `REL-08`~`REL-10`, archive/checksum/격리 설치 검증은 계속
  `PENDING`이다. [PR #34](https://github.com/bluetape4k/bluetape-skills/pull/34),
  [PR #35](https://github.com/bluetape4k/bluetape-skills/pull/35),
  [공개 Release 목록](https://github.com/bluetape4k/bluetape-skills/releases).

## 중단 조건

적용 가능한 gate나 hold가 `PENDING`, stale, failed이면 dependent 작업을
실행하지 않는다. 특히 각 PR merge와 `v1.3.4` tag/GitHub Release는 현재
대화의 계획 승인만으로 실행하지 않고, 해당 exact SHA를 보고한 뒤 fresh
approval을 다시 받는다. 공개 후에는 live release asset, checksum, 추출본
validator, 14/14 격리 설치를 모두 확인한 뒤에만 완료로 보고한다.
