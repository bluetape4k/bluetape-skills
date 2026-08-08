# Common Diagram Contract

Use this reference for every bluetape4k diagram, chart, README visual, docs
visual, blog image, or site visual.

## Source and Scope

- Read the target README or page section before changing the diagram.
- Read the source code/configuration that implements the behavior being drawn.
- The diagram must answer a source-backed reader question.
- Remove or skip an asset that cannot be tied to source-backed behavior.
- Keep source-backed helper/provider concepts even when routing is hard; solve
  layout instead of deleting relationships.
- Do not use existing rendered PNG/SVG assets as the source model unless the
  user explicitly asks for migration or visual parity.
- If the user reports a defect, scan the related diagram set for the same
  marker, connector, label, icon, lane, endpoint, or style pattern.
- For repeated-review assets, benchmark comparisons, branch/loop-heavy views,
  or long technical identifiers, create and validate a semantic ledger before
  drawing. The ledger is an input contract, not a replacement for rendered
  geometry or PNG inspection.
- When an SVG/PNG is generated, inspect the generator/template source in the
  same change. Audit selectors and marker definitions for stale palettes,
  shared shape/text classes, unused markers, and orientation defaults before
  regenerating any asset. A clean output cannot compensate for a stale source.

## One-Asset Loop

Choose the pipeline by the information model, not by a universal preference.

| Reader need / asset shape | Canonical source pipeline |
| --- | --- |
| precise static structure, topology, time order, or relationship contract | SVG -> PNG |
| architecture/component, class/UML, ERD, sequence, static state/flow, connector-heavy technical diagram | SVG -> PNG |
| coordinate-driven chart where axes, points, paths, or interpolation carry meaning | SVG -> PNG |
| DOM-native chart/dashboard built from repeated cards, grid/flex, tables, bars, scores, or filters | HTML/CSS/JavaScript -> PNG |
| reader-explorable business workflow, journey, decision/process map, or operational flow with branch/state comparison and explanatory panels | HTML/CSS/JavaScript -> PNG |
| small static business flow whose connector topology is the whole message | SVG -> PNG |

Dark/light support or localization alone does not justify HTML. Use HTML when
the reader benefits from multiple views, filters, branch/state exploration, or
narrative composition. Reject a single universal pipeline: structural diagrams
remain SVG, while eligible charts and business workflows follow `chart.md` or
`workflow.md`.

1. Select and record one approved source pipeline.
2. For the high-change cases above, run `diagram-semantic-audit.py` against the
   source ledger and record its counts/budget before drawing.
3. Edit one source asset.
4. Validate the source: XML for SVG, or HTML plus its data contract for an
   eligible DOM-native chart/workflow.
5. Render the matching PNG with CairoSVG or the kind-specific deterministic
   Chromium capture contract.
6. Inspect the full-size PNG.
7. Run type-specific audits and fallback invariants.
8. Record evidence and any repair receipt before moving to the next asset.

Batch scripts and contact sheets are allowed only as pattern scans. They do not
replace one-by-one full-size PNG inspection.

## Fonts, Theme, and Text

- For English diagrams, use `Architects Daughter` for titles and headings, and
  `Comic Mono` for body labels, annotations, and technical identifiers.
- For Korean diagrams, use `goorm Sans` for Korean reader-facing text and
  `goorm Sans Code` for code, commands, and technical identifiers. When one
  text node mixes code and Hangul, keep `goorm Sans` as the fallback after
  `goorm Sans Code`.
- For bilingual blog posts, create separate Korean and English SVG/PNG assets
  whenever a diagram contains reader-facing text. Do not reuse a localized
  raster across locales; keep technical identifiers unchanged in both assets.
- For bilingual HTML companions, keep English and Korean in separate,
  source-equivalent files and link them bidirectionally. Follow the repository
  naming contract; new bluetape4k companions default to English `*.html` and
  Korean `*.ko.html`.
- When HTML is the canonical visual companion, support `auto`, `light`, and
  `dark` themes. Export theme-specific PNG fallbacks from the HTML instead of
  maintaining hand-edited duplicate raster content.
- In light themes, make cards visibly distinct from the canvas.
- Final footer/caption text must be reader-facing only; do not put evidence,
  generation notes, or validation logs inside the art.
- Resize cards for the longest meaningful text instead of shrinking text until
  it is hard to read.
- Split long framework, bean, and class names into readable title/subtitle
  lines.
- Reject clipped text, text touching card/frame boundaries, and text crowded
  against icons.
- Peer cards must use a consistent text alignment model, including icon cards.
- Automated label bounds are screening evidence; full-size PNG inspection still
  decides whether typography and overall density are readable.
- In SVG, do not put a thick white stroke and `paint-order: stroke` on one text node;
  CairoSVG can paint the stroke over the fill and erase the glyph. Use a label
  capsule or separate stroke-only underlay plus fill-only foreground text.
- Mark real source snippets and pseudocode with `data-code-snippet="<language>"`
  and use semantic token spans for keywords, types, calls, strings, numbers,
  comments, and operators. UML members, participant names, and prose remain
  ordinary monospace text unless they are intentionally presented as code.

## Icons

- Use shared icons from `${BLUETAPE_WIKI_ROOT}/docs/icons` when a card
  represents a real server, service, managed service, queue/topic, database,
  cache, or external infrastructure component.
- Use AWS official Architecture Icons for AWS service cards.
- Use catalog Redis, Kafka, database, queue, and similar icons directly for
  non-AWS infrastructure cards.
- Do not invent technology logos. If no confirmed official/catalog icon exists,
  keep the card text-only or use a clearly generic infrastructure icon.
- Standard icons replace legacy art; remove old cylinders, wrappers, sprites,
  hand-drawn stacks, duplicate `<use>` references, and unused icon `<defs>`.
- After icon changes, audit the related SVG set for duplicate standard-plus-
  legacy icon patterns, not only the named file.

## Arrowheads and Markers

- PNG rendering is authoritative for arrowhead color, size, dash inheritance,
  and direction.
- Prefer fixed `markerUnits="userSpaceOnUse"` for README-scale arrows.
- Do not rely on `context-stroke` unless a marker audit and PNG zoom check prove
  correct output.
- Use explicit per-color markers when paths have semantic colors.
- Same-role arrowheads must read as the same size in PNG.
- Standard sizes:
  - UML hollow inheritance/generalization: `18x16`
  - sequence messages: `16x16`
  - primary flow/progression/query/write/read movement: `14x14`
  - secondary/static relationships: `10x10`
- Make the role machine-checkable on every referenced `<marker>` with
  `data-role="uml-hollow|sequence|primary|secondary"`, matching numeric
  `markerWidth`/`markerHeight`, `markerUnits="userSpaceOnUse"`,
  `orient="auto"` (or `auto-start-reverse` for a `marker-start`), and
  `data-tip-direction="positive-x"`. A direct
  polygon/polyline head must declare `data-arrowhead="true"`, the same
  `data-role`, `data-size="WxH"`, `data-tip-direction="positive-x"`, and
  `data-solid-head="true"`.
- Treat the marker's local +x axis as the forward axis. `marker-end` must use
  the final non-zero path tangent, while `marker-start` must use
  `auto-start-reverse`; a numeric or missing `orient`, a reversed triangle,
  or a zero terminal tangent is a direction failure. `diagram-arrowhead-audit.py`
  must report the direction-check count, not only marker size.
- Dashed relationship lines may be dashed, but their arrowheads must render
  solid. If CairoSVG renders marker-based heads dashed, replace them with direct
  `polygon` or `polyline` heads with explicit no-dash attributes.
- Run `diagram-arrowhead-audit.py` before PNG inspection. It rejects untyped or
  mis-sized referenced markers, reversed marker geometry/orientation, dashed
  marker children/direct heads, and a marker-start/marker-end terminal segment
  shorter than the arrowhead footprint plus the clearance margin. This is a
  coordinate guard, not a replacement for full-size PNG inspection.
- When one marker mismatch is found, scan the whole related diagram set for the
  same pattern.

## Connector Geometry

- Prefer horizontal, vertical, and rounded orthogonal connectors.
- Avoid diagonal card-to-card segments unless the style/source reason is
  explicitly documented.
- Start and end segments must leave/enter card, lane, or layer boundaries
  perpendicular to the touched edge.
- Endpoints must stay away from card corners by at least `max(8px, rx / 2)`.
- Do not route lines through card interiors, along card borders, or parallel and
  immediately adjacent to card edges.
- Bent connectors need rounded corners at every turn, normally `Q` segments
  plus round line caps/joins.
- A `Q` command is not proof: if the PNG still shows a hard corner, move bend
  coordinates, change ports, or open corridor space.
- Account for arrowhead size before each target bend. Leave enough terminal
  segment for the arrowhead before it reaches the card edge.
- Separate incoming and outgoing ports for cards with multiple relationships.
- Do not let different relationships share a collinear connector segment or
  visual corridor; assign distinct ports and routes.
- Prefer the shortest semantically correct port pair; use top/bottom or
  same-side routes when they remove crossings or detours.
- Move labels away from every unrelated line, card, arrowhead, lane title, and
  region border.
- Keep relationship labels auditable: use an explicit label background `<rect>`
  or explicit text `x`/`y` coordinates. Recognized labels with unbounded or
  malformed transform geometry fail closed.
- Classify decoration paths by complete class tokens (for example,
  `icon-line-*` must not become a route merely because it contains the token
  `line`). Preserve `data-source`/`data-target` on connectors and make path
  parsers consume every control/end point in `Q`, `C`, and transformed fixtures;
  parser uncertainty is a documented exception, not a passing zero count.

## Lane, Layer, and Whitespace

- Lane/title labels must remain visually clear from cards, icons, connectors,
  and shadows.
- When excess lane bottom whitespace is reported, compute the gap from lane
  bottom to content bottom, trim lane/frame/canvas/footer together, rerender,
  and report before/after values.
- If a lane is too cramped, increase canvas/viewBox dimensions rather than
  crowding connectors or shrinking text.
- When changing lane or card dimensions, move dependent connector ports, paths,
  labels, notes, footers, frames, and viewBox together.
- Reserve a no-flow zone around lane titles, subtitles, notes, and footer
  labels. Connectors must never enter or cross that zone; if a route needs the
  space, move the port/lane boundary or split the lane before adding a detour.

## PNG Canvas and Asset Exposure

- The rendered PNG is the acceptance artifact. Run
  `diagram-visual-audit.py` on every final PNG and record width/height, aspect,
  content bounding-box occupancy, ink occupancy, margins, margin imbalance, and
  `alpha_min`. The default screening thresholds are aspect `<= 4:1`,
  bounding-box occupancy `>= 0.22`, and margin imbalance `<= 0.35`; a relaxed
  threshold requires a named, source-backed exception.
- Decide explicitly whether the README PNG is opaque or intentionally
  transparent. A transparent background is allowed only when the visual note
  and full-size inspection prove that it preserves the intended canvas; use
  `--require-opaque` for README exports that must be self-contained.
- For every README-facing asset directory, run
  `diagram-asset-pair-audit.py`. Require a one-to-one SVG/PNG pair, resolve
  local Markdown/HTML image links, reject SVG embeds, and reject Mermaid or
  Graphviz residue. `--require-all-referenced` is required when the directory
  is the canonical README asset set.
- Mechanical validators must distinguish `validated`,
  `documentedExceptions`, and `exceptionSlugs`. `legacySkipped`, `targets=0`,
  `cards=0`, or `paths=0` is incomplete evidence until a targeted fallback
  invariant proves the actual entities.

## Required Local Commands

Use available repo-local wrappers when present. The commands below are the SVG
path and remain required for connector-heavy SVGs. An eligible DOM-native chart
or business workflow uses the separate validation and capture commands required
by its kind reference.

```bash
xmllint --noout <diagram>.svg
cairosvg <diagram>.svg -o <diagram>.png -s 2
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-semantic-audit.py" --repo-root <repository-root> --json <diagram>.semantic.json
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-connector-audit.py" <diagram>.svg
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-arrowhead-audit.py" <diagram>.svg
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-visual-audit.py" --require-opaque <diagram>.png
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-asset-pair-audit.py" --asset-dir <asset-dir> --readme <README.md> --require-all-referenced
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-geometry-audit.py" --fail-diagonal <diagram>.svg
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-endpoint-audit.py" <diagram>.svg
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-mixed-corner-audit.py" <diagram>.svg
python3 "${CODEX_HOME:-$HOME/.codex}/skills/bluetape-diagram/scripts/diagram-svg-text-normalize.py" <diagram>.svg
git diff --check -- <diagram>.svg <diagram>.png
```

These scripts are executable helpers, not rule references; do not load their
source unless diagnosing an audit. If a generic audit reports weak counts for a
visible diagram, add a fallback invariant that counts the actual entities,
relationships, labels, markers, or ports that prove the claim.

## Review Page Gate

When a local diagram review page exists, verify that it links the touched PNG
and SVG to the current worktree and canonical output path before asking the user
to review.

## Blocking Common Checklist

- [ ] **DIA-COM-01 — Verify source and related-set scope**
  - **Action:** Read target prose and implementing source, define the reader question, and scan related assets for the reported pattern.
  - **Evidence:** Exact paths, source-backed concepts, and scan results.
  - **Failure:** Do not model from an old rendered asset or delete hard-to-route source relationships.
- [ ] **DIA-COM-02 — Preserve readable text and theme**
  - **Action:** Apply approved fonts/theme, remove CairoSVG text hazards on the SVG path, highlight explicit source snippets, resize for meaningful text, keep peer alignment, and exclude evidence notes from the art.
  - **Evidence:** SVG `text_hazards=0` when applicable, `code_without_highlight=0`, and full-size PNG text/font/alignment inspection.
  - **Failure:** Missing text, unhighlighted explicit code, clipping, crowding, inconsistent peers, or unreadable shrinkage blocks PASS.
- [ ] **DIA-COM-03 — Use verified infrastructure icons**
  - **Action:** Use catalog/official icons, remove legacy duplicates/defs, and scan related SVGs after icon changes.
  - **Evidence:** Icon source paths and duplicate-pattern scan, or concrete text-only N/A.
  - **Failure:** Reject invented logos or standard-plus-legacy duplicates.
- [ ] **DIA-COM-04 — Verify markers in PNG**
  - **Action:** Use fixed per-color markers or direct heads, declare the role/size/orientation/tip-axis contract, run the arrowhead audit, and verify solid color/size/direction in PNG.
  - **Evidence:** Marker role/size/orient/tip-axis/terminal/direction audit counts and zoomed/full-size PNG notes.
  - **Failure:** Dashed, black, mismatched, check-like, or inconsistent heads require repair and related-set scan.
- [ ] **DIA-COM-05 — Verify connector endpoints and routes**
  - **Action:** Enforce perpendicular boundary attachment, corner clearance, no card/border intrusion, separated ports, no shared connector segments, label clearance, and shortest semantic routes.
  - **Evidence:** Endpoint/geometry/connector audit results including relationship names and label/shared-segment counts, plus visual inspection.
  - **Failure:** Diagonal, floating, corner-adjacent, crossing, card-hugging, shared-corridor, or label-colliding routes block PASS.
- [ ] **DIA-COM-06 — Verify every bent corner**
  - **Action:** Use rounded orthogonal geometry at every turn with sufficient pre/post bend and arrowhead clearance.
  - **Evidence:** Mixed-corner audit and PNG corner inspection.
  - **Failure:** A lone Q or remaining sharp H/V/L turn is not proof; move bends/ports/corridors.
- [ ] **DIA-COM-07 — Synchronize lanes, canvas, and whitespace**
  - **Action:** Move dependent ports/paths/labels/footer/frame/viewBox with lane/card changes, reserve no-flow title/note zones, and measure requested whitespace trims.
  - **Evidence:** Before/after dimensions/gaps, no-flow-zone result, and full-size PNG inspection.
  - **Failure:** Excess whitespace, cramped lanes, title/note crossings, or stale dependent coordinates blocks PASS.
- [ ] **DIA-COM-08 — Run required local commands**
  - **Action:** Run the selected pipeline's source validation, render, diff, arrowhead-direction, PNG-geometry, and asset-pair checks; add XML, CairoSVG, connector, geometry, endpoint, and mixed-corner checks when triggered.
  - **Evidence:** Exact selected-pipeline commands; for connector-heavy SVGs also include nonzero meaningful entity counts, `shared_segments=0`, `label_cards=0`, `label_labels=0`, `label_connectors=0`, `validated=<n>`, `documentedExceptions=<n>`, and failures=0.
  - **Failure:** WEAK/UNAVAILABLE/zero counts or `legacySkipped` require targeted fallback proof; missing output is FAIL.
- [ ] **DIA-COM-09 — Verify review exposure**
  - **Action:** When a review page exists, prove it links current worktree canonical SVG/PNG outputs.
  - **Evidence:** Link targets and rendered review-page result, or concrete absence N/A.
  - **Failure:** Do not ask for review through stale or missing assets.
- [ ] **DIA-COM-10 — Verify PNG canvas geometry**
  - **Action:** Run `diagram-visual-audit.py` on every final PNG, inspect full size, and record any explicit aspect/occupancy/transparency exception.
  - **Evidence:** Dimensions, aspect, bbox/ink occupancy, margins, alpha decision, and failures=0.
  - **Failure:** Blank/background-only output, stale tall/wide canvas, severe margin imbalance, or undocumented transparency blocks PASS.
- [ ] **DIA-COM-11 — Verify source pair and README exposure**
  - **Action:** Run `diagram-asset-pair-audit.py` on the canonical asset directory and target README(s), with `--require-all-referenced` when the directory is the README set.
  - **Evidence:** SVG/PNG pair count, README PNG refs, missing refs, SVG refs, duplicate refs, Mermaid/Graphviz residue, and failures=0.
  - **Failure:** Missing pair, missing/SVG README link, residue, or unreferenced canonical asset blocks PASS.
