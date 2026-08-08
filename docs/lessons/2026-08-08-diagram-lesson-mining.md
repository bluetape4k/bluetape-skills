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

초기 규칙 보강 단계에서는 기존 diagram을 재렌더링하지 않았지만, 후속
자산 이행에서 공개 bundle의 현재 3개 자산을 실제로 보강했다.

## 후속 자산 이행 (2026-08-08)

사용자 요청에 따라 다음 자산을 one-asset loop로 재검증하고, SVG를
CairoSVG 2.9.0으로 다시 PNG로 렌더링했다.

- `bluetape-skills-public-bundle-boundary-01.svg`: primary marker에
  `data-role`과 `data-tip-direction="positive-x"`를 추가했다.
- `bluetape-workflow-7-tier-review-01.svg`: blue/red/green marker를 모두
  `14x14` primary head로 통일하고, marker를 group에서 실제 종단 path로
  옮겼다. fan-out/fan-in 공통 선분은 무화살표 bus/trunk로 분리해
  `shared_segments=0`으로 만들고, 짧은 마지막 수직 구간을 15px 이상으로
  확보했다.
- `bluetape-workflow-type-router-01.svg`: primary marker metadata를 추가하고
  7개 lane fan-out을 trunk/bus/종단 branch로 분리했다.
- branch/loop 자산의 재현 가능한 source model은
  `docs/images/*.semantic.json` ledger로 보존했다.

최종 감사 결과는 세 SVG 모두 XML/text/arrowhead/connector/geometry/endpoint/
mixed-corner 실패 0, marker 방향 검사 `1/1`, `16/16`, `8/8`, PNG는 각각
`2400x1440`, `3200x1800`, `2400x1440`의 opaque canvas와 균등 46px 여백,
README pair 감사는 `svgs=3`, `pngs=3`, `pairs=3`, `png_refs=3`,
`svg_refs=0`이다. 각 PNG는 full-size로 확인했으며, 새 규칙은 이 3개
자산에 실제 적용된 상태다.

새 diagram을 추가할 때도 generator/source metadata, one-asset loop,
semantic ledger(반복 review·branch·긴 식별자), SVG↔PNG pair, full-size PNG
검사를 생략하지 않는다.
