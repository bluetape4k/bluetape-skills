# Business Workflow Rules

Use with `common.md` for business workflows, service journeys, decision maps,
operational process views, and state/branch explorers. Technical sequence,
protocol, retry, and lifecycle diagrams remain governed by `sequence.md`.

## Pipeline Selection

HTML/CSS/JavaScript -> PNG is preferred when the workflow is reader-explorable
and normal DOM layout expresses the content.

| Use HTML/CSS/JavaScript -> PNG when | Keep SVG -> PNG when |
| --- | --- |
| readers filter scenarios, reveal branches, compare states, or switch explanatory views | one static path or topology is the complete message |
| cards, panels, tables, callouts, and responsive sections carry more meaning than exact connector geometry | exact edge attachment, ordering, ports, arrowheads, or routed topology carry meaning |
| dark/light and locale-specific companion pages are part of a broader multi-view experience | theme or locale is the only reason to prefer HTML |
| the workflow needs a linked explanatory companion beyond the README snapshot | the README image is the complete deliverable |

Do not choose HTML merely because a browser is available. Do not force a
reader-explorable workflow into SVG merely to reuse the structural-diagram
pipeline.

## Source Contract

- Keep one structured source for steps, branches, state outcomes, labels, and
  ordering. Do not hand-copy the same rule into markup, JavaScript, and PNG.
- Keep English and Korean files source-equivalent. Technical identifiers,
  state names, API names, and decision outcomes remain identical across
  locales.
- Keep raw personal data, secrets, production identifiers, and sensitive
  examples out of the source, HTML, logs, and screenshots.
- Use normal DOM layout as the primary geometry. Do not wrap a
  coordinate-driven SVG or canvas renderer in HTML to bypass the SVG contract.
- Use semantic HTML landmarks, headings, buttons, labels, and focus order.
- Support `auto`, `light`, and `dark` themes without network-dependent assets.
- Disable animation and transitions for capture and reduced-motion users.

## README and Publication

- README and Markdown pages embed PNG fallbacks, not HTML.
- Link the PNG or adjacent text to the matching locale HTML companion.
- For theme-aware README previews, use a `<picture>` with light/dark PNG
  sources when the target renderer supports it.
- Export the bounded locale/theme matrix from the same HTML source:
  `en.light.png`, `en.dark.png`, `ko.light.png`, and `ko.dark.png`.
- Do not export every interactive branch. Select the default and
  decision-relevant snapshots; the HTML companion owns exploration.

## Deterministic Capture

For every eligible HTML workflow:

- pin and record Chromium version, viewport, device scale factor, locale,
  timezone, loaded fonts, theme, and selected workflow view;
- wait for `document.fonts.ready` and an explicit workflow-ready signal;
- disable timestamps, randomness, network requests, caret, animation, and
  environment-dependent labels;
- capture every declared locale/theme fallback twice from unchanged inputs;
- require equal dimensions and SHA-256 hashes for both captures.

Capture drift blocks publication. Repair the source/environment or return the
asset to SVG when deterministic replay cannot be proved.

## Blocking Workflow Checklist

- [ ] **DIA-WORKFLOW-01 — Prove HTML eligibility**
  - **Action:** Record the reader interactions/views that make the workflow more than a static connector diagram.
  - **Evidence:** Required filters, branches, state comparisons, or explanatory panels and the rejected SVG-only alternative.
  - **Failure:** Theme/locale alone or generic browser availability does not pass.
- [ ] **DIA-WORKFLOW-02 — Ground every branch and outcome**
  - **Action:** Map every visible step, branch, state, and outcome to source-backed behavior.
  - **Evidence:** Structured source path and branch/outcome ledger.
  - **Failure:** Invented, unreachable, omitted, or contradictory paths block publication.
- [ ] **DIA-WORKFLOW-03 — Preserve locale equivalence**
  - **Action:** Verify English and Korean companions expose equivalent steps, branches, identifiers, and outcomes.
  - **Evidence:** Locale pair paths and structural/content comparison.
  - **Failure:** Missing locale content or semantic drift blocks publication.
- [ ] **DIA-WORKFLOW-04 — Verify themes and accessibility**
  - **Action:** Inspect auto/light/dark rendering, keyboard navigation, focus visibility, reduced motion, contrast, and responsive overflow.
  - **Evidence:** Desktop/narrow viewport results for both locales and both explicit themes.
  - **Failure:** Clipping, hidden controls, unreadable contrast, or inaccessible branches blocks publication.
- [ ] **DIA-WORKFLOW-05 — Prove deterministic fallbacks**
  - **Action:** Capture the bounded locale/theme PNG matrix twice with pinned inputs.
  - **Evidence:** Four fallback paths, commands, dimensions, and paired SHA-256 equality.
  - **Failure:** Missing fallback, unbounded branch snapshots, or hash drift blocks publication.
- [ ] **DIA-WORKFLOW-06 — Verify README routing**
  - **Action:** Confirm each README locale shows the correct theme-aware PNG and links to the matching HTML companion.
  - **Evidence:** English/Korean README link and image targets.
  - **Failure:** Cross-locale routing, direct HTML embedding, or stale fallback paths blocks publication.
