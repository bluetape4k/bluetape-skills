---
name: bluetape-writer
description: Use when writing, reviewing, localizing, or validating software technical documentation in the bluetape ecosystem, including README, KDoc, design, plan, review, lesson, operations, release, technical article, and diagram prose.
---

# Bluetape Writer

## Scope Boundary

This skill is exclusively for software technical documentation. Its
naturalness rules mean established Korean software technical register, not
generic conversational Korean, essay style, or advertising copy.

In scope:

- README, KDoc, API and module documentation;
- specifications, designs, implementation plans, code reviews, lessons, and
  operations or release documents;
- technical blog posts, workshop explanations, bilingual technical articles,
  and reader-facing diagram or interactive-visualization text.

Out of scope:

- essays, general-interest articles, personal reflections without a software
  engineering purpose, marketing copy, brand copy, and promotional landing-page
  prose;
- product UI microcopy whose primary concern is interaction design rather than
  technical explanation;
- legal, policy, financial, or business writing that requires its own domain
  terminology contract.

For a mixed artifact, apply this skill only to the software technical sections
and route the remaining prose to a more appropriate writing or design surface.
Do not broaden this skill's vocabulary rules to make nontechnical Korean sound
formal.

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
| Any Korean Superpowers brainstorming, specification/design, plan, review, or lesson | `references/korean-naturalness-checklist.md` after facts are locked |
| User-approved terminology set or repeated domain-term correction | `references/terminology-glossary.md` and `references/terminology-rules.json`; run `scripts/audit-korean-terms.mjs` |
| User asks for their Exposed-book voice or says the text does not sound like them | `references/kotlin-exposed-book-style.md` |

Do not load cache or personal-voice references for unrelated posts.

## Superpowers Technical Artifact Gate

Apply this gate to every new or materially revised brainstorming/design
discussion, specification/design, implementation plan, review, and lesson. It
applies to transient chat prose and review summaries as well as files under
`docs/superpowers/`, `docs/review/`, and `docs/lessons/`. Instantiate a fresh
copy for each artifact; evidence from one artifact does not prove another.

Treat a revision as material when it changes technical meaning, a decision or
recommendation, scope or boundary, acceptance/DoD mapping, evidence or source
basis, finding severity or disposition, verification claims, or the
reader-facing structure that supports those elements. Spelling, punctuation,
or layout corrections that change none of them do not require a fresh full
checklist, but the owning edit still needs the `SPW-05` final read-back.

Independent reviewer notes may remain lane-internal while perspectives are
being collected. Once those notes are integrated into a verdict, user-visible
response, or persisted review artifact, treat the integrated output as a new
artifact and complete the full `SPW-01` through `SPW-05` gate.

Apply `bluetape-workflow/references/checklist-contract.md`. Every row below is
required unless the entire artifact is out of scope. A language-policy reminder,
spellcheck, or generic prose cleanup cannot replace these checks. A missing or
unchecked item blocks the dependent workflow step.

The native `writer` role and this `bluetape-writer` skill are distinct. A
delegated writer response is supporting evidence only; the owning session must
still load this skill, verify the final integrated artifact, and record every
applicable `SPW-*` result.

- [ ] **SPW-01 — Lock audience, purpose, and evidence**
  - **Action:** Identify the artifact kind, primary reader, required language, decision or question, current source paths/URLs, exact identifiers, and unsupported or unresolved claims before drafting.
  - **Evidence:** Artifact path or transcript location, audience/language, purpose, source ledger, preserved technical tokens, and explicit unknowns.
  - **Failure:** Stop drafting or qualify/remove unsupported claims; do not write repository behavior from memory while current evidence is available.
- [ ] **SPW-02 — Satisfy the artifact contract**
  - **Action:** Write the smallest complete structure for the artifact kind: brainstorming states the problem, constraints, viable alternatives, recommendation, and tradeoffs; a spec adds boundaries, contracts, failure modes, compatibility, acceptance criteria, and DoD; a plan adds dependency order, exact actions/files, expected evidence, tests, rollback/rerun points, and approval gates; a review adds scope/basis, severity, concrete location/evidence, disposition, gaps, and verdict; a lesson adds context, decision, outcome, verification, miss or surprise, and a future guard or evidence-backed N/A.
  - **Evidence:** Artifact sections or transcript anchors covering every applicable field without filler.
  - **Failure:** Keep the artifact incomplete and block approval, implementation, PR progression, or lesson closure until the missing contract is repaired.
- [ ] **SPW-03 — Apply Korean technical register**
  - **Action:** For Korean artifacts, complete `references/korean-naturalness-checklist.md` after facts are locked; use precise engineer-to-engineer prose, stable terminology, concrete verbs, and correct subject/predicate and semantic dimensions while preserving code, identifiers, commands, URLs, numbers, citations, and exact errors. For an explicitly non-Korean artifact, apply the same precision and preservation rules in its approved language.
  - **Evidence:** Completed naturalness checklist for Korean or approved non-Korean scope, terminology decisions, and confirmation that no meaning-changing rewrite occurred.
  - **Failure:** Reject translationese, promotional or generic AI prose, invented metaphors, vague conclusions, terminology drift, or any rewrite that changes technical meaning.
- [ ] **SPW-04 — Verify technical meaning and traceability**
  - **Action:** Read the finished artifact against its sources and upstream/downstream artifacts; verify facts, identifiers, numbers, links, examples, decisions, acceptance mapping, severity, commands, and stated gaps without softening uncertainty or findings.
  - **Evidence:** Source-to-claim and, when applicable, spec-to-plan or finding-to-disposition traceability with mismatches repaired.
  - **Failure:** Reopen the artifact and every dependent review or approval affected by drift; a later test or CI pass does not repair prose traceability.
- [ ] **SPW-05 — Read back and record writer DoD**
  - **Action:** Re-read the rendered Markdown or final transcript in context, confirm headings/tables/lists/code fences and concise technical flow, then record `SPW-01` through `SPW-05` status in the owning workflow evidence.
  - **Evidence:** Final path or transcript anchor, read-back result, applicable checklist count, remaining gaps, and owning workflow step.
  - **Failure:** Leave the writer gate unchecked and block the dependent workflow step; do not claim the artifact or workflow step complete.

## Article Workflow

Use this sequence only for technical posts, series, or site routes. For README,
KDoc, design, plan, review, lesson, operations, release, or diagram prose, stay
inside the parent workflow already selected by `bluetape-workflow` and apply
the matching writer gate plus triggered references; standalone documentation
maintenance remains Type E. Do not require post, series, hero,
locale-publication, or site-build steps.

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
6. Run the contextual terminology audit before the Korean naturalness pass.
   Resolve collection/item, database-row/action-message, state-code/reader-label,
   and code-token/prose distinctions instead of applying global replacements.
7. Run the triggered Korean naturalness/personal-voice pass. Preserve facts,
   terms, numbers, commands, citations, and user wording; manually reject any
   rewrite that changes meaning.
8. Obtain Korean approval when the workflow requires bilingual publication,
   then localize English naturally. Do not translate Korean idioms literally.
9. Create/validate visuals with the correct companion skill and inspect rendered
   output at article scale.
10. Build the site and verify every changed route, locale pair, asset, and series
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

- Keep this skill and its instructional references in English. For user-facing
  research, specifications, plans, code reviews, lessons, `WIP.md`,
  `CHANGELOG.md`, release notes, GitHub issue/PR titles, bodies, comments, and
  pushed commit messages, write Korean prose by default; retain English only
  for code, commands, APIs, identifiers, URLs, exact source excerpts, and
  machine-required tokens. Reader-facing code comments such as KDoc, Rustdoc,
  Go doc comments, and Python docstrings are Korean as well.
- Korean routes are Korean-first. Unless the user explicitly scopes
  Korean-only, a bilingual article is incomplete until matching English routes
  exist and build.
- Keep Korean `/ko/blog/...` and English `/blog/...` part counts, titles,
  technical claims, numbers, source links, asset references, and bottom series
  navigation aligned.
- Public GitHub artifacts, CHANGELOG entries, release notes, WIP snapshots, and
  pushed commits are Korean under workspace policy.
- In localized Korean Keep a Changelog output, translate the defect category
  `Fixed` as `버그 수정`. Do not render it as `결정된`, `수정`, or `수정됨`;
  preserve `Fixed` only when an explicitly English locale or a machine-required
  token requires it.
- Translate reader-facing CHANGELOG/release-note categories `Added`, `Changed`,
  and `Removed` as `추가`, `변경`, and `제거` under the same parser/token
  exception.
- For bilingual blog posts, any diagram with reader-facing text must have
  separate Korean and English SVG/PNG assets. Korean assets use Korean labels,
  English assets use English labels, and technical identifiers remain unchanged.
  A text-free hero image may remain shared across locales.
- Apply user wording corrections exactly when they improve naturalness or
  technical precision.

## Korean Technical Voice

- This is a software technical register, not a general Korean writing style.
  Do not rewrite technical prose as an essay, conversational explanation, or
  promotional narrative in the name of naturalness.
- Practical engineer-to-engineer prose; explain the reader's problem before a
  capability list.
- Specific evidence beats importance claims. Concrete verbs beat noun-heavy
  translation. Repeat the same technical term for the same concept.
- Natural Korean is mandatory, but natural does not mean conversational.
  Match the artifact: technical articles and reports prefer established
  technical-register terms over casual paraphrases. For example, use
  `저비용 검사`, `고비용 처리`, `조기 거부`, `방지 대상`,
  `정책 불일치`, and `계약 단일화` when those terms preserve the intended
  meaning. Humor is optional.
- Do not apply the preferred terms mechanically. Choose `고비용 작업` or
  `고비용 처리` by context, and distinguish a distributed policy from an
  actual policy mismatch.
- Use familiar engineering idioms only when they clarify a concrete failure
  mode, then return to the technical explanation.
- Reject English sentence skeletons, writer-diary openings, vague impression
  verbs, invented metaphors, marketing praise, and filler conclusions.
- Translate `mental model` as `사고방식` in Korean software technical prose.
  Do not use the literal `정신 모형` or the structural term `사고 구조`.
- Check subject/predicate and semantic dimension: impact scope is small/large,
  not short/long. Prefer `X 우선` for “X First” headings.
- Separate dictionary choice from semantic role. Before replacing a term, decide
  whether it names a collection or item, a database row or an action message, a
  state identifier or a reader label, and a code token or explanatory prose.
- When a repeated correction produces a new reusable rule, add both a concise
  human rule and a machine-checkable example. Do not grow the glossary with a
  one-off synonym that has no context boundary.
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

## Technical Article Checklist

Apply this checklist to technical blog posts and article routes. For README,
KDoc, specification, design, plan, review, lesson, operations, release, or
diagram prose, use the already selected parent workflow plus `SPW-*` when
triggered; standalone documentation maintenance uses Type E. Do not instantiate
`BLOG-*` rows for a non-article artifact merely to mark article-only route,
locale, hero, or series-navigation work N/A.

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
  - **Action:** Run the contextual terminology audit, then complete triggered
    naturalness/personal-voice checklists after facts are locked, preserving
    facts, identifiers, numbers, commands, links, and user wording.
  - **Evidence:** Audit report plus reviewed primary draft with reference
    checklist counts and no meaning-changing rewrite.
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
- `node ~/.codex/skills/bluetape-writer/scripts/audit-korean-terms.mjs` for
  changed Korean article files when the terminology rules apply;
- the repository site build, normally `npm run build`;
- changed Korean and English route checks;
- part-count/title/source-link/series-navigation parity;
- rendered asset inspection for every touched visual.

Completion evidence states the locale scope, triggered references, sources,
benchmark checks, site build, routes, asset QA, and known gaps in the parent
Step DoD table. A PR body ends with the central `## DoD Status` section. Do not
publish, merge, or claim completion while a required locale or route is missing.
