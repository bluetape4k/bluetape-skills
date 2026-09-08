# Kotlin Cancellation and Resource Lifecycle

Use when changing cancellation, timeout, async completion, cleanup, or resource
ownership. Load `testing.md` for deterministic proof.

## Cancellation and Deadlines

- Rethrow caller cancellation before retry, fallback, error callbacks, or
  failure-checkpoint writes. Translate only the timeout owned by the current
  operation; an outer caller deadline remains cancellation.
- `Dispatchers.IO` relocates blocking work; it does not promise interruption.
  Use `runInterruptible` only for interrupt-cooperative APIs, or the driver's
  cancellation hook when supported. State remaining driver/vendor limits.
- Keep `NonCancellable` limited to required cleanup. Define a cleanup deadline
  or grace policy separately from the operation deadline; a coroutine timeout
  cannot force a non-cooperative close or JDBC call to stop.
- Preserve the primary failure when rollback, close, metrics, or logging also
  fail. Attach safe secondary diagnostics where the boundary allows it;
  telemetry must not turn a committed transaction into an apparent failure.
  Do not leak secrets through secondary exceptions.
- Separate adapter-owned behavior from upstream behavior. Characterize the
  pinned upstream version's swallowed cleanup failures rather than recovering
  them by parsing logs or copying its transaction implementation.

## Ownership and Completion

- Record who creates, closes, and can share each resource. Close library-owned
  resources once; leave caller-owned resources open unless ownership transfer
  is explicit. Cover partial acquisition, late registration, and failed startup.
- Preserve lifecycle phases when adopting a shared registry: flush/drain before
  shutdown and final close after shutdown can require different hooks. Retain
  documented ordering and retry-after-failed-close behavior.
- Distinguish claiming cleanup once from observing cleanup completion. Use a
  shared completion signal when concurrent closers or waiters must join.
- When the API promises release before ordinary success/failure completion,
  join acquisition/cleanup before terminalizing, including pre-action executor
  rejection. Cover cancellation racing with acquisition and scheduler failure;
  unexpected scheduling exceptions must not strand the result.
- Do not fall back to blocking cleanup on an action-completion/event-loop
  thread. Bound fallback execution and preserve the result's failure policy.
- Preserve standard `Future.cancel()` immediate terminal behavior. Test eventual
  cleanup separately; do not make every cancelled future wait for release.

## Blocking Lifecycle Checklist

- [ ] **KT-LIFE-01 — Prove cancellation and deadline ownership**
  - **Action:** Trace caller cancellation, owned timeout conversion, blocking API support, and separate cleanup grace policy.
  - **Evidence:** Real cancellation tests and driver limits; no retry/failure side effect after cancellation.
  - **Failure:** Reject dispatcher-only cancellation claims or swallowed outer deadlines.
- [ ] **KT-LIFE-02 — Prove ownership and completion ordering**
  - **Action:** Map resources and phases; test partial acquisition, scheduler rejection, concurrent close, and promised cleanup-before-completion paths.
  - **Evidence:** Barrier tests, close counts, shared completion proof, and separate Future.cancel eventual-cleanup proof where applicable.
  - **Failure:** Repair orphaned resources, blocked completion threads, or stranded results; preserve documented caller-owned and cancellation contracts.
- [ ] **KT-LIFE-03 — Preserve the primary outcome**
  - **Action:** Inject cleanup/metrics failure after primary failure and after commit; characterize upstream limitations separately.
  - **Evidence:** Primary outcome, safe secondary diagnostics, and version-pinned characterization or concrete N/A.
  - **Failure:** Block secondary-failure replacement, secret leakage, and unproven upstream guarantees.
