# ERD Rules

Use with `common.md` for entity relationship, table, schema, ownership, and
persistence-contract diagrams.

## Source Model

- ERDs show the domain relationship the README reader needs, not incidental
  table metadata.
- Omit ERDs that cannot be tied to real schema, ownership, or persistence
  contracts.
- Read actual table/entity/source definitions before changing relationships.

## Tables and Placement

- Position related tables so connectors are short and readable.
- Prefer placing directly related tables on the same row when that removes
  unnecessary bends.
- Increase vertical spacing when cardinality labels or connectors crowd table
  borders.
- Move table bodies rather than adding long detours.
- Trim unused bottom whitespace after table positions are final.

## Cardinality and Labels

- Cardinality labels such as `1`, `N`, and `1:N` are small text near the
  relevant connector endpoints.
- Do not put cardinality labels in large boxes, badges, or circles unless the
  established local ERD style explicitly uses them.
- Labels must not overlap arrowheads, lines, table borders, FK labels, owner
  labels, or relationship names.
- Place endpoint labels close enough to the endpoint to identify the side, but
  offset far enough that the line remains visible.
- `FK`, `owner`, and relationship labels must not touch cardinality labels.

## Connectors

- Use orthogonal connectors where possible.
- Avoid crossings by moving tables before adding bends.
- If a connector must bend, use visible rounded corners and enough arrowhead
  clearance.
- Relationship endpoints must attach cleanly to table boundaries, not float in
  whitespace or stop inside the table.

## Evidence

When generic card audits cannot count custom ERD groups, add fallback invariant
counts:

- entity/table group count
- relationship connector count
- visible cardinality label count
- FK/owner/relationship label overlap result
- bottom whitespace before/after when trimming was requested

## Blocking ERD Checklist

- [ ] **DIA-ERD-01 — Ground entities and relationships**
  - **Action:** Read real schema/entity/source definitions and include only reader-relevant ownership/persistence contracts.
  - **Evidence:** Entity/table and relationship inventory with source anchors.
  - **Failure:** Omit ungrounded incidental metadata or the entire ERD when no real contract exists.
- [ ] **DIA-ERD-02 — Place tables for readable relationships**
  - **Action:** Keep related tables close, move bodies before adding bends, increase crowded spacing, and trim final whitespace.
  - **Evidence:** Layout/crossing review and before/after whitespace when requested.
  - **Failure:** Avoidable detours, crossings, border crowding, or unused space blocks PASS.
- [ ] **DIA-ERD-03 — Verify cardinality and labels**
  - **Action:** Place compact endpoint cardinalities and FK/owner/relationship labels without overlap.
  - **Evidence:** Visible label count and overlap inspection.
  - **Failure:** Large badges, ambiguous endpoints, or touching labels/lines/heads block PASS.
- [ ] **DIA-ERD-04 — Verify relationship connectors**
  - **Action:** Use orthogonal rounded routes with boundary-attached endpoints and arrowhead clearance.
  - **Evidence:** Connector/entity/cardinality fallback counts plus common audits.
  - **Failure:** Floating/inside-table endpoints or sharp/crossing routes block PASS.
