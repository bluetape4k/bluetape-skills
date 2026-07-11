# Cache Series Lessons

Use this reference when writing or reviewing bluetape4k cache, Near Cache, Exposed cache strategy, or workshop cache articles.

## Series Shape

- Part 1: bluetape4k Cache module overview.
- Part 2: Near Cache need, structure, Redisson Pub/Sub vs Lettuce RESP3, benchmark summary.
- Part 3: Near Cache + Exposed strategies using `bluetape4k-exposed` and `exposed-workshop` chapter 11.
- Part 4: practical examples using `bluetape4k-workshop`.
- Adjust part count only when content density or source evidence requires it.

## Corrections To Preserve

- Say "더 많은 코드를 차지합니다", not awkward personification such as "더 많은 표정을 짓습니다".
- Say "Redis가 잠깐 불안정되었을 때".
- Say "장애 증폭기".
- Say "첫 요청은 DB에서 읽고".
- Avoid "DB를 치고" in explanatory prose unless deliberately colloquial.

## Cache Strategy Accuracy

- Cache-aside PUT management is not true write-through.
- For real read-through/write-through/write-behind examples, use `exposed-workshop` chapter 11 and the `JdbcCacheRepository` implementation path.
- Show or link `JdbcCacheRepository` when explaining the abstraction.
- The Exposed strategy map should show:
  - `JdbcCacheRepository`
  - `RMap` / `RLocalCachedMap`
  - `EntityMapLoader` for read-through miss loading
  - `EntityMapWriter` for write-through/write-behind persistence
  - Exposed DB / table boundary
- If `bluetape4k-workshop` examples diverge from the article's intended strategy names, create a GitHub issue instead of presenting the examples as canonical.

## Benchmark Coverage

- Part 2, Part 3, and Part 4 should include benchmark results when benchmark evidence exists.
- Do not dump all benchmark rows. Summarize the profiles that prove the article's point, and link/source the full benchmark data.
- State metric direction: higher throughput is better; lower latency is better.
- Include representative values in prose/table and chart where useful.

## Source Links

- Use develop-branch links for full source.
- Keep snippets short and explanatory; full source links carry the complete context.

## Blocking Cache-Series Checklist

- [ ] **CACHE-01 — Confirm series placement**
  - **Action:** Map the article to the four-part series and change part count only from content-density/source evidence.
  - **Evidence:** Part purpose, neighboring links, and rationale for any series change.
  - **Failure:** Do not publish overlapping or orphaned series content.
- [ ] **CACHE-02 — Preserve accepted Korean corrections**
  - **Action:** Apply the named wording corrections and reject awkward personification/colloquial drift.
  - **Evidence:** Final prose search/review.
  - **Failure:** Repair known rejected phrases before approval.
- [ ] **CACHE-03 — Verify cache strategy accuracy**
  - **Action:** Distinguish cache-aside from read/write-through/behind and map repository, map, loader, writer, and DB/table boundaries from source.
  - **Evidence:** Current source links and architecture mapping.
  - **Failure:** File source-drift issue or correct the article; never present divergent examples as canonical.
- [ ] **CACHE-04 — Ground benchmark claims**
  - **Action:** Summarize representative profiles with source, context, values, direction, caveats, and full-data link.
  - **Evidence:** Benchmark ledger/table/chart and exact provenance, or concrete no-evidence N/A.
  - **Failure:** Remove unmeasured performance claims or undirected numbers.
- [ ] **CACHE-05 — Verify source links and snippets**
  - **Action:** Keep snippets focused and link full current develop source for context.
  - **Evidence:** Valid source URLs and snippet-to-source match.
  - **Failure:** Repair stale refs, identifiers, or truncated misleading examples.
