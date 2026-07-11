# Class Diagram Rules

Use with `common.md` for class, UML, repository/entity, inheritance, interface,
and dependency diagrams.

## Semantics

- Use standard UML meaning:
  - inheritance/generalization: solid line with hollow triangle
  - interface implementation: dashed or semantically marked line with hollow
    triangle only when the diagram intentionally distinguishes it
  - dependency/use: dashed line
  - creation or call flow: separate arrow style with a legend if non-obvious
- Do not remove source-backed inheritance or dependency lines because routing is
  hard. Reposition cards or enlarge the canvas.
- Prefer relationship-centered placement over layer/grid placement when layer
  rows create crossings.

## Layout

- Place related table/entity/repository/interface groups close enough that the
  relationship reads without long doglegs.
- Use vertical inheritance where possible.
- Put entrypoint/factory/controller cards aside from the main inheritance or
  repository relationship corridors when their create arrows add clutter.
- Avoid rigid grids when card text is much shorter than the card body.
- If connector density is high, increase image size first, freely reposition
  cards, then trim outer whitespace after routes are clean.
- Keep peer cards with similar content at similar widths unless text length
  requires a documented exception.

## Arrowheads and Dashed Lines

- Rendered PNG decides arrowhead validity.
- Dashed relationship shafts must not make hollow/open arrowheads dashed.
- If marker-based dashed heads render dashed, black, too small, or check-like,
  replace the marker head with direct solid geometry.
- Re-check both SVG and PNG because CairoSVG can change marker appearance.
- Same-role UML arrowheads must be similar in size; oversized inheritance heads
  fail even when the SVG marker definition is valid.

## Connectors

- Use rounded orthogonal bends for every non-straight connector.
- Reject paths that mix one `Q` bend with remaining sharp `L/H/V` corners.
- Bend coordinates must leave room for the arrowhead and visible corner radius.
- Prefer top-to-bottom, bottom-to-top, bottom-to-center, or same-side routing
  when it removes crossings.
- Distinct relationships from the same card need distinct source ports and
  corridors.
- Labels must not sit on class borders, connectors, arrowheads, or other labels.

## Evidence

In addition to common evidence, record:

- count of inheritance/generalization relationships
- count of dashed dependency/use relationships
- dashed-arrowhead PNG inspection result
- rounded-corner audit result for every bent relationship cluster

## Blocking Class Checklist

- [ ] **DIA-CLS-01 — Preserve UML semantics**
  - **Action:** Map every source relationship to standard inheritance, implementation, dependency, creation, or call notation with legends when non-obvious.
  - **Evidence:** Relationship inventory and source anchors.
  - **Failure:** Never delete a source-backed relationship to simplify routing.
- [ ] **DIA-CLS-02 — Place by relationship**
  - **Action:** Group related types, prefer vertical inheritance, separate cluttering entrypoints, and enlarge/reposition before rigid grids.
  - **Evidence:** Layout rationale and crossing/whitespace review.
  - **Failure:** Long doglegs, empty card bodies, or avoidable crossings block PASS.
- [ ] **DIA-CLS-03 — Verify arrowheads and dashed roles**
  - **Action:** Check hollow inheritance, dashed shafts with solid heads, role-consistent sizes, and CairoSVG output.
  - **Evidence:** Inheritance/dependency counts and dashed-head PNG inspection.
  - **Failure:** Dashed/black/small/oversized/check-like heads require direct geometry or marker repair.
- [ ] **DIA-CLS-04 — Verify connectors and labels**
  - **Action:** Use rounded turns, distinct ports/corridors, clean endpoints, and labels clear of borders/lines/heads/labels.
  - **Evidence:** Mixed-corner/common audits and cluster-level PNG notes.
  - **Failure:** Any sharp mixed turn, overlap, or relationship collision blocks PASS.
