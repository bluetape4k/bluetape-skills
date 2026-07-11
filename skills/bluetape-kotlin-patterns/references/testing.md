# Kotlin Testing and Infrastructure

Use for every new/touched Kotlin test, fixture, Testcontainers launcher, HTTP
adapter conformance suite, or HC5 factory.

## Assertions and Structure

- Use JUnit 5, MockK, `bluetape4k-assertions`, descriptive backtick names, and
  Given/When/Then structure.
- Migrate touched AssertJ/Kluent/JUnit/kotlin.test assertion blocks to
  bluetape4k assertions.
- Use `io.bluetape4k.assertions.assertFailsWith`; do not use JUnit
  `assertThrows`, AssertJ exception assertions, or `kotlin.test.assertFailsWith`.
- Prefer intent-specific matchers: Boolean/null/collection/array content and
  size matchers instead of generic equality or `!!` chains.
- Keep reusable mocks as class fields, reset with `clearMocks`, and use
  `coEvery`/`coVerify` for suspend functions.
- Use `confirmVerified` when strict interaction scope is part of the contract.

## Coroutines and Concurrency

- Use `runTest` for virtual time; use `runSuspendIO` or a real dispatcher for
  real IO, Testcontainers, and Ktor `testApplication`.
- JUnit expression-body tests using `runBlocking` explicitly return `Unit`.
- Use `untilSuspending` for suspend polling and `untilAsserted` otherwise.
- Use `MultithreadingTester` for thread/race stress,
  `StructuredTaskScopeTester` for structured/virtual-thread behavior, and
  `SuspendedJobTester` for suspend cancellation/stress when they fit.
- Before an ad hoc thread/coroutine stress harness, record why no ecosystem
  tester proves the risk.
- Cancellation tests exercise real job cancellation, cleanup, and propagation;
  do not construct manual continuations when `suspendCancellableCoroutine`
  expresses the behavior.

## Testcontainers and Shared Fixtures

- Reuse bluetape4k `XxxServer.Launcher` singletons; do not instantiate raw
  `GenericContainer` for already wrapped infrastructure.
- Shared fixtures expose SDK-neutral launchers, endpoint/credential properties,
  singleton/reuse policy, and bind/host-port verification when images/flags
  change.
- Container-backed tests normally stay out of daily smoke and run sequentially
  across modules, worktrees, and agents. Gradle BuildService mutexes do not
  serialize separate Gradle processes.
- For fresh proof, use `cleanTest --no-build-cache` when stale state can hide a
  failure. Classify network/container/sandbox errors with evidence before code
  changes; remove only verified Testcontainers residue.
- Test helper artifacts do not replace production helper dependencies when a
  test imports production extensions.

## HTTP and HC5

- Extend shared adapter conformance before backend-specific tests.
- Cover cancel-before-enqueue, in-flight cancellation, delayed body cleanup,
  timeout exposure, request tags, EOF/close, and cleanup semantics when exposed.
- Verify HC5 API placement from the actual dependency and test each factory
  overload's started/unstarted lifecycle contract.

## Verification

Run the smallest affected test first, then affected compile/test tasks. Record
command, expected/actual test count for matrix changes, and fresh results.
Testcontainers commands remain sequential. Run the full affected module test
before Kover XML; keep coverage report-only unless policy explicitly says
otherwise.

## Blocking Test Checklist

- [ ] **KT-TEST-01 — Use project test idioms**
  - **Action:** Apply JUnit 5, MockK, bluetape4k assertions, descriptive structure, and suspend-aware mocking/assertion APIs.
  - **Evidence:** Touched tests and assertion/mocking review.
  - **Failure:** Replace generic or incompatible touched-test idioms.
- [ ] **KT-TEST-02 — Prove concurrency and cancellation**
  - **Action:** Use the fitting ecosystem tester, virtual/real dispatcher, polling primitive, and real cancellation/cleanup path.
  - **Evidence:** Triggered stress/lifecycle tests or concrete risk-based N/A.
  - **Failure:** Document why no helper fits before any ad hoc harness; block fake cancellation proof.
- [ ] **KT-TEST-03 — Reuse safe infrastructure fixtures**
  - **Action:** Use launcher singletons, verify endpoints/reuse, serialize container work, and classify infrastructure failures from raw evidence.
  - **Evidence:** Fixture source, sequential command, fresh results, and residue decision.
  - **Failure:** Replace raw duplicate containers or investigate retry-only passes.
- [ ] **KT-TEST-04 — Cover HTTP lifecycle contracts**
  - **Action:** Extend conformance and test cancellation, timeout, body close/EOF, tags, cleanup, and HC5 started/unstarted semantics when exposed.
  - **Evidence:** Matrix cases and dependency-source verification, or concrete N/A.
  - **Failure:** Keep adapter/factory work blocked on missing lifecycle cases.
- [ ] **KT-TEST-05 — Run fresh targeted then module validation**
  - **Action:** Run the smallest affected test, affected compile/tests, full module test before Kover, and record matrix counts.
  - **Evidence:** Fresh commands, expected/actual counts, and report-only coverage result.
  - **Failure:** Do not accept stale cache output or run Kover before behavior proof.
