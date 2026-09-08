# Kotlin Retry, Cache, and Transaction Boundaries

Use for retry queues, incremental streams, cached reads, and transactional side
effects. Load `lifecycle.md` when cancellation or shutdown intersects them.

## Retry and Replay

- When retry metadata belongs to each entry, derive its next count, sequence,
  deadline, and version from that entry. Do not reuse a batch representative's
  state. Test mixed retry histories and competition with newly arriving entries.
- Preserve the documented ordering and same-key conflict policy across retries;
  pushing an entire failed batch to the front is not proof. Cover capacity,
  dead-letter/exhaustion, cancellation, and shutdown paths that can lose entries.
- Retrying after a stream has emitted items or an operation has committed can
  duplicate visible effects. Define the replay boundary and idempotency/resume
  policy; do not disable safe pre-effect or idempotent retries globally.

## Cache Invalidation

- Prevent an in-flight miss from repopulating invalidated data after a write.
  Capture a generation/version before reading and make the check-and-store
  atomic with respect to invalidation, or prove an equivalent ordering scheme.
- Cover successful write, drop, and transaction commit paths with appropriate
  invalidation. Preserve rollback behavior according to the cache contract.
  Delegation syntax alone does not prove optional capabilities are intercepted.
- Test miss-start -> write/invalidate -> miss-finish. Returning an older value
  to the already-started caller may be allowed; stale cache reinsertion is a
  separate failure. State whether external writes through other instances are
  outside the wrapper's invalidation guarantees.

## Transaction Effects

- Keep source state and required audit state inside the same atomic boundary
  when the backend supports it; distinguish post-commit best-effort publication.
- Document guarantees by backend and operation. Redis MULTI/EXEC is not database
  rollback, and a shared interface does not make all adapters equally atomic.
- Recognize backend conditions through typed errors/codes and established
  helpers; do not infer duplicate/conflict semantics from message substrings.

## Blocking Data Checklist

- [ ] **KT-DATA-01 — Preserve retry state and replay boundaries**
  - **Action:** Test mixed per-entry histories, same-key ordering, new arrivals, exhaustion, and retry after visible effects where touched.
  - **Evidence:** Deterministic queue/partial-stream tests and explicit replay policy, or concrete N/A.
  - **Failure:** Block batch-state contamination, lost entries, or unintended duplicate effects.
- [ ] **KT-DATA-02 — Prevent stale cache reinsertion**
  - **Action:** Trace invalidation through write/drop/commit and prove miss completion cannot store across the invalidation boundary.
  - **Evidence:** Controlled overlap tests, atomic ordering proof, rollback semantics, and external-write scope.
  - **Failure:** Reject check-then-store races or delegation-only invalidation claims.
- [ ] **KT-DATA-03 — State actual transaction guarantees**
  - **Action:** Separate atomic writes, rollback behavior, post-commit effects, and backend error classification.
  - **Evidence:** Failure-injection tests tied to each supported backend contract, or concrete N/A.
  - **Failure:** Reject universal rollback claims or post-commit failures presented as an uncommitted write.
