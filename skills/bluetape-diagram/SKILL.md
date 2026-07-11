---
name: bluetape-diagram
description: Use when bluetape4k work creates or updates technical diagrams, charts, README visuals, docs visuals, blog images, or site visual assets.
---

# bluetape4k Diagram Generation

This skill is the lightweight entrypoint. Do not load every rule by default.
Load the common contract first, then only the diagram-kind references that match
the current asset.

## Reference Routing

Always read:

- `references/common.md`

Then read only the matching kind files:

| Asset shape | Required reference |
| --- | --- |
| architecture, component, flow-style architecture | `references/architecture.md` |
| class, UML, repository/entity relationship class view | `references/class.md` |
| ERD, schema, table relationship view | `references/erd.md` |
| sequence, request/response, retry, branch, lifecycle, time flow | `references/sequence.md` |
| chart, benchmark, README metric visual | `references/chart.md` |

If a user-reported defect is about connectors, markers, arrowheads, labels,
icons, lane whitespace, rendered PNG parity, or review pages, keep
`references/common.md` open while editing.

## Execution Contract

1. Read the target README/page and source-backed behavior before drawing.
2. Work one asset at a time: edit SVG, render PNG, inspect PNG, then continue.
3. Treat PNG output as authoritative. SVG-only success never closes the task.
4. Convert every user-reported visual defect into a concrete geometry/style
   invariant and record the evidence.
5. Use the installed generators only as helpers:
   - `$fireworks-tech-graph` for diagrams/charts by default.
   - `$architecture-diagram-generator` for system architecture diagrams.
6. Do not use Graphviz for bluetape4k README diagrams.

## Non-Negotiable Gates

- Render with CairoSVG CLI:
  `cairosvg <diagram>.svg -o <diagram>.png -s 2`
- Open every touched or high-risk PNG at full size after the final coordinate
  change.
- Connector-heavy diagrams must have XML parse, marker/color, endpoint,
  perpendicular attachment, geometry, crossing/card-intrusion, mixed-corner,
  and full-size PNG evidence.
- Audit rows marked `WEAK`, `UNAVAILABLE`, `connectors=0`, `cards=0`,
  `paths=0`, or missing command output are not PASS evidence unless a targeted
  fallback invariant proves the same claim.
- Same-role arrowheads must render with consistent size/color in PNG:
  UML hollow inheritance `18x16`, sequence message `16x16`, primary
  flow/progression `14x14`, secondary/static relationship `10x10`.
- Bent connectors use rounded orthogonal corners with enough pre/post bend
  clearance. A `Q` command is not enough if the PNG still looks sharp.
- If full-size PNG inspection contradicts a script result, the PNG wins.

## Evidence Ledger

## Mandatory Diagram Checklist

Apply `bluetape-workflow/references/checklist-contract.md`. Complete the
common checklist and every selected kind checklist for each asset separately.

- [ ] **DIA-01 — Pin asset scope and source model**
  - **Action:** Record the canonical SVG/PNG paths, target README/page, implementing source/config, reader question, related-set scan, and diagram kind.
  - **Evidence:** Source/asset ledger and trigger-to-reference map.
  - **Failure:** Remove or defer assets without a source-backed reader purpose.
- [ ] **DIA-02 — Load common and kind rules**
  - **Action:** Read `common.md` and only the matching architecture/class/ERD/sequence/chart references; keep common open for user-reported geometry/style defects.
  - **Evidence:** Exact loaded reference list and applicable conditional rules.
  - **Failure:** Do not edit from generic diagram conventions.
- [ ] **DIA-03 — Complete one SVG edit**
  - **Action:** Edit exactly one asset, preserving source-backed concepts and converting reported defects into explicit invariants.
  - **Evidence:** Scoped SVG diff and invariant list.
  - **Failure:** Stop batch progression until this asset completes the full loop.
- [ ] **DIA-04 — Parse and render the authoritative PNG**
  - **Action:** Validate XML and render with the required CairoSVG CLI at scale 2.
  - **Evidence:** Successful commands and PNG dimensions/path.
  - **Failure:** SVG-only or alternate-renderer success does not advance the asset.
- [ ] **DIA-05 — Run common and type-specific audits**
  - **Action:** Run connector/geometry/endpoint/mixed-corner and kind-specific audits as triggered, adding targeted fallback invariants for weak generic counts.
  - **Evidence:** Counts and failures=0 with no WEAK/UNAVAILABLE/zero-count ambiguity.
  - **Failure:** Repair the asset or prove the same claim with a concrete fallback before visual review.
- [ ] **DIA-06 — Inspect the full-size PNG**
  - **Action:** Open the final PNG after the last coordinate change and inspect labels, endpoints, arrowheads, corners, crossings, card intrusion, icons, spacing, fonts, and whitespace.
  - **Evidence:** Full-size PNG path and observed pass/fail notes.
  - **Failure:** PNG contradiction overrides scripts; return to DIA-03.
- [ ] **DIA-07 — Verify exposure and diff hygiene**
  - **Action:** Check canonical embeds/review-page links, related asset parity, and `git diff --check` for SVG/PNG/page changes.
  - **Evidence:** Link/embed results, canonical paths, and clean diff check.
  - **Failure:** Broken exposure, stale paths, or unrelated artifacts blocks completion.
- [ ] **DIA-08 — Render the evidence ledger**
  - **Action:** Report every asset and checklist row with commands, counts, dimensions, inspection notes, reference paths, and gaps.
  - **Evidence:** X=Y, Blocked=0 for each asset with falsifiable values rather than “checklist passed”.
  - **Failure:** Do not claim visual completion; expose the unchecked row and next coordinate/style repair.

Every completion report or PR body must include concrete evidence rows:

| Gate | Evidence |
| --- | --- |
| Scope | asset path and related-set scan result |
| Source | README/source files read or documented exception |
| XML | `xmllint --noout ...` result |
| Render | CairoSVG command and PNG dimensions |
| Kind rules | relevant reference files loaded |
| Connector audits | counts such as `connectors`, `cards`, `q_bends`, `failures=0` |
| Type-specific audit | sequence/class/ERD/architecture/chart invariant result |
| Visual inspection | full-size PNG path and observed pass/fail notes |
| Review exposure | local review page link check when a review page exists |
| Diff hygiene | `git diff --check` result |

Do not write "checklist passed" unless the ledger contains the values that make
the claim falsifiable.

## Output

Produce the requested SVG/PNG/chart assets in the target repository's canonical
path. Keep image text concise, source-relevant, and reader-facing only.
