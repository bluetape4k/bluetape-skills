# Architecture Diagram Rules

Use with `common.md` for architecture, component, ownership, dependency, and
flow-style architecture diagrams.

## Source Model

- Architecture diagrams are static responsibility, ownership, component, or
  dependency views.
- If the visual mainly shows ordered calls, branches, retries, lifecycle, or
  request/response flow, use the sequence reference instead.
- Useful architecture diagrams name concrete runtime responsibilities, backend
  primitives, telemetry paths, ownership boundaries, and reader-relevant
  dependency directions.

## Style Baseline

- Start from a current bluetape4k best-practices architecture family or a
  recent approved repo-local architecture reference.
- Record the reference PNG path in the evidence ledger.
- Use a restrained, readable palette. If a chapter/repo has an approved family,
  match that family rather than inventing a new style.
- Cards with solid/dashed or multi-color connectors need an in-image legend or
  adjacent README explanation.

## Layout

- Choose orientation from the reader question:
  - vertical stacks for true top-down lifecycles, pipelines, or dependency tiers
  - horizontal layers/columns for responsibility maps, receiver/API groupings,
    ownership boundaries, and input-helper-output maps
- Do not preserve a vertical lane if it creates generic labels or long detours.
- Prefer moving cards, widening the canvas, or changing ports over adding
  complex connector doglegs.
- Keep right/left/top/bottom margins even; if space runs out, enlarge the
  image or reduce card width consistently.
- Long DB or external-target cards may be stretched so multiple inbound
  connectors enter as clean horizontal lines.

## Connectors

- Architecture links should use clear orthogonal routes with rounded corners
  unless a straight line is possible.
- Do not route operation links along lane borders or through lane titles.
- For lane/layer-to-lane/layer relationships, connect boundary to boundary;
  for concrete operations, connect concrete card to concrete card.
- Avoid card-adjacent connector corridors. Leave visible standoff space.
- When a connector bends near an arrowhead, move the bend to account for the
  rendered arrowhead size instead of shrinking the arrowhead first.

## Visual Failures

Reject the PNG when:

- the diagram reads as a sequence/flowchart instead of static architecture
- connector colors or dashed styles are unexplained
- card text alignment is inconsistent among peer cards
- DB/service icons are wrapped inside legacy cylinders or placeholder art
- lines cross avoidably or pass too close to cards
- lane bottom whitespace remains excessive after requested trimming

## Blocking Architecture Checklist

- [ ] **DIA-ARC-01 — Confirm static architecture semantics**
  - **Action:** Verify the asset answers a responsibility/ownership/component/dependency question rather than an ordered call sequence.
  - **Evidence:** Source model and reader question.
  - **Failure:** Route time-ordered behavior to the sequence reference.
- [ ] **DIA-ARC-02 — Match an approved visual family**
  - **Action:** Open a current best-practices or approved repo-local reference and preserve palette/legend conventions.
  - **Evidence:** Reference PNG path and style comparison.
  - **Failure:** Do not invent unexplained colors, dashes, or legacy art.
- [ ] **DIA-ARC-03 — Choose layout from the reader question**
  - **Action:** Select vertical or horizontal organization, balance margins, and move/resize cards before adding complex detours.
  - **Evidence:** Layout rationale and whitespace/margin inspection.
  - **Failure:** Reject generic lanes, long doglegs, crowding, or excessive bottom space.
- [ ] **DIA-ARC-04 — Verify architectural connectors**
  - **Action:** Route boundary or concrete-operation links appropriately with rounded orthogonal paths, standoff, and arrowhead clearance.
  - **Evidence:** Common audit results plus architecture PNG inspection.
  - **Failure:** Lines on borders/titles, avoidable crossings, or card-adjacent corridors block PASS.
