# gpt-5.6 skill 단순화 교훈

## 맥락

router, common gate, leaf skill, reference가 같은 승인·상태·liveness 규칙을
서로 풀어 써서 지침이 길어지고 변경 시 drift 위험이 커졌다. Korean
naturalness reference도 작업별 용어와 사례를 계속 누적해 758줄까지
증가했다.

## 결정

- router는 분류와 leaf 선택, checklist contract는 상태와 row shape,
  common gates는 공통 실행 gate, leaf는 type-specific delta만 소유한다.
- topology와 liveness 순서는 해당 reference에만 두고 router는 링크한다.
- 모델 ID는 skill에 고정하지 않고 현재 `AGENTS.md`와 installed catalog에서
  해석한다.
- 자연스러움 reference는 재사용 가능한 register와 검증 경계만 유지하고,
  article-specific 사례는 task lesson에 남긴다.

## 결과와 검증

`bluetape-workflow/SKILL.md`는 302줄에서 약 200줄,
`bluetape-maintenance/SKILL.md`는 136줄에서 117줄로 줄었다. live canonical
14개 skill을 전체 export한 뒤 `scripts/validate.sh`에서 144개 test,
159개 subtest가 통과했고 1개 source-only test만 공개 bundle 경계에 따라
skip됐다.

## 다음 작업 원칙

규범에는 canonical owner를 하나만 둔다. leaf가 공통 gate를 다시 설명하기
시작하거나 reference가 task별 사례를 축적하면 ID/file 참조로 되돌리고,
machine contract는 schema·script·test로 검증한다.
