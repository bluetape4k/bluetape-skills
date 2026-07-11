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
- Reject charts with missing legends, unreadable tick labels, clipped text,
  misleading scales, or unexplained color meaning.

## Blocking Chart Checklist

- [ ] **DIA-CHART-01 — Ground the data and question**
  - **Action:** Record source data, transformation, metric direction, and the reader question that benefits from a chart.
  - **Evidence:** Source path/artifact and reproducible transformation ledger.
  - **Failure:** Use prose/table or remove the chart when data/question is not grounded.
- [ ] **DIA-CHART-02 — Select a truthful chart form**
  - **Action:** Consult current best practices and choose form/scale/layout without misleading compression or decoration.
  - **Evidence:** Form/scale rationale and reference.
  - **Failure:** Reject misleading axes/scales or decorative value hiding.
- [ ] **DIA-CHART-03 — Make series and units readable**
  - **Action:** Add legends for comparisons, units on labels/axes/legends, distinct palette, and sufficient margins.
  - **Evidence:** Full-size PNG inspection of ticks, labels, legend, colors, and clipping.
  - **Failure:** Missing units/legend, indistinguishable series, or clipped text blocks PASS.
- [ ] **DIA-CHART-04 — Verify rendered meaning**
  - **Action:** Compare plotted values to source/transformation at full size.
  - **Evidence:** Representative value cross-check and PNG path.
  - **Failure:** Repair any source/render mismatch before publication.
