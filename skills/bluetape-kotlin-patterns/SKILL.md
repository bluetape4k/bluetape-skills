---
name: bluetape-kotlin-patterns
description: Use when implementing or reviewing Kotlin code, tests, Spring Boot configuration, Exposed/data access, public APIs, or Gradle modules in a bluetape4k repository.
---

# bluetape4k Kotlin Code Patterns

## Parent Contract

Use `bluetape-workflow` first to select Type A/B/C/D/F, or Type P release
preflight when Kotlin code needs a verdict, and to own plan approval, gate
progression, and Step DoD reporting. This support skill supplies Kotlin
implementation and review rules; it does not authorize edits or PR actions.

Every Kotlin implementation lane and every Kotlin code-review verdict must read
this skill. Report its triggered checks in the parent workflow's DoD evidence.

## Conditional Reference Loading

| Trigger | Required reference |
|---|---|
| Any new/touched Kotlin tests, fixtures, Testcontainers, HTTP adapter, or HC5 factory | `references/testing.md` |
| Spring Boot auto-configuration, properties, conditional beans, or library integration tests | `references/spring-boot.md` |
| Module add, move, rename, removal, benchmark module, or artifact rename | `references/module-setup.md` and workflow `references/repository-hazards.md` |
| Before completion or a Kotlin review verdict | `references/checklist.md` |

Load `kotlin-coroutines-skill`, `ecc-kotlin-exposed`, or
`ecc-springboot-kotlin` as additional domain guidance when the touched behavior
requires deeper coroutine, Exposed, or Spring reasoning.

## Evidence and Reuse First

- Inspect current source, tests, KDoc/README, callers, and symbol impact before
  editing. Use current evidence rather than memory or stale specs.
- Search the current repository, sibling bluetape4k repositories, and version
  catalog for existing helpers, extensions, fixtures, and conventions before
  adding raw JDK/third-party/ad hoc utilities.
- Use a raw fallback only when no suitable ecosystem helper exists or the raw
  API is the behavior under test; record the reason.
- Keep review-only work read-only. Re-review means reopen the latest artifact
  and revalidate old findings against current files.

## Validation and Invariants

- Caller input uses bluetape4k `require*` helpers and preserves their
  `IllegalArgumentException` contract. Keep the returned validated value.
- Internal state invariants use `check`/`checkNotNull`; do not use them for
  caller validation or double-check a `requireNotNull` result.
- Preserve existing exception contracts. Do not replace an established
  `AssertionError`, `IllegalArgumentException`, or domain exception with
  `IllegalStateException` merely to standardize on `check`.
- Do not introduce `!!` in production code.

```kotlin
val validName = name.requireNotBlank("name")
val validId = id.requireNotNull("id")
check(state == State.READY) { "state must be READY" }
```

## Logging, Coroutines, and Lifecycle

- Use established `KLogging()` patterns; use `KLoggingChannel()` for
  coroutine-heavy components. Prefer lazy messages and `log.warn(e) { ... }`.
- Rethrow `CancellationException` before broad exception handling. Do not wrap
  suspend calls or suspend close paths in `runCatching`.
- If cleanup must run after cancellation, isolate only cleanup in
  `NonCancellable`, then rethrow the original cancellation.
- Wrap blocking APIs in `withContext(Dispatchers.IO)` and avoid `GlobalScope`.
- In cancellable loops, prefer `currentCoroutineContext().ensureActive()`;
  query `Job` only when a liveness Boolean is needed.
- The coroutine context dispatcher key is `ContinuationInterceptor`, not
  `CoroutineDispatcher`.
- Do not expose mutable flows/channels as public API.
- In virtual-thread-aware code, avoid monitors (`@Synchronized`,
  `synchronized`); use explicit concurrency primitives.
- AtomicFU is for class properties. Local counters use
  `java.util.concurrent.atomic.*`.
- In-flight `Deferred` caches remove failed/cancelled values and test evaluator
  failure, explicit cancellation, and real job cancellation.
- `close()` handles independent non-suspending resources independently; define
  ownership and cleanup on every failure path.

## Kotlin API and Modeling

- Prefer top-level package functions, extension functions, DSL builders, named
  parameters, immutable values, and expression-style helpers over Java-style
  wrappers or bean mutation.
- Wrap two or more same-typed domain parameters in a named value object, or use
  named arguments when a wrapper would be disproportionate.
- Public durable contracts need English KDoc, realistic examples, direct
  tests, and README/API entries together.
- Data classes implement `Serializable` and define `serialVersionUID`. When a
  data-class constructor requires validation, prevent generated construction
  paths from bypassing it.
- Prefer existing value generators: UUID-valued identities use the ecosystem
  UUID generator; unique string suffixes use the established Base58 helper.
- Use `INHERIT` when an annotation default must differ from a global property
  default.
- Keep lifecycle vocabulary precise: `close` shuts resources; `clear` removes
  state/cache entries.
- Verify public helper names against actual source vocabulary before adding
  aliases or documentation.

## Exposed and Data Boundaries

- Import Exposed operators from current top-level packages; never introduce
  deprecated `SqlExpressionBuilder.eq`.
- In `insert`, `update`, and `deleteWhere`, guard implicit receiver shadowing by
  extracting colliding values to named locals.
- Verify DDL customization against the actual Exposed API/source in use.
- Prefer established datasource/repository/dialect helpers over raw JDBC or
  new wrappers.
- Shared DB tests avoid destructive schema recreation unless isolation proves
  it safe.
- Token/TTL locks verify live ownership before extend/release and use
  server-side time when available. Keep sync/async/suspend/virtual-thread entry
  paths behaviorally aligned.

## Documentation and Contribution Surface

- Public KDoc, CHANGELOG, release notes, issues, PRs, and pushed commits are
  English. Keep `README.md` and existing localized README files equivalent when
  behavior or examples change.
- Grep actual classes, functions, and capabilities before accepting public
  documentation claims.
- Load `bluetape-diagram` for README diagrams or benchmark charts.
- Keep agent-facing guidance concise English; internal specs/plans/lessons may
  use Korean under workspace policy.

## Review Focus

## Mandatory Kotlin Checklist

Apply `bluetape-workflow/references/checklist-contract.md`. Complete
`references/checklist.md`; its rows are the canonical Kotlin verdict state.

- [ ] **KT-01 — Load triggered Kotlin guidance**
  - **Action:** Classify the touched Kotlin surface and load every matching testing, Spring, module, coroutine, Exposed, and domain reference.
  - **Evidence:** Trigger-to-reference map with concrete touched files/symbols.
  - **Failure:** Keep implementation/review blocked until no trigger is unclassified.
- [ ] **KT-02 — Inspect impact and reuse**
  - **Action:** Inspect current source, references/callers, tests, docs, and existing ecosystem helpers before editing or judging the diff.
  - **Evidence:** Symbol-impact and reuse anchors plus rationale for every raw fallback.
  - **Failure:** Do not implement or review from memory or stale artifacts.
- [ ] **KT-03 — Enforce Kotlin contracts**
  - **Action:** Check validation/exception compatibility, cancellation/blocking/concurrency/resource ownership, API modeling, Exposed boundaries, and public documentation rules.
  - **Evidence:** Per-trigger findings tied to current file/line evidence.
  - **Failure:** Classify violations P0/P1/P2/P3 and block progression on P0/P1.
- [ ] **KT-04 — Prove behavior with Kotlin validation**
  - **Action:** Run diagnostics, import/deprecation cleanup, targeted compile/tests, triggered lifecycle/concurrency checks, and `git diff --check`.
  - **Evidence:** Fresh commands/results or an exact unavailable-tool fallback with equivalent proof.
  - **Failure:** Do not issue a Kotlin PASS verdict from stale, partial, or unexplained missing validation.
- [ ] **KT-05 — Render the final Kotlin checklist**
  - **Action:** Complete every row in `references/checklist.md` and all triggered reference checklists, then report severity convergence in the parent DoD.
  - **Evidence:** X=Y, Blocked=0, concrete N/A evidence, and P0=0/P1=0.
  - **Failure:** Expose the unchecked row and repair action instead of claiming completion.

Review the exact current diff and call out P0/P1/P2/P3 with file/line evidence:

- validation/exception compatibility;
- cancellation, dispatcher, blocking, concurrency, and resource ownership;
- API compatibility and caller ergonomics;
- Exposed transaction/receiver/deprecation risk;
- triggered Spring/testing/module rules;
- test assertions that can pass without proving named behavior;
- public docs/source drift and verification gaps.

The main workflow owns severity convergence and final acceptance. Before a
verdict or completion claim, load `references/checklist.md` and run the smallest
fresh compile/test/diagnostic evidence that can prove the claim.
