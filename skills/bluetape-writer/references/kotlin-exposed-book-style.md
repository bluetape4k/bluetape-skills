# Kotlin Exposed Book Voice

Use only when the user asks for their Exposed-book voice or rejects generic AI
prose. This reference is derived from the user's Kotlin Exposed Book corpus,
especially the async/non-blocking and high-performance chapters. Refresh via
the Notion connector when exact current corpus evidence is required.

## Core Rhythm

1. Start from the reader's problem, operational history, or current mental
   model.
2. Show the smallest useful code, schema, query, diagram, configuration, or
   measured result.
3. Explain in plain Korean what it proves and which runtime/request path changes.
4. Name the caveat, operational boundary, or selection rule.

## Voice

- Practical and slightly conversational; assume the reader is building or
  operating a system, not browsing a feature brochure.
- Keep API/ecosystem names stable in English while explaining behavior in
  natural Korean.
- Personal judgment is acceptable when grounded in experience and not overused.
- Compare JPA, MyBatis, JDBC, R2DBC, Vert.x, Spring Data, plain SQL, or a local
  helper only when the tradeoff is concrete.
- Code is evidence: explain generated SQL/config/result, thread model, cache
  path, or avoided failure after each meaningful snippet.
- Dry humor names a real pain and ends quickly.

## Async and Performance Emphasis

- Separate IO-bound from CPU-bound async work.
- Call out false combinations directly, such as blocking DB work consuming an
  event loop; also acknowledge when synchronous Spring is the pragmatic choice.
- Performance claims name workload shape and the changed path: cache strategy,
  read/write routing, tenant lookup, event loop, virtual thread, dispatcher,
  connection pool, or round trips.
- Compare blocking and coroutine variants by runtime model, not vague
  faster/slower language.
- End with a selection table/rule rather than a universal recommendation.

## Section and Code Flow

- Prefer “why” before “what”. Open module sections with the service/test problem
  removed by the helper.
- Use one term for one concept; translate behavior, not API identifiers.
- Name dangerous edges directly: transaction/rollback, lazy loading, blocking
  JDBC, pool size, cache invalidation, nullability, dialect, or tenant routing.
- For code-heavy posts: domain setup -> representative snippet -> resulting
  behavior/SQL/runtime path -> rule of thumb.
- End each section with a practical caveat or choice.

## Anti-Patterns

- Feature catalogs without a reader problem.
- Unproved praise such as powerful, flexible, efficient, robust, or seamless.
- Corporate/textbook polish that removes the author's practical voice.
- Cute metaphors, one joke per paragraph, hidden uncertainty, or universal
  framework recommendations.

## Blocking Book-Voice Checklist

- [ ] **BOOK-01 — Start from the reader's operating problem**
  - **Action:** Open from the current mental model, failure, or service/test problem before features.
  - **Evidence:** Intro and section-opening review.
  - **Failure:** Rewrite brochure-like openings.
- [ ] **BOOK-02 — Use code and results as evidence**
  - **Action:** Show the smallest useful code/schema/query/config/result and explain the resulting SQL/runtime/cache/request path.
  - **Evidence:** Snippet-to-behavior mapping.
  - **Failure:** Remove unexplained or decorative code.
- [ ] **BOOK-03 — Name async and performance boundaries**
  - **Action:** Separate IO/CPU work, call out blocking/event-loop conflicts, name workload/path, and compare runtime models.
  - **Evidence:** Concrete workload, path, result, and caveat.
  - **Failure:** Reject vague faster/slower claims.
- [ ] **BOOK-04 — End with a practical choice**
  - **Action:** Close sections with caveats/rules and end comparisons with a selection rule/table instead of a universal recommendation.
  - **Evidence:** Section endings and final choice guidance.
  - **Failure:** Replace generic conclusions.
- [ ] **BOOK-05 — Preserve the user's restrained voice**
  - **Action:** Keep natural Korean, stable API names, grounded judgment, and brief pain-linked humor while removing corporate polish and cute metaphors.
  - **Evidence:** Final voice comparison to the requested corpus/style.
  - **Failure:** Revert over-polished or generic AI phrasing.
