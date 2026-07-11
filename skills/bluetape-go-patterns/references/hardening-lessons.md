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
