# 변경 기록

Bluetape Skills의 주요 변경 사항을 이 파일에 기록합니다.

## [Unreleased]

## [1.3.2] - 2026-08-08

### 추가

- `$bluetape-diagram`에 semantic ledger와 semantic audit를 추가해 diagram의
  의미 계약, 관계 방향, 표시되는 connector를 렌더링 전에 검증하도록 했습니다.
- 화살촉 방향·크기·terminal segment, SVG/PNG asset pair, visual geometry,
  mixed-corner와 shared connector를 자동 점검하는 audit script와 회귀 테스트를
  추가했습니다.

### 변경

- orthogonal connector의 rounded corner와 화살촉 여유를 제작 계약으로 고정하고,
  README workflow diagram도 SVG와 원본 크기 PNG에서 같은 둥근 꺾임을 유지하도록
  보강했습니다.
- 반복적으로 지적된 diagram 제작 lesson을 reusable `$bluetape-diagram`
  reference와 공개 bundle 검증 게이트로 승격했습니다.

## [1.3.1] - 2026-08-07

### 변경

- 한국 개발자가 주 독자인 기준으로 GitHub issue/PR 제목·본문·댓글과 push 대상 commit message를 한국어로 작성하도록 운영 규칙을 통일했습니다.
- KDoc, RustDoc, Go doc comment, Python docstring 등 독자가 읽는 코드 주석을 한국어로 작성하도록 기준을 정리했습니다.
- `WIP.md`, `docs/**/*.md`, `CHANGELOG.md`, release notes는 한국어로 작성하고, `AGENTS.md`, `CLAUDE.md`, `SKILL.md` 등 AI-facing 운영 문서는 영어로 유지하도록 경계를 명확히 했습니다.
- 코드 식별자, 명령, URL, 정확한 오류 메시지, machine-readable token은 원문을 보존하도록 예외를 명시했습니다.

## [1.3.0] - 2026-07-31

### 변경

- GPT-5.6용 canonical workflow 계약의 공통 의미를 한 소유자에게 모으고,
  leaf skill은 유형별 차이에 집중하도록 단순화했습니다.
- 재사용 가능한 workflow reference와 결정론적 공개 다이어그램의 검증
  경계를 명확히 하도록 `$bluetape-diagram`을 갱신했습니다.
- 재사용 reference에는 글별 사례를 남기지 않고 `$bluetape-writer`의 한국어
  문체와 자연스러움 지침을 강화했습니다.
- canonical Kotlin 및 full-feature skill 표면의 신규·의미 있는 변경 지침은
  한국어 우선으로 유지했습니다.

## [1.2.2] - 2026-07-27

### 추가

- 저장소 관행 탐색, hook 대상 확인, receipt 수명주기 복구, 공개 번들 테스트
  이식성, 완료 gate 규율을 다루는 재사용 가능한 workflow lesson을
  추가했습니다.
- Go, Kotlin, Python, Rust 구현 패턴에 운영 로그 요구사항을 추가했습니다.

### 변경

- `develop`를 기본 통합 branch로 채택하고 `main`은 검토된 안정 release
  승격에만 사용하도록 했습니다.
- DOM 기반 HTML/CSS 차트, 결정론적 캡처, 이중 언어 글꼴, 현지화된 시각
  자산에 대한 `$bluetape-diagram` 지침을 확장했습니다.
- `$bluetape-workflow`의 worktree 격리, GNO fallback, 위임 deadline,
  run-command 계약, 실패 해소 규칙을 강화했습니다.
- `$bluetape-writer`의 언어 선택, 독자 문체, 한국어 자연스러움 점검을
  명확히 했습니다.

### 버그 수정

- 실패한 review lane을 완료된 correction 또는 exact-head rereview lane과
  명시적으로 연결한 뒤 append-only coordinator 완료를 허용하되, 미해결·잘못된
  실패 해소 주장은 계속 block하도록 했습니다.
- private `AGENTS.md`와 외부 companion skill이 공개 번들에 없을 때 source-only
  workflow contract test가 명시적으로 skip하도록 했습니다.

## [1.2.1] - 2026-07-17

### 추가

- renderer에 민감한 text halo를 제거하고 CairoSVG PNG 출력의 lane·관계 label을
  보존하는 fail-closed SVG text normalizer를 추가했습니다.
- 명시적 code snippet의 semantic token highlighting을 추가하고 CSS cascade,
  inline attribute, token style, 멱등성 회귀 범위를 포함했습니다.

### 변경

- canonical PNG를 렌더링하기 전에 `$bluetape-diagram`이 `text_hazards=0`과
  `code_without_highlight=0`을 요구하도록 했습니다.

## [1.2.0] - 2026-07-17

### 추가

- 관계 label 충돌과 공유 connector segment를 검사하는
  `$bluetape-diagram` 자동 connector check를 추가했습니다.

### 변경

- connector audit 실패는 가능한 경우 `data-from`/`data-to` 관계 이름을 사용하고,
  SVG affine transform을 적용하며, 연결되지 않은 path subpath를 분리해
  유지하도록 했습니다.

## [1.1.0] - 2026-07-14

### 추가

- guard가 적용된 run/lane lifecycle command, topology 기반 완료 판정,
  liveness 처리, receipt 기반 복구, handoff, immutable live report를 제공하는
  Phase 2 native workflow runtime을 추가했습니다.
- Workflow manifest 1.1, receipt/topology/liveness 계약과 coordinator lifecycle,
  복구, 보안, lock, 규모, 렌더링 레이아웃 회귀 범위를 추가했습니다.

### 변경

- 14개 canonical Bluetape skill을 동기화해 router, maintenance, publishing,
  bug-fix, fast-track, full-feature, self-improvement gate가 현재 workflow
  계약을 공유하도록 했습니다.
- 번들 검증이 manifest inventory, 렌더링된 실행 파일 이름, 선언된 외부
  companion skill, workflow 계약, 전체 workflow test suite를 점검하도록
  확장했습니다.
- 1.1.0 번들의 영어·한국어 설치, 업데이트, runtime, 검증 지침을
  갱신했습니다.

### 보안

- owner fencing, filesystem containment, permission check, stale-lock recovery,
  receipt 검증, recovery-run provenance을 강화했습니다.

## [1.0.0] - 2026-07-11

### 추가

- reference, template, script, agent prompt를 포함한 14개 canonical Bluetape
  개발 skill의 첫 안정 공개 번들을 제공했습니다.
- private runtime state와 retired alias를 배포에서 제외하는 안전한 설치·업데이트
  script를 추가했습니다.
- 공개 번들 경계, workflow router, 7-Tier review gate를 포함한 이중 언어 설치·
  사용 지침을 추가했습니다.
- canonical inventory, 필수 skill front matter, private 또는 secret 유사
  payload 금지 여부를 검증하도록 했습니다.

[1.0.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.0.0
[1.1.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.1.0
[1.2.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.0
[1.2.1]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.1
[1.2.2]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.2
[1.3.2]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.3.2
[1.3.1]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.3.1
[1.3.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.3.0
[Unreleased]: https://github.com/bluetape4k/bluetape-skills/compare/v1.3.2...develop
