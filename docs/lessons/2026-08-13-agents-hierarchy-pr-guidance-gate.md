# AGENTS.md 계층과 PR 직전 기준 정보 재확인 교훈

## 맥락

관리되는 live `bluetape-workflow`에는 user-scope, workspace, repository/worktree
`AGENTS.md`를 읽는 `WF-00`과 PR 직전 guidance를 다시 읽는 `CG-12A`가 추가됐다.
공개 `bluetape-skills`는 관리자의 live skill이나 chezmoi 원본을 자동 복제하는
저장소가 아니므로, 안정화된 계약을 별도 검토 후 공개 bundle에 승격해야 한다.

## 결정

- 분류 전에 세 scope의 `AGENTS.md`를 순서대로 읽고 누락·읽기 실패를 차단한다.
- `gh pr create` 또는 PR update 직전에 같은 계층, leaf skill, common gate, PR
  template, linked issue metadata를 다시 읽는다.
- 한국어 설명에서는 guidance를 `기준 정보` 또는 `원본`으로 표현하고, public
  bundle에는 workflow manifest·PR template·contract test까지 함께 배포한다.

## 결과와 검증

- 공개 후보에 `WF-00`, `CG-12A`, manifest dependency, PR DoD template, 회귀
  검증을 반영했다.
- `uv run --with pytest pytest -q skills/bluetape-workflow/tests`는
  `147 passed, 1 skipped, 164 subtests passed`를 기록했다.
- `./scripts/validate.sh`는 14개 canonical skill, workflow contract, diagram
  audit, public bundle boundary를 PASS했다. `code-review`와 `self-audit`는
  공개 bundle 밖의 companion skill이라 선언된 경고만 남겼다.

## 다음 작업을 위한 guard

공개 bundle을 live skill 또는 chezmoi 원본과 동기화할 때는 파일을 자동으로
덮어쓰지 말고, 이 저장소의 `develop` PR과 `main` 승격을 별도 검토 단계로
수행한다. PR 생성 직전 guidance snapshot과 linked issue metadata를 다시
확인하지 못하면 PR을 만들지 않는다.

## Writer DoD

- `SPW-01`: 공개 workflow lesson, 한국어 독자, 현재 후보 파일·명령·수치·범위를 고정했다.
- `SPW-02`: 맥락, 결정, 결과·검증, 다음 guard를 포함했다.
- `SPW-03`: 한국어 기술 문체와 `기준 정보`/`원본` 용어를 검토했다.
- `SPW-04`: 현재 worktree와 validator/test 결과를 대조했다.
- `SPW-05`: 최종 Markdown을 다시 읽고 표기·명령·수치·식별자 parity를 확인했다.
