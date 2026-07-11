# Blog Style and Visual Checklist

Use after reading 2-3 representative posts from the same locale and, when
possible, the same series or article shape.

## Article Shape

- Match nearby frontmatter fields, title/subtitle pattern, hero placement,
  heading depth, table style, code-block length, source-link style, and closing.
- Introduce the practical problem quickly. Architecture posts explain the pain
  before the diagram; benchmark posts explain the scenario before results;
  workshop posts move from runnable profile to result to operational lesson.
- Keep code snippets short and surround them with what the code proves.
- Multi-part posts use local article flow and bottom series navigation, not a
  repeated global outline.
- Bilingual work keeps route, part, title, link, number, and asset parity.

## Voice

- Keep a practical engineer-to-engineer tone and concrete transitions.
- Light humor must sharpen real engineering pain, not replace explanation.
- Avoid unnatural personification, generic praise, marketing structure, and
  vague infrastructure language.
- English localization preserves claims and evidence but does not translate
  Korean jokes or idioms literally.

## Hero and Embed QA

- Match the current series' hero composition and first-viewport subject.
- A requested worker/operator is clearly robotic when that is the established
  visual language.
- Avoid generic stock atmosphere and flat diagram-like heroes.
- Embed rendered PNGs in MDX and keep the companion source assets required by
  the selected visual skill.
- Verify changed routes render the expected images.

## Final Consistency Pass

Compare title, intro, headings, tables, code density, visual placement, closing,
and links against the sampled posts. If the result reads like a standalone
marketing article rather than a bluetape4k engineering note, revise it.

## Blocking Style Checklist

- [ ] **STYLE-01 — Match local article shape**
  - **Action:** Match sampled frontmatter, title/subtitle, hero, headings, tables, code density, links, closing, and series navigation.
  - **Evidence:** Draft-to-sample comparison with named nearby posts.
  - **Failure:** Revise structural drift before voice review.
- [ ] **STYLE-02 — Lead with the engineering problem**
  - **Action:** Introduce the practical scenario before architecture/results and explain what every code snippet proves.
  - **Evidence:** Section mapping from problem to evidence to interpretation.
  - **Failure:** Rewrite catalog-like or unexplained code sections.
- [ ] **STYLE-03 — Preserve a concrete voice**
  - **Action:** Remove generic praise, marketing structure, vague infrastructure language, and humor without a real failure mode.
  - **Evidence:** Reviewed prose with concrete claims and transitions.
  - **Failure:** Keep style blocked while the article reads like generic promotion.
- [ ] **STYLE-04 — Verify visual fit and embeds**
  - **Action:** Match series hero language, keep companion diagram assets, and render changed routes with expected images.
  - **Evidence:** Contact-sheet or diagram QA plus route screenshots/build evidence.
  - **Failure:** Reject generic heroes, flat substitutes, or broken/uninspected embeds.
- [ ] **STYLE-05 — Recheck bilingual consistency**
  - **Action:** Compare route, part, title, link, number, asset, and navigation parity for bilingual scope.
  - **Evidence:** Locale comparison matrix or concrete single-locale N/A.
  - **Failure:** Drift blocks completion.
