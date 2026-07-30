# Chart Rules

Use with `common.md` for benchmark, metric, module summary, README, docs, blog,
or site charts.

## Source and Form

- Consult current bluetape4k wiki best-practices material before choosing chart
  form, scale, labels, and layout.
- Chart data must come from source-backed benchmark, README, build, or module
  evidence.
- The chart must answer a reader question that prose or a table does not answer
  as quickly.

## Render Pipeline Selection

SVG -> PNG is the default. HTML/CSS -> PNG is an opt-in exception only for a
DOM-native chart whose geometry is expressed directly by normal document
layout.

| Use HTML/CSS -> PNG when | Keep SVG -> PNG when |
| --- | --- |
| simple bar, progress, scorecard, comparison panel, heatmap table, or repeated benchmark card | line, area, scatter, radar, multi-axis, curve, or coordinate-precise plot |
| values map directly to flex/grid layout, percentages, widths, heights, colors, or repeated DOM cards | paths, points, axes, ticks, interpolation, or exact plot coordinates drive meaning |
| the chart has no semantic connectors, arrowheads, routed edges, or diagram topology | architecture, class/UML, ERD, sequence, static technical flow, topology, or connector-heavy content |

When any condition is ambiguous, use SVG. Do not replace an SVG technical
diagram with HTML/CSS merely because browser capture is available.
Reader-explorable business workflows are governed by `workflow.md`; do not
reclassify them as charts to bypass the workflow eligibility gate.

HTML/CSS chart source rules:

- Keep one machine-readable data source such as `<chart>.data.json`.
- Generate visible values, labels, order, and CSS dimensions from that source.
  Do not hand-copy a value into both markup text and a CSS width/height.
- Use DOM layout only; do not hide a coordinate-driven SVG or canvas renderer
  inside the HTML exception.
- Keep `<chart>.html` and optional companion CSS as source artifacts. README and
  Markdown pages embed only `<chart>.png`.
- Do not add a browser or chart dependency when an existing repository capture
  runner or installed Chromium can render the asset.

## Deterministic HTML Capture

For every eligible HTML/CSS chart:

- pin and record the Chromium executable/version, viewport, device scale factor,
  output dimensions, locale, timezone, and loaded font files;
- disable animation, transitions, caret, network-dependent content, timestamps,
  random values, and environment-dependent labels;
- wait for `document.fonts.ready` and the chart-ready signal before capture;
- capture from a local source with a repository script or reproducible command;
- render twice from unchanged inputs and require identical PNG dimensions and
  SHA-256 hashes.

A changed browser version or font set invalidates replay evidence. If stable
capture cannot be proved, return to SVG -> PNG.

## Readability

- Include a legend whenever two or more series, colors, or line/bar groups are
  compared.
- Labels, axes, and legends must state units.
- Avoid palettes where adjacent series are hard to distinguish.
- Do not hide important values behind decorative gradients or oversized titles.
- Use enough plot margins so tick labels, series labels, and legends do not
  clip in PNG output.

## Verification

- Confirm the data source and transformation in the evidence ledger.
- Inspect the rendered PNG at full size.
- For a DOM-native chart, cross-check every displayed value and CSS dimension
  against the single data source, then prove the deterministic replay contract.
- For coordinate-driven SVG charts, verify every series value, axis domain,
  tick/unit mapping, scale transform, and plotted coordinate rather than only a
  representative point.
- Reject charts with missing legends, unreadable tick labels, clipped text,
  misleading scales, or unexplained color meaning.

## Blocking Chart Checklist

- [ ] **DIA-CHART-01 — Ground the data and question**
  - **Action:** Record source data, transformation, metric direction, and the reader question that benefits from a chart.
  - **Evidence:** Source path/artifact and reproducible transformation ledger.
  - **Failure:** Use prose/table or remove the chart when data/question is not grounded.
- [ ] **DIA-CHART-02 — Select a truthful chart form**
  - **Action:** Consult current best practices, choose form/scale/layout, and apply the render-pipeline table. Use HTML/CSS only when every DOM-native eligibility condition passes.
  - **Evidence:** Form/scale rationale, reference, selected pipeline, and eligibility decision.
  - **Failure:** Reject misleading axes/scales, decorative value hiding, an ambiguous HTML exception, or HTML-wrapped SVG/canvas plotting.
- [ ] **DIA-CHART-03 — Make series and units readable**
  - **Action:** Add legends for comparisons, units on labels/axes/legends, distinct palette, and sufficient margins.
  - **Evidence:** Full-size PNG inspection of ticks, labels, legend, colors, and clipping.
  - **Failure:** Missing units/legend, indistinguishable series, or clipped text blocks PASS.
- [ ] **DIA-CHART-04 — Verify rendered meaning**
  - **Action:** Compare rendered values to source/transformation at full size. Check every displayed value and CSS dimension for HTML/CSS; check every series point, axis domain, tick/unit mapping, scale, and coordinate for coordinate-driven SVG.
  - **Evidence:** Complete value/geometry cross-check and PNG path.
  - **Failure:** Repair any source/render mismatch before publication.
- [ ] **DIA-CHART-05 — Prove single-source HTML data**
  - **Action:** For the HTML/CSS branch, drive labels, values, ordering, and dimensions from one machine-readable data source; otherwise record SVG-branch N/A evidence.
  - **Evidence:** Data path, render input command, duplicate-value check, or concrete SVG-branch N/A.
  - **Failure:** Hand-copied values or CSS dimensions block HTML/CSS publication.
- [ ] **DIA-CHART-06 — Prove deterministic HTML replay**
  - **Action:** For the HTML/CSS branch, capture twice with pinned browser/font/environment inputs after readiness; otherwise record SVG-branch N/A evidence.
  - **Evidence:** Browser/version, viewport, device scale, locale/timezone, font files, two commands, equal dimensions, and equal SHA-256 hashes.
  - **Failure:** Any replay drift returns the chart to repair or SVG -> PNG.
