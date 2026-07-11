---
name: bluetape-writer
description: Use when writing, reviewing, localizing, or validating README files, technical documentation, articles, Korean technical prose, or bilingual public content in the bluetape ecosystem.
---

# Bluetape Writer

## Parent Contract

Use `bluetape-workflow` first and route article/document maintenance through
Type E. The parent workflow owns plan approval, mutation authority, Step DoD,
GitHub metadata, and PR/merge boundaries. This skill owns README, documentation,
article, and localization evidence; structure; locale parity; technical voice;
source links; and site validation.

Load `bluetape-diagram` for diagrams, charts, Mermaid/ASCII conversion, or
visual QA. Hero images are bitmap scene assets and follow the image-generation
surface, not the diagram construction rules.

For release, tag, Maven, catalog, or Go publication actions, load the matching
`bluetape-publish-jvm` or `bluetape-publish-go` skill. Writer work does not
authorize publication side effects.

## Conditional Reference Loading

| Trigger | Required reference |
|---|---|
| Any new post or substantial rewrite | `references/blog-style-checklist.md` after reading 2-3 nearby posts |
| Cache, Near Cache, Exposed cache, or workshop cache series | `references/cache-series-lessons.md` |
| Korean draft is translated, generic, promotional, or LLM-like | `references/korean-naturalness-checklist.md` after facts are locked |
| User asks for their Exposed-book voice or says the text does not sound like them | `references/kotlin-exposed-book-style.md` |

Do not load cache or personal-voice references for unrelated posts.

## Ordered Workflow

1. Confirm single post/series, Korean-only/English-only/bilingual scope, source
   repositories, branch, benchmark evidence, and visual needs.
2. Read representative nearby posts in the same locale and the triggered style
   references. Extract frontmatter, hero placement, heading rhythm, code/table
   density, links, closing, and series navigation.
3. Ground every technical claim in current source, docs, benchmark artifacts,
   or official references. Preserve decision-relevant external research under
   the workspace web-research SOP.
4. Draft Korean first unless the user explicitly requests another locale.
5. Review facts, identifiers, numbers, source URLs, benchmark direction, and
   code snippets before prose humanization.
6. Run the triggered Korean naturalness/personal-voice pass. Preserve facts,
   terms, numbers, commands, citations, and user wording; manually reject any
   rewrite that changes meaning.
7. Obtain Korean approval when the workflow requires bilingual publication,
   then localize English naturally. Do not translate Korean idioms literally.
8. Create/validate visuals with the correct companion skill and inspect rendered
   output at article scale.
9. Build the site and verify every changed route, locale pair, asset, and series
   link before completion.

## Evidence Rules

- Do not describe repository behavior from memory while source is available.
- Inspect actual class/function/config names and link full source to the current
  `develop` branch unless the article intentionally targets another ref.
- If examples reveal source drift, file or request a durable issue instead of
  silently writing around the mismatch.
- Benchmark claims include source/artifact, command or run context, environment,
  representative values, metric direction, caveats, and what the result does
  not prove. Summarize decision-relevant profiles rather than dumping all rows.
- Never claim “latest” without checking current source or benchmark output.
- Short code snippets explain one idea; source links carry full context.

## Locale and Series Contract

- Korean routes are Korean-first. Unless the user explicitly scopes
  Korean-only, a bilingual article is incomplete until matching English routes
  exist and build.
- Keep Korean `/ko/blog/...` and English `/blog/...` part counts, titles,
  technical claims, numbers, source links, asset references, and bottom series
  navigation aligned.
- Public GitHub artifacts and pushed commits remain English under workspace
  policy. Diagram labels remain English unless localization is materially useful.
- Apply user wording corrections exactly when they improve naturalness or
  technical precision.

## Korean Technical Voice

- Practical engineer-to-engineer prose; explain the reader's problem before a
  capability list.
- Specific evidence beats importance claims. Concrete verbs beat noun-heavy
  translation. Repeat the same technical term for the same concept.
- Natural Korean is mandatory; humor is optional. Use familiar engineering
  idioms only when they clarify a concrete failure mode, then return to the
  technical explanation.
- Reject English sentence skeletons, writer-diary openings, vague impression
  verbs, invented metaphors, marketing praise, and filler conclusions.
- Check subject/predicate and semantic dimension: impact scope is small/large,
  not short/long. Prefer `X 우선` for “X First” headings.
- A strong section follows: reader problem -> smallest useful code/result ->
  interpretation -> caveat/selection rule.

## Visual Contract

### Hero Images

- Inspect same-series and nearby heroes before generating/replacing one.
- Match the existing polished bitmap scene language. For the
  `bluetape4k-projects` series, use the established 3D miniature workbench with
  white/blue robotic builders, Kotlin/JVM module blocks, blueprint props, and
  bright studio lighting.
- A flat diagram, SVG card flow, icon sheet, or generic stock illustration is
  not a valid hero unless the user explicitly requests that style.
- Compare the candidate against an equal-size contact sheet of existing heroes.

### Diagrams and Charts

- Load `bluetape-diagram` and follow its current output/evidence contract.
  Do not impose a conflicting renderer or Graphviz requirement here.
- Use visuals only when they reduce cognitive load or show measured data.
- Keep source plus required SVG/PNG outputs, inspect rendered PNGs at article
  scale, and verify labels, endpoints, spacing, fonts, and MDX embeds.

## Validation and Completion

## Mandatory Article Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **BLOG-01 — Pin article scope and evidence**
  - **Action:** Record post/series, locale scope, source repos/refs, benchmark evidence, routes, visual needs, and publication authority.
  - **Evidence:** Approved scope, exact source/benchmark paths or URLs, route map, and side-effect boundary.
  - **Failure:** Stop drafting claims whose source, locale, or target route is ambiguous.
- [ ] **BLOG-02 — Load local style and triggered references**
  - **Action:** Read 2-3 nearby same-locale posts and every trigger-matched style/cache/naturalness/personal-voice reference.
  - **Evidence:** Sampled paths and extracted frontmatter, heading, code/table, link, visual, closing, and navigation patterns.
  - **Failure:** Do not draft from generic blog conventions or load unrelated voice overlays.
- [ ] **BLOG-03 — Lock factual claims**
  - **Action:** Verify identifiers, behavior, numbers, source URLs, code, metric direction, caveats, and “latest” claims from current source or primary evidence.
  - **Evidence:** Claim-to-source ledger and preserved research artifact when required.
  - **Failure:** Remove/qualify unsupported claims or file the source-drift issue before prose polishing.
- [ ] **BLOG-04 — Draft the primary locale**
  - **Action:** Draft Korean first unless another locale is explicitly requested, following reader problem -> useful evidence -> interpretation -> caveat/selection rule.
  - **Evidence:** Complete primary-locale route with local article shape and exact technical terms.
  - **Failure:** Revise feature-catalog, marketing, or evidence-free sections before localization.
- [ ] **BLOG-05 — Pass voice and naturalness review**
  - **Action:** Complete triggered naturalness/personal-voice checklists after facts are locked, preserving facts, identifiers, numbers, commands, links, and user wording.
  - **Evidence:** Reviewed primary draft with reference checklist counts and no meaning-changing rewrite.
  - **Failure:** Reject translationese, generic AI prose, invented metaphors, or altered technical meaning.
- [ ] **BLOG-06 — Synchronize locale parity**
  - **Action:** After required primary approval, localize naturally and align route, part, title, claims, numbers, links, assets, and series navigation.
  - **Evidence:** Locale parity matrix or concrete evidence that the approved scope is single-locale.
  - **Failure:** A missing or drifted required locale blocks completion.
- [ ] **BLOG-07 — Create and inspect visuals**
  - **Action:** Use the correct hero or diagram surface, compare series style, and inspect rendered assets at article scale.
  - **Evidence:** Hero comparison or completed diagram checklist, asset paths, and rendered QA.
  - **Failure:** Generation success, generic stock style, or uninspected embeds is not PASS.
- [ ] **BLOG-08 — Build and verify routes**
  - **Action:** Run diff check, site build, every changed locale route, asset embed, and series-link/navigation check.
  - **Evidence:** Fresh build output and per-route/asset/parity results.
  - **Failure:** Keep publication/PR completion blocked on any missing route, asset, or navigation edge.
- [ ] **BLOG-09 — Report article DoD**
  - **Action:** Render scope, references, sources, benchmark proof, locale parity, build, routes, asset QA, gaps, and side-effect state in the parent DoD.
  - **Evidence:** X=Y, Blocked=0 with concrete evidence or valid N/A for every row.
  - **Failure:** Do not publish, merge, or claim completion; expose the unchecked row and repair action.

For `bluetape4k.github.io` changes, run:

- `git diff --check`;
- the repository site build, normally `npm run build`;
- changed Korean and English route checks;
- part-count/title/source-link/series-navigation parity;
- rendered asset inspection for every touched visual.

Completion evidence states the locale scope, triggered references, sources,
benchmark checks, site build, routes, asset QA, and known gaps in the parent
Step DoD table. A PR body ends with the central `## DoD Status` section. Do not
publish, merge, or claim completion while a required locale or route is missing.
