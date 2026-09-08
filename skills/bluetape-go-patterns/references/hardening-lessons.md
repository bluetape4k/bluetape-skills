# bluetape-go Hardening Lessons

Load only for the advanced domains named by `SKILL.md`.

## Release and Workflow Proof

- Verify issue/PR milestone and assignee before implementation/merge gates.
- Never create or push a release tag until its commit contains the matching
  `CHANGELOG.md` section and live milestone/open-PR state is checked.
- Keep raw benchmark evidence, environment, dirty-tree note, metric direction,
  deterministic case order, and pre-timer correctness validation.

## Selective Parity and Dependencies

- A Kotlin match alone is not a Go use case. Record keep/adapt/replace/split,
  defer, or non-goal and implement only the Go-native slice with real call-site
  evidence.
- For AWS, SQL, text, image, geo, statistics, money, or crypto, decide package
  boundary, maintenance/license/native lifecycle, examples, and validation
  before adding a dependency.
- Do not rewrite downstream packages merely to showcase a new helper.

## Input and Compatibility Contracts

- Exported concrete values are safely zero-value usable or constructor-only by
  an enforced documented contract.
- Generic/Redis/cache keys preserve caller values unless canonicalization is
  explicit and collision-tested.
- Compact encoders and text/locale/currency helpers reject oversized input
  early and reject aliases by canonical round-trip/re-encoding where promised.
- Document byte-preserving versus numeric/text normalization semantics.

## External Provider Adapters

- Keep SDK/client construction, credentials, retry/backoff, timeout, metrics,
  logging, and downstream deduplication caller-owned. Inject only the provider
  method subset the adapter actually calls.
- Bound and validate request bytes before dispatch, including provider metadata
  overhead; reject malformed input without a provider call. Preserve stable
  caller identity independently from provider-assigned receipt IDs.
- Treat transport success and item-level success as separate contracts. Map
  nil/malformed output, partial failures, and missing success identifiers to
  deterministic typed errors while keeping provider messages out of public
  formatting. Check caller cancellation before dispatch and after every
  provider response so late success cannot mask shutdown.
- Fake external clients must deep-copy requests, record logical calls and
  contexts, support blocking/cancellation and output-plus-error cases, and
  prove no live credentials or endpoint are needed for normal, malformed,
  partial, and cancellation tests.

## Spatial SQL and Remote Graph Boundaries

- Keep spatial SQL in engine-specific packages when SRID, axis order, distance
  units, constructor functions, or index predicates differ. Preserve explicit
  SRID in the wire value (for example EWKB) and validate finite coordinates,
  bounds, identifiers, and distance before dispatch. Do not hide engine
  semantics behind a minimum-common-dialect abstraction without real call sites.
- For MySQL geographic SRS, make the intended axis order explicit in every
  constructor and reader query. For MariaDB and other drivers whose binary
  bind representation is ambiguous, use an engine-native binary boundary and
  prove point round-trip, distance, and bounding-box/index behavior against the
  real engine fixture.
- Remote graph adapters must bound rows, columns, nested result expansion, and
  serialized parameters before materializing caller-visible values. Validate
  map keys and endpoint shapes, copy mutable provider data, and reject malformed
  or output-plus-error responses deterministically. A result limit on the outer
  channel alone is not a bound if one item can contain an unbounded nested list.
- Treat remote-driver cancellation claims literally. If the chosen API lacks
  `context.Context` or server-side cancel, check context before dispatch and at
  every result/publish checkpoint, close the local stream deterministically, and
  document that the server traversal may continue. Never close a caller-owned
  shared client merely to force cancellation of one operation.
- Pin Testcontainers image references with a digest, prove readiness through a
  protocol-level check, and serialize Docker-backed suites when ports or
  resources overlap. A missing local image, mutable tag, or skipped integration
  test is an evidence gap, not a passing fixture proof.

### Conditional key-value and cache primitives

- Separate conditional miss/contention from provider failure. A conditional
  write that did not match is a normal `(false, nil)`-style outcome; a mutation
  error, malformed command/result, or output-plus-error after dispatch is
  commit-unknown until a bounded probe with appropriate read consistency proves
  the state. Do not retry caller cancellation as contention.
- Store correctness deadlines in an absolute field with an explicit unit (for
  example epoch milliseconds). Provider TTL/retention metadata is a cleanup
  hint, not the ownership or freshness signal; round it conservatively so
  asynchronous cleanup cannot remove an active lease/value early.
- Treat Lua result shapes as a wire contract. Accept only documented
  status/payload arity and types, copy returned bytes before handing them to a
  serializer, and reject malformed/partial results without decoding. Check
  context immediately before dispatch and after every command response.
- Bound both sides of a value boundary: reject serialized writes before
  dispatch, and use a range/length check or equivalent narrow read before
  materializing a stored value or passing it to a codec. An oversized legacy
  value must produce a typed size error without replacement/deletion unless the
  API explicitly says otherwise; test the key-preservation invariant.
- A conditional-cache fake must hold state under one mutex while evaluating
  CAS/SETNX, deep-copy request payloads and metadata, and expose configured
  output-plus-error and late-cancellation paths. Race evidence must assert exact
  winner counts, not merely that the test avoids a panic.

## External Execution and Polling

- Keep long-running execution observation caller-bounded: require an explicit
  wait timeout or a documented caller deadline, use cancellable timers rather
  than uninterruptible sleeps, cap custom backoff, and treat only an explicit
  terminal-status allowlist as completion. Unknown statuses must fail closed or
  follow a documented compatibility policy; waiting must not implicitly stop,
  retry, or publish a result after caller cancellation.

## Cancellation and Concurrent Primitives

- Return caller cancellation/deadline without retrying it and prove no late
  write, stale reader, leaked key/waiter, or goroutine remains.
- Cyclic, ordered, goroutine-safe, no-lost-update, collapse, lock-owner,
  rate-limit, or rotation claims require exact totals/order/owner/side-effect
  assertions under contention.
- Distributed coordination documents owner token, lease expiry, over-TTL
  overlap, cleanup, and failure injection.

## Rule Engines

- Return an error if any rule fails even when execution continues.
- Keep per-run composite selection local to `Execute`; typed errors fail closed
  if child predicates drift.
- Bounded inference requires a positive max-cycle guard, typed non-convergence,
  and explicit in-place/non-transactional `Facts` semantics.
- Do not combine inference with skip-later options that can report false
  convergence.

## Observability, Containers, and Evidence

- Keep logging package-local and caller-owned; no global registry or MDC-shaped
  API. Guard expensive debug attributes, sample high-volume success, and avoid
  raw/high-cardinality provider errors by default.
- Serialize shared Docker-backed suites. Prove connection, cleanup,
  cancellation, and injected failure; container log readiness is insufficient.
- Package READMEs own behavior/caveats/commands/benchmarks; root README is an
  index. Public examples should be compile-checked.
- README diagrams need paired source/rendered assets and full-size PNG review;
  generation success alone is not visual evidence.

## Blocking Hardening Checklist

- [ ] **GO-HARD-01 — Prove release and benchmark identity**
  - **Action:** Verify live issue/PR metadata, changelog/tag commit alignment, benchmark environment, raw evidence, direction, ordering, and pre-timer correctness when triggered.
  - **Evidence:** Live metadata/SHAs and reproducible benchmark ledger, or concrete N/A.
  - **Failure:** Block release or performance claims on mismatched or incomplete identity.
- [ ] **GO-HARD-02 — Justify parity and dependencies**
  - **Action:** Classify source parity and evaluate package boundary, maintenance, license, native lifecycle, examples, and tests before dependency adoption.
  - **Evidence:** Keep/adapt/replace/split/defer/non-goal decision and comparative evidence.
  - **Failure:** Reject Kotlin-only rationale or showcase-driven rewrites.
- [ ] **GO-HARD-03 — Preserve input and compatibility contracts**
  - **Action:** Verify zero values, caller keys, canonical collision handling, size rejection, round trips, and normalization semantics.
  - **Evidence:** Contract tests for every touched encoder/key/value behavior.
  - **Failure:** Treat collisions, aliases, unsafe zero values, or undocumented normalization as P1.
- [ ] **GO-HARD-04 — Prove cancellation and coordination**
  - **Action:** Test caller cancellation/deadline, no late side effects, exact contention outcomes, owner tokens, lease overlap, cleanup, and failure injection.
  - **Evidence:** Race/stress and lifecycle results with exact totals/order/ownership.
  - **Failure:** Block claims on leaks, stale artifacts, lost updates, or retrying caller cancellation.
- [ ] **GO-HARD-05 — Fail rule engines closed**
  - **Action:** Verify child failures propagate, per-run state is local, cycle bounds are positive, non-convergence is typed, and fact mutation semantics are explicit.
  - **Evidence:** Failure, concurrency, and non-convergence tests.
  - **Failure:** Block false success/convergence behavior.
- [ ] **GO-HARD-06 — Verify observability and public evidence**
  - **Action:** Keep logging caller-owned/guarded/low-cardinality, serialize containers with connection proof, compile public examples, and visually review paired diagram assets.
  - **Evidence:** Logging tests/review, service results, example tests, and diagram ledger/full-size PNG review.
  - **Failure:** Generation or log readiness alone is not completion evidence.
- [ ] **GO-HARD-07 — Harden external provider adapters**
  - **Action:** Verify narrow client injection, pre-dispatch byte bounds, caller-owned identity, transport/item response mapping, cancellation priority, and provider-message redaction.
  - **Evidence:** Fake request copies/context traces, malformed/partial/output-plus-error/cancellation tests, and a no-live-credentials review.
  - **Failure:** Provider-assigned IDs replacing caller identity, unbounded dispatch, ambiguous partial success, leaked provider text, or cancellation masked by a late response is P1.

- [ ] **GO-HARD-08 — Bound external execution polling**
  - **Action:** Verify explicit wait/deadline ownership, cancellable bounded timers, capped backoff, terminal-status allowlist and unknown-status policy, no implicit stop/retry, and no late result after cancellation.
  - **Evidence:** Fake call sequence and delay assertions, timeout/cancellation/terminal-failure tests, race/resource review, and documented caller stop ownership.
  - **Failure:** Unbounded polling, uncancellable sleep, unknown status reported as success, implicit side effect, or late publication is P1.
