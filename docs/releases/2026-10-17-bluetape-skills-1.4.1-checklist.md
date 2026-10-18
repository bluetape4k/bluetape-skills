# Bluetape Skills 1.4.1 릴리스 체크리스트

## 릴리스 식별 및 승인 경계

| 항목 | 값 |
|---|---|
| 저장소 | `bluetape4k/bluetape-skills` |
| 분류 | Type E 유지보수 + Type P stable-release 준비 |
| 대상 버전 / 태그 | `1.4.1` / `v1.4.1` |
| 최신 공개 릴리스 | `v1.4.0` (`2026-09-08`) |
| 통합 브랜치 / 안정 브랜치 | `develop` / `main` |
| 후보 브랜치 | `release/bluetape-skills-1.4.1` (로컬 version-sync 후보) |
| 기준 커밋 | `31e69c613e9f908bec27f3a7ebee6e34cabebe21` (`develop`, PR #40 병합 후) |
| 후보 SHA | local `HEAD`를 기준으로 하며 원격 작업 승인 요청 직전에 다시 읽어 기록; 원격 ref는 아직 없음 |
| 후보 PR 권한 | PENDING — 제안 대상 `bluetape4k/bluetape-skills`, base `develop`, head `release/bluetape-skills-1.4.1`; 이 exact pair와 candidate SHA에 대한 push/PR 생성 승인은 아직 없음 |
| 배포 범위 | Codex 기본 모델 및 OMX 역할별 모델을 직접 적용하는 한·영 참고 문서와 README 연결 |
| 제외 범위 | installer 동작, skill inventory, 사용자 개인 설정/chezmoi, 자동 설정·동기화 |
| dispatch hold | GitHub Actions workflow 없음 — workflow dispatch는 N/A; tag와 Release는 별도 승인 전까지 보류 |
| 별도 승인 보류 | 후보 PR push/생성, PR merge, `main` 승격, 서명 태그, GitHub Release 및 archive 업로드 |

## 근거와 독자 계약

- 사용 목적은 다른 개발자가 설정을 검토하고 필요에 따라 수동 적용하는 것이다. 이 문서는 보편적 권고나 자동 설치 기능이 아니다.
- Codex 기본 설정 출처: [Configuration Reference](https://developers.openai.com/codex/config-reference), [GPT-6 Luna model page](https://developers.openai.com/api/docs/models/gpt-6-luna).
- OMX 설정 경로·지원 key·설정 재생성 출처: [OMX model/config routing reference](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/docs/reference/omx-config-schema-routing.md).
- 저장소 경계 출처: `README.md`, `README.ko.md`, `scripts/install.sh`, `skills/bluetape-workflow/references/model-routing.md`.
- 수신 계정·workspace·Codex 클라이언트가 `gpt-6-luna`와 `max`를 지원해야 한다. 설정 문자열만으로 사용 권한이나 실제 적용을 보장하지 않는다.
- 예제는 현재 Bluetape 역할 table의 22개 role key를 담으며, 적용자는 설치 버전의 OMX role registry와 대조한다.

## 현재 release 순서

- PR #40은 모델 설정 참고 자료를 `develop`에 병합했지만, 병합 직후 `README.md`와 `README.ko.md`는 여전히 `v1.4.0`을 가리키고 `CHANGELOG.md` 변경은 `[Unreleased]` 아래에 있었다.
- 따라서 `31e69c613e9f908bec27f3a7ebee6e34cabebe21`을 바로 `main`에 승격하지 않는다. 먼저 `v1.4.1` 버전 참조를 `develop`에 반영하고, 그 exact head를 검증·승인받은 뒤 별도의 `main` promotion PR을 준비한다.
- 다음 release에서도 안정 승격 전 `develop`의 README 태그 예제와 CHANGELOG heading/link가 목표 버전과 일치하는지 확인한다.

## Workflow Gate

- [x] **WF-00 — guidance 계층 확인**
  - **Action:** user/workspace/repository `AGENTS.md` 계층을 적용한다.
  - **Evidence:** 활성 user-scope/workspace-scope guidance와 저장소 `AGENTS.md`를 확인했다. 기기별 절대 경로는 이 public checklist에 기록하지 않는다.
  - **Failure:** 누락된 정책이 있으면 변경을 중단한다.
- [x] **WF-01 — 작업 분류**
  - **Action:** 변경 유형과 범위를 분류한다.
  - **Evidence:** 공개 문서·README·CHANGELOG 유지보수(Type E), stable-release 준비(Type P)이며 제품 동작은 바꾸지 않는다.
  - **Failure:** 사용자 설정 자체를 변경하는 범위로 확장하지 않는다.
- [x] **WF-02 — 구체적인 실행 계획**
  - **Action:** 작업 순서·산출물·중단 게이트를 먼저 제시한다.
  - **Evidence:** 2026-10-18 계획은 저장소·`1.4.1`·`develop` 기준 SHA·후보 branch를 고정하고, 본 checklist 갱신 → 두 README와 CHANGELOG 동기화 → 문서/validator 검증 → exact-head 권한 경계 보고 순서로 실행한다. PR push/생성 전 권한이 없으면 멈춘다.
  - **Failure:** 승인되지 않은 범위는 실행하지 않는다.
- [x] **WF-03 — 최초 계획 승인**
  - **Action:** 첫 계획에 대한 명시적 승인을 확인한다.
  - **Evidence:** 사용자의 `다음 단계 진행해` 지시로 승인된 1.4.1 release 경로 중 local candidate preparation을 계속한다. PR 생성·merge·stable publish 권한으로 확대하지 않는다.
  - **Failure:** 계획에 없는 외부·불가역 작업은 보류한다.
- [x] **WF-04 — 실행 계약 로드**
  - **Action:** leaf·공통 gate·writer·release·OpenAI 문서 계약을 읽는다.
  - **Evidence:** `bluetape-maintenance`, `bluetape-writer`, `release`, `openai-docs`, `common-gates.md`, writer Korean checklist와 Type E checklist를 적용했다.
  - **Failure:** 필요한 실행 계약이 없으면 편집을 중단한다.
- [x] **WF-04A — workflow receipt 초기화**
  - **Action:** 설치된 `bluetape-flow.py`로 실행 증거를 초기화한다.
  - **Evidence:** 현재 workflow P receipt(component `release-prep-1-4-1`)는 이 linked worktree의 `.bluetape`를 사용한다. 앞선 receipt는 canonical `develop` checkout을 repo root로 잘못 고정해 `BLOCKED` 처리했고, reviewer lane의 timeout/probe/interrupt/fail 이력은 그 local receipt에 보존했다. 최종 receipt는 local candidate와 대조해 handoff 전에 verify한다.
  - **Failure:** `.bluetape`를 직접 편집하지 않는다.
- [x] **WF-05 — 의존 순서대로 실행**
  - **Action:** 완료한 gate의 증거를 기록한 뒤 다음 gate로 진행한다.
  - **Evidence:** version-sync 편집 → 검증 → 독립 리뷰 시도와 bounded fallback → exact local commit → receipt `completion-check`/`verify` 순서로 수렴한다. helper 종료 증거를 보고하기 직전 다시 읽으며, push·PR·merge·tag·Release는 이 실행에 포함하지 않는다.
  - **Failure:** 누락된 gate는 완료로 주장하지 않는다.
- [x] **WF-06 — 약한 gate 복구**
  - **Action:** 초기화 입력 경로 오류를 수정하고 영향을 받은 증거를 재확인한다.
  - **Evidence:** 첫 `mutation-check`는 아직 run이 없는 worktree-local `.bluetape`에서 거부됐다. 이후 생성한 canonical-root receipt가 integration checkout을 가리킨다는 scope 오류를 확인해 `BLOCKED` 처리하고, 후보 worktree 전용 receipt를 다시 초기화했다. 첫 `stall-record`도 `--decision`에 JSON 파일 경로가 필요하다는 계약을 놓쳐 거부됐으며 receipt는 바뀌지 않았다. decision JSON/checksum을 사용한 재시도는 통과했다. `.bluetape`는 helper로만 갱신했다.
  - **Failure:** 재시도에도 증거가 맞지 않으면 실행을 중단한다.

## Type E 게이트

- [x] **E-01 — 지원 skill 선택**
  - **Action:** 문서·배포 범위에 필요한 지원 skill을 고른다.
  - **Evidence:** `bluetape-writer`, `openai-docs`, `release`를 적용했고 다이어그램/코드 언어 skill은 해당 범위가 아님을 확인했다.
  - **Failure:** 사실 출처나 문서 계약이 빠지면 작성하지 않는다.
- [x] **E-02 — 현재 원본과 이력 조사**
  - **Action:** 현재 repository, GNO 기록, 공식 설정 문서, live GitHub 상태를 확인한다.
  - **Evidence:** 이 체크리스트의 근거 섹션 및 `PUB-02` 검색 기록.
  - **Failure:** live 상태가 달라지면 의존 gate를 다시 실행한다.
- [x] **E-03 — 동작과 소유권 보존**
  - **Action:** public reference만 추가하고 installer·사용자 config·chezmoi source를 변경하지 않는다.
  - **Evidence:** 변경 파일은 README/CHANGELOG/docs이며 install script와 skill inventory는 diff 밖이다.
  - **Failure:** 개인 설정 동기화가 섞이면 해당 변경을 분리한다.
- [x] **E-04 — managed source apply/parity**
  - **Action:** 적용 가능한 경우 managed source와 live target parity를 증명한다.
  - **Evidence:** N/A — user-scope config/skill/hook/chezmoi target을 수정하지 않았다.
  - **Failure:** user-scope 변경이 추가되면 이 행을 다시 연다.
- [x] **E-05 — 유지보수 검증**
  - **Action:** 공개 bundle validator, 한국어 용어 audit, 링크·JSON·diff 검사를 실행한다.
  - **Evidence:** 이번 편집 이후 `./scripts/validate.sh` 통과(151 tests, 164 subtests, diagram 50 tests), README의 `v1.4.0` 참조 0건 및 `v1.4.1` 참조 일치, CHANGELOG heading/link 확인, `git diff --check` 통과, 새 lesson 후행 공백 0건. 현재 terminology rules는 `clinic-appointment` 전용이라 본 문서에는 적용되지 않음; 해당 없는 audit을 실행하지 않고 자연스러움은 아래 inline fallback review에서 확인한다. machine-surface self-audit과 chezmoi sync는 N/A: 해당 runtime surface 변경 없음.
  - **Failure:** 실패한 적용 gate가 있으면 PR 전 수리한다.
- [x] **E-06 — durable pre-PR proof**
  - **Action:** 변경 diff·교훈·독립 review 또는 승인된 inline fallback·exact commit을 수렴한다.
  - **Evidence:** 현재 candidate diff와 새 lesson을 inline fallback으로 검토하고 P0/P1=0을 기록했다. reviewer 실행은 timeout 후 중단됐으며 독립 attestation으로 계산하지 않는다. final local commit과 receipt의 exact-head 확인을 함께 기록한다. PR #40의 이전 review는 새 변경 증거가 아니다.
  - **Failure:** 필요한 증거가 없으면 PR을 만들지 않는다.
- [ ] **E-07 — 공통 PR delivery**
  - **Action:** CG-11..15에 따라 PR을 준비하고 정확한 상태를 보고한다.
  - **Evidence:** version-sync 후보 PR은 생성·push 권한이 확인되지 않아 미실행이다. PR #40은 선행 문서 변경의 과거 이력일 뿐 새 후보의 PR 증거가 아니다.
  - **Failure:** exact candidate SHA에 대한 별도 권한과 검증 없이 PR을 생성하지 않는다.
- [ ] **E-08 — fresh merge approval 이후 closeout**
  - **Action:** 사용자 승인 후 CG-16..18을 순서대로 실행한다.
  - **Evidence:** merge, canonical sync, 정리, GNO 결과.
  - **Failure:** 승인 전에는 merge/정리를 하지 않는다.

## Writer Gate

- [x] **SPW-01..05 — 수동 설정 안내**
  - **Action:** EN/KO 안내의 독자·출처·구조·정확성·최종 렌더를 확인한다.
  - **Evidence:** official Codex/OMX 근거와 22 role JSON parity 확인; 독립 문서 리뷰 2회에 걸친 수정 후 final `PASS`, 남은 actionable finding 없음.
  - **Failure:** source mismatch가 있으면 문서를 고친 뒤 관련 검증을 반복한다.
- [x] **SPW-01..05 — workflow 교훈**
  - **Action:** 관찰·근거·결정·재발 방지 guard가 있는 교훈을 검토한다.
  - **Evidence:** `docs/lessons/2026-10-17-workflow-owner-file-path.md`를 commit `6629cd9c2b6977fbbdd0f2ba4505df2e272343d8`에 포함; 정확한 commit 독립 검토에서 사실·guard 모두 `PASS`.
  - **Failure:** 재사용 가능한 guard가 없으면 교훈을 확정하지 않는다.
- [x] **SPW-01..05 — 릴리스 계획/checklist**
  - **Action:** 승인 범위·순서·evidence·release hold를 마지막으로 다시 읽는다.
  - **Evidence:** 본 checklist의 `1.4.1` 후보·기준 SHA·권한 hold를 현재 상태에 맞춰 read-back했고, PR #40 이력과 새 후보 증거를 분리했다.
  - **Failure:** 빠진 gate나 잘못된 authority가 있으면 PR 전 고친다.
- [x] **SPW-01..05 — `README.md`**
  - **Action:** 버전 예제와 한국어 README의 대응 내용·독자 안내를 검토한다.
  - **Evidence:** `README.md`와 `README.ko.md`의 clone/update 명령이 모두 `v1.4.1`; 이전 tag 문자열 없음, EN/KO stable-install·develop 안내 대응과 수동 설치 경계를 확인했다.
  - **Failure:** 영어·한국어 예제가 서로 다르면 후보를 제출하지 않는다.
- [x] **SPW-01..05 — `docs/lessons/2026-10-18-release-promotion-preflight.md`**
  - **Action:** 관찰한 사실·결정·재발 방지 guard와 자연스러운 한국어를 검토한다.
  - **Evidence:** 새 lesson을 main-session inline fallback으로 검토했다. 독립 reviewer timeout은 기록했으며 이 verdict는 독립 attestation이 아니다. 적용 가능한 terminology series는 없다.
  - **Failure:** 근거를 넘어서 일반화하거나 승인 경계를 흐리지 않는다.
- [x] **KO-01..07 — `docs/codex-model-routing.ko.md`**
  - **Action:** 자연스러움·용어·사실·JSON·locale 링크를 확인하고 contextual terminology audit을 실행한다.
  - **Evidence:** writer checklist 수동 확인; 5개 Korean-file audit에서 이 파일 finding 0건; English counterpart 링크와 JSON parity 통과.
  - **Failure:** 근거 없는 의미 변경 또는 미해결 audit finding을 두지 않는다.
- [x] **KO-01..07 — `README.ko.md`**
  - **Action:** 독자용 안내·설치 경계·링크를 검토하고 용어 audit을 실행한다.
  - **Evidence:** `v1.4.1` 갱신분을 수동 read-back했고 EN/KO 대응·GitHub Releases 링크·설치 경계를 확인했다. `clinic-appointment` 전용 terminology rules는 적용하지 않는다.
  - **Failure:** 자동 적용으로 오해할 표현이 있으면 수정한다.
- [x] **KO-01..07 — `CHANGELOG.md`**
  - **Action:** 한국어 변경 요약과 코드 token 보존을 검토하고 용어 audit을 실행한다.
  - **Evidence:** `1.4.1` heading/date, `[Unreleased]` compare URL, `추가`/`변경` headings 및 신규 lesson 요약을 수동으로 확인했다. `clinic-appointment` 전용 terminology rules는 적용하지 않는다.
  - **Failure:** 기능 범위를 과장하거나 영문 분류 heading을 남기지 않는다.
- [x] **KO-01..07 — release checklist**
  - **Action:** 상태·사실·용어·최종 렌더를 검토하고 용어 audit을 다시 실행한다.
  - **Evidence:** 새 후보의 검증 상태와 권한 경계, PR #40 이력과의 분리를 최종 read-back했다. `clinic-appointment` 전용 terminology rules는 적용하지 않는다.
  - **Failure:** 미해결 terminology finding을 닫지 않는다.
- [x] **KO-01..07 — `docs/lessons/2026-10-17-workflow-owner-file-path.md`**
  - **Action:** lesson의 사실·재발 방지 guard와 자연스러운 한국어를 검토한다.
  - **Evidence:** 용어 audit finding 0건; 실제 helper containment 근거에 연결.
  - **Failure:** 관찰하지 않은 오류 원인을 단정하지 않는다.

## 독립 문서 리뷰 기록

- PR #40의 과거 독립 리뷰 기록은 그 PR의 exact head에만 해당하며, 이 `1.4.1` version-sync 후보와 새 lesson을 검증하지 않는다.
- 첫 verdict는 `REQUEST CHANGES`: OMX 강제 설정 갱신 영향·중첩 role map 보존·shell fallback 표기에서 MEDIUM 2건과 LOW 1건을 지적했다.
- 수정: scope별 dry-run과 일치하는 적용 mode, 가능한 설정 변경·보관·제거 효과를 EN/KO에 기록하고, 예제에 없는 role을 보존하도록 명시했다. shell parameter expansion 안에서 확장되지 않는 `~` fallback을 `$HOME` 경로로 바꿔 README와 가이드 모두 수정했다.
- 공식 OMX setup guide와 현재 CLI 도움말을 확인했고, 독립 재검토 후 최종 `PASS`; 남은 actionable finding은 없다.
- PR #40 exact commit `6629cd9c2b6977fbbdd0f2ba4505df2e272343d8` 최종 검토: `PASS`; 그 변경 전체와 checklist/lesson을 포함했고 actionable finding이 없었다. 이 증거는 현재 candidate로 승계하지 않는다.
- 이번 `1.4.1` 후보의 독립 리뷰 lane은 startup timeout 뒤 bounded probe에도 verdict를 내지 않아 helper liveness 절차에 따라 interrupt/fail로 보존했다. 재시도 루프를 만들지 않고 아래 inline fallback을 수행했다.
- Inline fallback review 범위: README EN/KO 버전 예제와 독자 계약, CHANGELOG heading/date/compare 링크, checklist 승인·상태, lesson의 근거·결정·재발 방지, ignored local release rule과 공개 범위.
- Inline fallback finding: 심각 0, 중요 0, 사소 0. README는 의도한 `v1.4.1` target과 일치하고, 미공개 tag/PR/merge/release를 완료된 사실로 표현하지 않으며, 기존 installer·canonical skill·chezmoi 범위를 변경하지 않았다.
- Inline fallback 검증: `./scripts/validate.sh` 통과, README/CHANGELOG parity 확인, tracked diff whitespace 검사와 신규 lesson whitespace 검사 통과. 이는 main-session 자체 검토이며 독립 attestation이 아니다.
- Inline verdict: PASS; P0=0, P1=0.
- Exact local commit은 이 checklist/inline review report를 포함한다. PR 생성 승인이 있으면 live branch/head와 원격 checks/reviews/threads를 별도로 다시 확인한다.

## Common Workflow 게이트

- [x] **CG-01 — authority 재확인**
  - **Action:** 현재 AGENTS, plan, status, diff를 확인한다.
  - **Evidence:** user/workspace/repository guidance, `$release`, `$bluetape-maintenance`, `$bluetape-writer`, common gates 및 current clean canonical `develop`를 확인했다. 현재 계획은 `1.4.1` version-sync 후보 준비로 제한된다.
  - **Failure:** 지침이 달라지면 영향받은 gate를 다시 연다.
- [x] **CG-02 — historical/live 조사**
  - **Action:** GNO를 검색하고 직접 live GitHub를 확인한다.
  - **Evidence:** 이번 turn GNO에서 repository/domain/action 검색은 관련 결과 없음; live default `develop`, 최신 release `v1.4.0`, PR #40 head `6c527b92b6ed4c67efbf4c092459e55f9f3d0181`가 merge commit `31e69c613e9f908bec27f3a7ebee6e34cabebe21`으로 병합됨, workflows 없음.
  - **Failure:** 불명확한 이력에 의존해 외부 변경을 하지 않는다.
- [x] **CG-03 — 기존 작업 보호**
  - **Action:** clean integration checkout에서 격리 worktree를 만든다.
  - **Evidence:** 원래 `develop` clean 유지; `.worktrees/release/bluetape-skills-1.4.1`에서 `release/bluetape-skills-1.4.1`을 `31e69c6` 기준으로 생성했다. 기존 `promote-bluetape-skills-1.4.0` worktree는 보존한다.
  - **Failure:** 기존 dirty 상태는 보존한다.
- [x] **CG-04 — 언어/소유 경계**
  - **Action:** 외부 문서 한국어·README locale·public/private 경계를 지킨다.
  - **Evidence:** 한·영 개별 안내; installer와 private runtime 파일은 변경하지 않는다.
  - **Failure:** 개인 설정 또는 잘못된 언어가 섞이면 분리한다.
- [x] **CG-05 — 기존 패턴 재사용**
  - **Action:** 기존 skill model-routing 계약과 README/installer 패턴을 따른다.
  - **Evidence:** 기존 README stable-install/update 예제와 CHANGELOG link 형식을 따른다. installer/API abstraction은 변경하지 않는다.
  - **Failure:** 근거 없는 신규 설정 표면을 추가하지 않는다.
- [x] **CG-06 — 문서/locale 계약**
  - **Action:** EN/KO 안내와 README 항목을 연결하고 설정의 수동 성격을 설명한다.
  - **Evidence:** 두 README의 stable clone/update 명령이 모두 `v1.4.1`이고 EN/KO 경로가 대응한다. 이전 `v1.4.0` 문자열은 README에서 0건이며 GitHub Releases 링크와 수동 적용 안내를 확인했다.
  - **Failure:** 한 locale 또는 실행 예제가 빠지면 PR을 멈춘다.
- [x] **CG-07 — 최소 검증**
  - **Action:** 실제 변경 범위를 검증하는 최소 명령을 실행한다.
  - **Evidence:** `./scripts/validate.sh` 통과(151 tests, 164 subtests, diagram 50 tests); tracked `git diff --check` 통과; 신규 lesson 후행 공백 검사 통과; README 버전 refs 및 CHANGELOG release heading/compare URL 일치.
  - **Failure:** 실패 결과를 분류하고 수리 후 재실행한다.
- [x] **CG-08 — 무거운 검증 직렬화**
  - **Action:** 해당하는 DB/native/emulator/benchmark 검증을 직렬로 수행한다.
  - **Evidence:** N/A — 문서 전용이며 그런 검증을 시작하지 않았다.
  - **Failure:** 해당 검증이 추가되면 병렬 실행을 피한다.
- [x] **CG-09 — lesson gate**
  - **Action:** 재사용 가능한 릴리스 선행 조건 누락을 기록하고 독립 검토를 우선 시도한다; 실패 시 inline fallback과 commit을 사용한다.
  - **Evidence:** `docs/lessons/2026-10-18-release-promotion-preflight.md`에 관찰·결정·guard를 기록하고 checklist의 inline review에 함께 검토했다. workflow receipt는 독립 reviewer 실패를 보존한다. 이전 사용자 요청인 “결정이 필요하면 대상과 선택의 의미를 자세히 설명할 것”도 checklist의 버전·branch·권한 hold에 반영했다.
  - **Failure:** 교훈 증거 없이 pre-PR 검토로 진행하지 않는다.
- [x] **CG-10 — final pre-PR 수렴**
  - **Action:** 독립 review를 우선 시도한다. 불가하면 inline fallback에서 P0/P1을 해소하고 exact local commit을 만든다.
  - **Evidence:** 독립 review 실행 실패 후 workspace-approved inline fallback verdict `PASS; P0=0, P1=0`을 checklist에 기록하고 exact local commit을 생성한다. remote PR/check evidence는 포함하지 않는다.
  - **Failure:** unresolved P0/P1 또는 dirty diff이면 PR을 만들지 않는다.
- [ ] **CG-11 — PR authority 확인**
  - **Action:** 대상 repository/base/head와 PR 생성 권한을 확인한다.
  - **Evidence:** 제안 pair는 `bluetape4k/bluetape-skills`, `develop`, `release/bluetape-skills-1.4.1`; 사용자가 이 exact pair와 candidate head의 PR 생성 권한을 승인하기 전까지 PENDING.
  - **Failure:** 범위를 벗어난 PR을 생성하지 않는다.
- [ ] **CG-12 — exact branch push**
  - **Action:** 수렴된 head를 원격에 push하고 SHA를 되읽는다.
  - **Evidence:** exact-head PR 생성 authority 이후 push 결과와 local/remote SHA를 기록한다.
  - **Failure:** 원격 head가 다르면 덮어쓰지 않고 멈춘다.
- [ ] **CG-12A — PR 직전 guidance 갱신**
  - **Action:** PR 생성 직전 AGENTS·leaf/common gate·template·issue metadata를 다시 읽는다.
  - **Evidence:** PR 생성 권한이 주어지면 exact `develop`/candidate head, 현재 template·label·milestone 및 guidance를 그 직전에 재확인한다.
  - **Failure:** guidance drift가 있으면 영향 gate를 갱신한다.
- [ ] **CG-13 — PR 생성/확인**
  - **Action:** Korean body와 `## DoD Status` 마지막 section을 사용해 PR을 만든다.
  - **Evidence:** exact-head authority 후 live PR URL/head/metadata/body를 read-back한다.
  - **Failure:** metadata/body가 다르면 CI 진행 전에 수정한다.
- [ ] **CG-14 — CI, review, thread 확인**
  - **Action:** exact-head checks와 live review/thread 상태를 확인한다.
  - **Evidence:** 새 version-sync candidate의 exact-head 독립 리뷰, live checks 및 review/thread 상태를 수집한 뒤 기록한다.
  - **Failure:** CI 실패·미해결 thread·P0/P1은 merge-ready를 막는다.
- [ ] **CG-15 — merge-ready 보고**
  - **Action:** gate 수와 PR/head를 reconcile해 사용자에게 보고한다.
  - **Evidence:** 새 version-sync PR의 exact head와 checks/리뷰/N/A 수를 보고한다. PR #40은 이미 `31e69c6`으로 병합됐으며 새 PR 상태를 대신하지 않는다.
  - **Failure:** 누락 증거가 있으면 fresh merge 승인을 요청하지 않는다.
- [ ] **CG-16 — fresh merge 승인**
  - **Action:** merge-ready 보고 뒤 exact PR/head에 대해 새 승인을 받는다.
  - **Evidence:** 승인 전에는 이 행이 PENDING이다.
  - **Failure:** plan approval로 merge를 대신 승인하지 않는다.
- [ ] **CG-17 — merge 확인**
  - **Action:** fresh approval 후에만 merge하고 GitHub 상태/merge SHA를 확인한다.
  - **Evidence:** live merged state와 SHA.
  - **Failure:** 승인 없이 merge하지 않는다.
- [ ] **CG-17A — canonical checkout 동기화**
  - **Action:** merge 검증 후 canonical `develop` checkout을 동기화한다.
  - **Evidence:** local/upstream SHA, ancestry, 기존 worktree 상태.
  - **Failure:** dirty state를 덮어쓰지 않는다.
- [ ] **CG-17B — 승인된 task 정리**
  - **Action:** 동기화 후 이 작업이 만든 안전한 worktree/branch만 정리한다.
  - **Evidence:** exact merged commit과 clean/preserved 상태.
  - **Failure:** 미병합이거나 모호한 작업은 삭제하지 않는다.
- [ ] **CG-18 — canonical GNO lesson index**
  - **Action:** merge/sync/정리 후 기존 collection에 lesson을 색인하고 검색한다.
  - **Evidence:** canonical checkout의 `gno update`, `gno embed`, 대표 `gno search`와 commit SHA.
  - **Failure:** feature worktree에서 색인하지 않는다.
- [ ] **CG-X01 — 불가역 배포 action 승인**
  - **Action:** stable main promotion/tag/release 직전에 정확한 SHA와 fresh approval을 확인한다.
  - **Evidence:** 이번 계획 승인은 이 action을 허용하지 않는다.
  - **Failure:** 승인 없이는 main merge, tag, Release를 실행하지 않는다.

## Stable Release 게이트

- [x] **PUB-01 — release 대상/authority 고정**
  - **Action:** 버전, 이전 공개 버전, 범위와 hold를 기록한다.
  - **Evidence:** 최신 공개 릴리스 `v1.4.0`; 목표 `1.4.1`; 수동 참고자료 소비자 범위; `develop` 기준 SHA `31e69c613e9f908bec27f3a7ebee6e34cabebe21`. `develop` <- `release/bluetape-skills-1.4.1` 후보 쌍은 제안 상태이며 외부 push/PR 권한은 미승인이다. `main`/tag/Release 보류를 유지한다.
  - **Failure:** 후보 version이나 authority가 달라지면 재계획한다.
- [x] **PUB-02 — live/historical 확인**
  - **Action:** GNO 이력과 live branch/release/PR/workflow 상태를 확인한다.
  - **Evidence:** 아래 GNO 검색에서 현재 후보와 관련한 결과는 없었다. Live GitHub에서 public/default `develop`, 최신 `v1.4.0`, PR #40 병합, GitHub Actions workflow 부재, `v1.4.1` tag/Release 부재를 확인했다. 현재 release PR은 아직 생성하지 않았다.
  - **Failure:** stale GNO를 live GitHub 사실로 취급하지 않는다.
- [x] **PUB-03 — canonical skill parity**
  - **Action:** 변경된 canonical skill 수와 public parity를 확인한다.
  - **Evidence:** N/A — canonical skill bytes와 manifest를 수정하지 않았다.
  - **Failure:** skill 내용 변경이 생기면 source parity gate를 연다.
- [ ] **PUB-04 — release validation**
  - **Action:** exact stable candidate에 validator·archive·checksum·isolated install을 실행한다.
  - **Evidence:** 이번 version-sync 편집 후 `./scripts/validate.sh`는 통과했다(151 tests, 164 subtests, diagram 50 tests). 다만 이 gate가 요구하는 exact stable candidate의 tag/archive/checksum/isolated-install 증명은 아직 없으며 승인된 stable release 단계에서 수행한다.
  - **Failure:** tag 대상 산출물 검증이 없으면 release하지 않는다.
- [ ] **PUB-05 — develop PR merge-ready/main promotion hold**
  - **Action:** exact `develop` PR 검증 후 `main` 승격 범위를 다시 고정한다.
  - **Evidence:** PR #40은 현재 `develop` 기준에 병합됐지만, `1.4.1` 버전 동기화 후보 PR은 아직 생성·검토되지 않았다. 새 PR의 exact-head merge-ready 확인 후 `main` 승격 보류 조건을 갱신한다.
  - **Failure:** stale head나 unresolved check이면 승격하지 않는다.
- [ ] **PUB-06 — exact SHA integration**
  - **Action:** 승인된 merge 및 `main` target SHA를 검증한다.
  - **Evidence:** 아직 merge 권한을 받지 않았다.
  - **Failure:** 다른 SHA를 release target으로 선택하지 않는다.
- [ ] **PUB-07 — tag와 GitHub Release**
  - **Action:** 별도 fresh approval 뒤 SSH-signed immutable `v1.4.1` tag와 Release를 생성한다.
  - **Evidence:** 현재 미승인/미실행.
  - **Failure:** approval 전에는 tag나 Release를 만들지 않는다.
- [x] **PUB-08 — downstream consumer sync**
  - **Action:** automated consumer update 대상을 확인한다.
  - **Evidence:** N/A — 문서는 독자별 수동 적용이며 자동 downstream consumer가 없다.
  - **Failure:** 자동 동기화가 발견되면 별도 승인/계획을 요구한다.
- [x] **PUB-09 — next development line**
  - **Action:** 다음 개발 line 변경을 확인한다.
  - **Evidence:** N/A — 별도 승인 없이는 이번 범위에 포함하지 않는다.
  - **Failure:** 후속 feature를 이 PR에 끼워 넣지 않는다.
- [ ] **PUB-10 — locale/release archive/checksum**
  - **Action:** release 시 README locale, Korean notes, `.tar.gz`, `.zip`, `SHA256SUMS`를 검증한다.
  - **Evidence:** release tag가 아직 승인·생성되지 않았다.
  - **Failure:** 불일치 artifact를 게시하지 않는다.
- [ ] **PUB-11 — artifact와 residual risk 보고**
  - **Action:** URL, SHA, isolation 결과, 잔여 위험을 최종 보고한다.
  - **Evidence:** tag/release 이후 수집한다.
  - **Failure:** 미게시 산출물을 완료로 표현하지 않는다.

### Historical Search Ledger

- Initial GNO query: `bluetape-skills Codex model config public bundle manual settings release` in `bluetape4k-github`, `bluetape4k-docs`, `bluetape4k-wiki`.
- Reformulated queries: `bluetape-skills model routing reference manual config codex`, `bluetape-skills public model configuration example`, `model routing manual setup codex`; no relevant issue/PR/release/lesson was found.
- Current release-prep queries: `bluetape-skills v1.4.1 release stable promotion main tag GitHub Release` (`bluetape4k-github`), `bluetape-skills release v1.4.0 v1.4.1 main tag stable branch` (`bluetape4k-docs`), and `public skill bundle release promotion main immutable tag GitHub Release` (`bluetape4k-wiki`); no relevant results. Live GitHub read-back supplies current authority.
- Live GitHub remains the authority for default branch, release, PR and workflow state.

## 중단 조건

- 새 모델/effort가 수신자의 공식 Codex 설정 문서나 OMX 설정 schema에서 확인되지 않으면 해당 예제를 공개하지 않는다.
- 사용자별 설정 값은 공개하지 않으며 예제 JSON은 model 관련 두 key만 담는다. 기존 JSON의 다른 key는 보존하도록 안내한다.
- PR head가 바뀌면 exact-head review·CI·상태 evidence를 다시 수집한다.
- Merge, `main` 승격, tag, release는 각 대상 SHA와 hold 상태를 다시 읽고 사용자가 별도로 승인하기 전에는 실행하지 않는다.
- 후보 branch push/PR 생성도 사용자가 저장소, base `develop`, head `release/bluetape-skills-1.4.1`, 검토된 candidate SHA를 지정해 승인하기 전까지 보류한다.

## 결과 기록

최종 갱신 시 각 적용 gate의 상태와 증거, PR URL/head SHA, fresh approval, merged `main` SHA, tag/Release URL, archive checksum 및 isolated installation 결과를 기록한다. 현재 미실행된 게시 게이트를 통과한 것으로 표현하지 않는다.
