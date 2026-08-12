# Superpowers 기술 산출물에 `bluetape-writer` 필수 게이트를 연결한 교훈

## 맥락

`bluetape-writer`는 specification, design, plan, code review, lesson을 적용
대상으로 선언했지만, `bluetape-workflow`의 명시적 로딩 조건은 blog/article과
Korean README에만 연결되어 있었다. `bluetape-full-feature`도 design에는
`brainstorming`, plan에는 `writing-plans`만 요구했다. 따라서 한국어로만
작성하거나 native `writer` 역할을 호출한 뒤 `bluetape-writer` 검증을
생략해도 체크리스트가 이를 차단하지 못했다.

## 결정

- brainstorming/design discussion, specification/design, implementation plan,
  review, lesson을 `Superpowers technical artifact`로 묶었다.
- 산출물마다 `SPW-01`부터 `SPW-05`까지 새로 적용한다. 다른 산출물의
  검증 결과를 재사용하지 않는다.
- 사실과 독자 범위를 먼저 고정하고, 산출물별 구조, 한국어 기술 문체,
  근거 추적, 최종 되읽기를 순서대로 검증한다.
- 대화에만 남는 임시 문구와 근거가 있는 `N/A` lesson에도 같은 게이트를 적용한다.
- 기술적 의미, 결정, 범위, 근거, 심각도, 검증 주장, 독자용 구조가 바뀌면
  `materially revised`로 판정한다. 단순 철자·구두점·레이아웃 수정은
  `SPW-05` 최종 되읽기만 다시 수행한다.
- 독립 검토 메모를 최종 verdict, 사용자 응답, 영속 review artifact로
  통합하는 순간 새 산출물로 보고 전체 게이트를 적용한다.
- native `writer` 역할의 출력은 보조 증거일 뿐이며, 소유 세션이 최종
  산출물과 `SPW-*` 상태를 검증한다.
- Type A 산출물에는 이미 선택된 상위 workflow를 유지한다. 문서라는 이유로
  별도 Type E workflow를 중첩하지 않는다.

## 결과

`bluetape-workflow`가 writer 적용의 필수 게이트를 소유하고,
`bluetape-writer`가 산출물별 체크리스트를 소유하도록 책임을 나눴다.
`bluetape-full-feature`의 A-03, A-04, A-08, A-09와 관련 세부 단계는
`SPW-01..05` PASS를 진행 조건으로 요구한다. 언어 정책 준수나 CI 성공은
writer 증거를 대신할 수 없다.

## 검증

- 변경 전 회귀 테스트가 `Superpowers technical artifact` 계약 부재로
  실패하는 것을 확인했다.
- 독립 읽기 전용 분석에서 router와 Type A 필수 로딩 표의 누락,
  Type E 중첩 가능성, native role과 skill의 혼동을 재현했다.
- 관리 원본 workflow 테스트 147개가 통과했다.
- 공개 bundle 검증에서 workflow 테스트 146개와 subtest 164개가 통과했고,
  source-only test 1개만 기존 bundle 경계에 따라 `skip`됐다.
- diagram 테스트 50개와 `git diff --check`가 통과했다.

## 놓친 점과 복구

처음에는 writer 범위 선언만으로 skill 적용이 강제된다고 볼 수 있었다.
그러나 필수 로딩 표와 실행 체크리스트에 증거 항목이 없으면 누락을
기계적으로 판정할 수 없다. 또한 기존 문구는 design/plan/review/lesson에도
Type E를 사용하라고 읽혀 Type A workflow와 충돌했다. 회귀 테스트와 독립
분석을 먼저 수행해 두 문제를 같은 변경에서 복구했다.

## 다음 작업 원칙

새 규칙이 실제로 다음 단계를 막아야 한다면 description이나 언어 정책에만
두지 않는다. 규범 소유자에 체크리스트 ID와 실패 상태를 정의하고,
실행 leaf skill에는 그 ID의 PASS 증거를 요구한다. 역할 이름과 skill 이름이
비슷해도 자동으로 같은 계약을 수행한다고 가정하지 않는다.
