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

후속 full-size PNG 검토에서 버스와 분기를 분리한 것만으로는 충분하지 않다는
점도 확인했다. 분기 선분이 버스에서 바로 수직으로 꺾이면 소스에 Q가 없어도
감사 결과가 통과했지만, PNG에서는 정각 T 접점으로 보였다. 따라서 각 분기의
첫 꺾임을 같은 connector path 안의 Q로 유지하고, 버스는 구조선(`bus-line`)으로
분리했다. `diagram-mixed-corner-audit.py`도 이제 Q가 전혀 없는 H/V 꺾임을
실패시키며, 이 회귀 조건을 전용 테스트로 고정했다.

최종 감사 결과는 세 SVG 모두 XML/text/arrowhead/connector/geometry/endpoint/
mixed-corner 실패 0 (`q_bends=26`), marker 방향 검사 `1/1`, `16/16`, `8/8`, PNG는 각각
`2400x1440`, `3200x1800`, `2400x1440`의 opaque canvas와 균등 46px 여백,
README pair 감사는 `svgs=3`, `pngs=3`, `pairs=3`, `png_refs=3`,
`svg_refs=0`이다. 각 PNG는 full-size로 확인했으며, 새 규칙은 이 3개
자산에 실제 적용된 상태다.

새 diagram을 추가할 때도 generator/source metadata, one-asset loop,
semantic ledger(반복 review·branch·긴 식별자), SVG↔PNG pair, full-size PNG
검사를 생략하지 않는다.

## 화살촉 결함의 기준선/수정 후 증거 (2026-08-08)

두 대표 아키텍처 자산에서 같은 결함을 먼저 재현했다. 기존 감사는 CSS에만
`marker-end`가 선언된 커넥터를 사용하지 않은 것으로 오인해 `markers=4
used_markers=0`(graph), `markers=5 used_markers=0`(image)으로 보고했으며,
실제 PNG에서 graph 화살촉은 방향과 끝점이 불안정하고 image 주요 경로의
화살촉은 secondary 크기라 작았다.

수정 후 기준선과 같은 명령을 다시 실행한 결과는 다음과 같다.

| 자산 | arrowhead 감사 | connector/geometry | PNG |
|---|---|---|---|
| `bluetape4k-graph-architecture-01` | `markers=4 used_markers=4 direction_checks=12 terminal_checks=8` | `connectors=8 intrusions=0`, `geometry_failures=0` | `3160x1960`, opaque, 균등 58px 여백 |
| `bluetape4k-image-architecture-01` | `markers=5 used_markers=5 direction_checks=15 terminal_checks=11` | `connectors=11 intrusions=0`, `geometry_failures=0` | `3160x1960`, opaque, 균형 여백 |

이 증거를 재현하려면 marker 참조가 직접 속성이거나 감사기가 해석할 수 있는
CSS 규칙이어야 하며, `markers>0 used_markers=0`은 PASS가 아니라 실패로
처리해야 한다. 사용자 결함 보고에는 기준선과 수정 후 감사 줄을 함께 남기고,
전체 크기 PNG를 확인한다. 이 회귀 조건은 `bluetape-diagram`의 CSS marker
resolver와 테스트로 고정했으며, 공개 bundle 검증은 `145 passed, 1 skipped,
159 subtests`, diagram 전체 테스트는 `50 passed`이다.
