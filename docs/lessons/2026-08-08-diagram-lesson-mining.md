# Diagram lesson mining 결과와 품질 게이트 보강

## 목적

workspace의 `docs/lessons`와 review/PR 기록에서 반복된 diagram 지적을 다시
분류하고, 다음 제작에서 같은 결함이 재발하지 않도록 `bluetape-diagram`
규칙과 감사 도구로 고정했다. 이번 변경은 기존 diagram을 일괄 재생성하지
않고 제작 계약만 강화한다.

## 반복 지적

| 반복 결함 | 근거 lesson/review | 이번에 고정한 불변식 |
| --- | --- | --- |
| SVG는 정상인데 PNG에서 화살촉이 역방향이거나 선 방향과 어긋남 | `bluetape4k-projects/docs/lessons/2026-06-19-sequence-diagram-rendering-qa.md`, `bluetape4k-exposed/docs/lessons/2026-06-18-readme-diagram-geometry-audit.md`, exposed-r2dbc-workshop arrowhead PR review | marker의 local `+x` tip, `orient="auto"`/`auto-start-reverse`, 마지막 non-zero tangent, direct head의 `data-tip-direction`을 `diagram-arrowhead-audit.py`로 검사 |
| 화살촉 크기와 점선 상속이 역할별로 달라짐 | `bluetape4k-exposed/docs/lessons/2026-06-22-readme-diagram-visual-qa-followup.md`, exposed-r2dbc-workshop marker PR들 | UML/sequence/primary/secondary 크기, `userSpaceOnUse`, solid head, terminal clearance를 함께 검사 |
| 내용은 위쪽에만 있고 오래된 viewBox/canvas가 남아 PNG가 비정상적으로 김 | `exposed-workshop/docs/lessons/2026-06-19-readme-diagram-final-qa.md`, `bluetape4k-aws/docs/lessons/2026-05-30-readme-diagram-checklist-repair.md` | PNG의 aspect, content bounding-box occupancy, margin imbalance, blank output을 `diagram-visual-audit.py`로 검사 |
| SVG/PNG가 어긋나거나 README가 SVG/없는 파일을 가리킴 | `exposed-workshop/docs/lessons/2026-05-20-readme-diagram-image-validation.md`, `bluetape-go/docs/lessons/2026-06-19-readme-diagram-refresh.md` | asset directory의 SVG↔PNG pair, README local ref, PNG-only embed, Mermaid/Graphviz residue를 `diagram-asset-pair-audit.py`로 검사 |
| `legacySkipped`, `cards=0`, `paths=0`이 QA 통과처럼 보임 | `bluetape4k-workshop/docs/lessons/2026-06-30-diagram-qa-evidence-gate.md`, `2026-07-03-issue-385-diagram-validation-coverage.md` | `validated`, `documentedExceptions`, `exceptionSlugs`를 구분하고 zero/weak 결과는 targeted fallback 없이는 실패 |
| generator를 고치지 않고 결과 SVG만 고쳐 재생성 때 결함이 복귀함 | `bluetape4k-image/docs/lessons/2026-07-03-image-repo-review-diagram-checklist.md`, `bluetape4k-projects/docs/lessons/2026-06-19-sequence-diagram-rendering-qa.md` | generator/template의 stale selector, shared `.label`, unused marker, marker orientation을 출력 전 검사 |
| lane title/note 영역으로 connector가 들어가거나 card와 겹침 | `clinic-appointment/docs/lessons/2026-06-20-diagram-feedback-resolution.md`, `exposed-workshop/docs/lessons/2026-06-29-chapter13-diagram-connector-qa.md` | lane title/subtitle/note/footer를 no-flow zone으로 예약하고 port/경계를 먼저 이동 |

## 적용한 제작 계약

- `SKILL.md`의 실행 순서에 generated source 점검, PNG geometry audit, asset
  pair/exposure audit를 추가했다.
- `references/common.md`에 arrowhead 방향, no-flow zone, canvas/투명도,
  coverage 상태(검증/명시적 예외/skip 분리)를 추가했다.
- `references/chart.md`와 `references/sequence.md`에 generator selector와
  unused marker 점검을 추가했다.
- `diagram-arrowhead-audit.py`가 marker orientation/local tip/path tangent를
  확인하고, 잘못된 triangle 방향과 `marker-start`의 `auto` 사용을 실패시킨다.
- `diagram-visual-audit.py`는 외부 이미지 라이브러리 없이 PNG를 해석해
  dimension/aspect/occupancy/margins/alpha를 보고한다.
- `diagram-asset-pair-audit.py`는 SVG/PNG pair와 README 노출을 확인한다.

## 검증

managed source에서 의도적으로 실패하는 RED fixture를 먼저 확인한 뒤, 다음
회귀 테스트를 통과시켰다.

```text
python3 -m unittest discover \
  -s /Users/debop/.local/share/chezmoi/private_dot_codex/private_skills/bluetape-diagram/tests \
  -p 'test_*.py'
47 tests, OK
```

새 negative fixture는 역방향 marker geometry, missing orientation, 잘못된
`marker-start`, stale tall canvas, 투명 PNG의 opaque gate, missing pair,
README SVG/Mermaid residue, unreferenced canonical PNG을 각각 실패시킨다.

## 남은 범위

이번 변경에서 기존 workspace diagram을 재렌더링하거나 강제로 metadata를
일괄 삽입하지 않았다. 따라서 기존 자산은 다음 touched-asset 작업에서
`data-tip-direction`/`orient`, SVG↔PNG pair, README exposure, PNG canvas를
순서대로 보강해야 한다. 새 규칙이 기존 자산 전체에 적용됐다고 주장하지
않으며, one-asset loop와 full-size PNG 검사를 유지한다.
