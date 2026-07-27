# Live skill 공개 bundle 동기화와 workflow gate 교훈

## 맥락

`~/.codex/skills`의 최신 canonical skill을 `bluetape-skills` 공개 bundle로
동기화하는 과정에서 기본 `develop` checkout에 기존 미커밋 변경이 남아
있었다. 동시에 user-scope hook 수정은 개인 `dotfiles` 저장소에, 공개
bundle 변경은 `bluetape-skills` 저장소에 반영해야 했다.

기존
`docs/lessons/2026-07-14-bluetape-skills-1.1.0-bundle.md`의 다음 원칙은
그대로 재사용했다.

- canonical skill은 파일을 선별하지 않고 디렉터리 전체를 export한다.
- compatibility alias, 개인 설정, hook, memory, runtime state와 cache는
  공개 bundle에서 제외한다.
- chezmoi의 `executable_` 파일명은 공개 target 이름으로 변환한다.

이번 작업에서는 저장소별 delivery 관행, hook target 판별, workflow receipt
수명주기, source-only 테스트의 공개 이식성, lesson gate 누락이라는 새로운
실패와 복구 조건이 추가로 드러났다.

## 실패와 원인

### 저장소 운영 관행을 확인하기 전에 PR을 만들었다

`dotfiles`에도 일반 Bluetape 저장소와 같은 PR 흐름을 적용했지만, GNO에는
그 의무를 뒷받침하는 기록이 없었고 실제 최근 Git/GitHub 이력은 `main`
직접 push가 관행이었다. 저장소 유형과 과거 delivery 이력을 확인하지 않고
공통 workflow만 기계적으로 적용한 것이 원인이었다.

### hook이 실제 worktree가 아닌 최초 workspace를 mutation 대상으로 보았다

현재 세션의 hook context는 비-Git 명령의 tool workdir를 최초
`bluetape-skills/develop` workspace로 해석했다. 그 결과 격리 worktree에서
실행한 검증 스크립트와 파일 동기화도 integration checkout mutation으로
오인됐다. Git 명령은 명령 자체에 절대 `git -C <worktree>`를 포함해야 실제
대상을 안정적으로 판별할 수 있었다.

### 중복 running receipt가 lifecycle 복구 명령까지 막았다

worktree 생성용 receipt와 실제 동기화용 receipt의 대상 범위가 겹치자
mutation-check가 단일 권한을 선택하지 못했다. 더 큰 문제는 같은 모호성
때문에 `run-cancel`도 차단되어 공식 lifecycle 명령으로 중복 receipt를
정리하는 경로가 deadlock된 점이다.

### source-only 테스트가 공개 bundle 경계를 침범했다

live workflow 테스트가 chezmoi source checkout의 `AGENTS.md`와 외부
`doctor` skill을 직접 읽었다. 이 파일들은 canonical 공개 bundle의 구성
요소가 아니므로 그대로 export하면 fresh bundle 검증이 실패했다.

### lesson gate 전에 PR과 완료 상태를 보고했다

작업에는 재사용 가능한 새 교훈이 있었지만 CG-09를 평가하지 않은 채 PR을
만들고 완료를 선언했다. 이는 CG-09 -> CG-10 -> CG-11 이후의 물리적 gate
순서를 어겼으며, WF-06에 따라 완료 선언을 철회하고 누락된 gate를
복구해야 하는 상태였다.

## 결정과 복구

- mutation 전에 GNO를 검색하고, 결과가 없으면 다른 collection과 실제
  Git/GitHub 이력을 확인해 저장소별 delivery 관행을 결정한다.
- 개인 `dotfiles`와 공개 `bluetape-skills`의 delivery 방식을 같은 규칙으로
  추정하지 않는다.
- dirty integration checkout은 정리하거나 덮어쓰지 않는다. 기존 격리
  checkout을 setup source로 사용해 별도 worktree와 branch를 만든다.
- Git mutation은 명령에 절대 `git -C <worktree>`를 포함해 hook이 실제
  target을 판별할 수 있게 한다.
- 동시에 겹치는 running receipt를 만들지 않는다. setup receipt를 정상
  종료한 뒤 실제 작업 receipt를 시작한다.
- receipt가 겹쳐도 `run-cancel`, `run-block` 같은 lifecycle 복구 명령은
  run id와 owner authority로 안전하게 실행될 수 있어야 한다. 이 속성이
  없으면 fail-closed 정책 자체가 복구 deadlock을 만든다.
- source checkout에만 존재하는 교차-surface 테스트는 공개 경계를 넓히지
  않는다. 필요한 외부 surface가 없을 때는 구체적인 사유로 skip하고,
  canonical bundle 자체의 계약 검증은 계속 실행한다.
- CG-09의 lesson path 또는 근거 있는 `N/A`가 확인되기 전에는 PR을
  merge-ready나 작업 완료로 보고하지 않는다.

## 결과와 검증

- live canonical 14개 skill과 격리 공개 bundle의 파일 inventory와 내용이
  일치했다. 공개 전용 portability guard 한 곳만 의도적인 변환으로 남겼다.
- compatibility alias, 개인 상태와 cache는 공개 bundle에 포함되지 않았다.
- `scripts/validate.sh`는 14 canonical skill, workflow contract, diagram
  audit와 공개 경계를 검증했다.
- 빈 임시 `CODEX_HOME` 설치에서 14/14 skill이 설치됐고 inventory와 내용
  불일치가 없었다.
- 기존 `develop`의 미커밋 변경은 그대로 보존했다.

## 다음 작업 원칙

Bluetape 작업은 공통 workflow를 실행하는 것만으로 완료되지 않는다.
mutation 전에 저장소별 운영 관행을 확인하고, 각 required gate를 물리적
순서대로 증명해야 한다. 특히 reusable learning, novel failure, recovery,
design, operational guidance 중 하나라도 존재하면 committed lesson을
CG-09에서 먼저 만들고 검증한 뒤에만 PR 생성과 merge-ready 보고로
진행한다.
