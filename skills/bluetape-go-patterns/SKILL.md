---
name: bluetape-go-patterns
description: Use when implementing, planning, reviewing, or releasing Go code in bluetape-go, bluetape-go-workshop, or another bluetape ecosystem Go module.
---

# bluetape-go Patterns

## Parent and Reference Routing

When used inside a bluetape workflow, the parent owns Step DoD, approvals,
GitHub metadata, and side effects. This skill owns Go-specific implementation
and P0/P1 review rules.

Load `references/hardening-lessons.md` only when work touches release proof,
source parity, distributed cache/lock/rate limiting, canonical encoders, rule
engines, observability hooks, Testcontainers readiness, benchmarks, or public
example/diagram evidence.

## Non-Negotiables

- Design Go-native narrow APIs; do not mechanically port Kotlin extensions.
- Prefer the standard library and repo helpers. New dependencies need explicit
  comparative evidence and approval.
- Specify success, failure, zero-value/nil, cancellation, timeout, cleanup, and
  error contracts where applicable.
- Concurrent/shared-state claims require bounded stress evidence and
  `go test -race`; no-panic smoke tests are insufficient.
- A P0/P1 finding blocks the workflow. Reviews report P0/P1/P2/P3 with
  `file:line` evidence or explicit no-finding evidence.

## P0/P1 Gate

### P0

- data race, deadlock, goroutine/resource leak, or unbounded growth capable of
  corrupting state or exhausting/hanging production;
- auth/authz/trust-boundary bypass, secret exposure, unsafe deserialization,
  command/path injection;
- silent data loss, duplication, or corruption;
- tag/changelog/commit mismatch that publishes the wrong module version.

### P1

- incorrect `context.Context` propagation, deadline, timeout, shutdown, or
  retry behavior; never retry caller-owned cancellation without a proven spec;
- response body, rows, transaction, file, timer/ticker, goroutine, or container
  not closed on every path;
- error wrapping that breaks `errors.Is`/`errors.As`, hides typed/sentinel
  errors, or returns ambiguous nil;
- broad/Kotlin-shaped/duplicative API, or exported concrete type with unsafe
  undocumented zero value;
- lossy/colliding key conversion, undocumented normalization, hidden lease or
  owner-token semantics, or non-canonical compatibility decoding;
- cancellation that returns while leaving a late write, stale cache hit,
  retained waiter/key, or coordination artifact;
- reusable rule/policy values holding unsynchronized per-run state or reporting
  convergence/success after failed child work;
- global logger state, raw provider-error logging, blocking/high-volume hooks
  without guards/sampling, or high-cardinality defaults;
- tests lacking failure/cancellation/cleanup/race proof for the claimed risk;
- HTTP boundary without owned timeouts, body limits/closing, status mapping, or
  proxy trust notes;
- CI/release lane omitting configured checks, required metadata, changelog/tag
  proof, or safe serialization of integration suites.

## Spec and Plan Gate

Before implementation verify:

- API shape, zero-value/factory behavior, explicit errors, and non-goals;
- context owner for IO, retries, fanout, backoff, workers, and shutdown;
- goroutine/channel close owner, synchronization, and cleanup path;
- table-driven success/failure plus cancellation/timeout and stress/race tests;
- compile-checked `Example...` tests for public usage contracts;
- caller-owned key/canonicalization, lease expiry, and side-effect semantics for
  distributed primitives;
- release target commit, matching changelog, milestone/assignee, and open PRs
  when release work is in scope.

Source parity plans must classify candidates as keep/adapt/replace/split/defer
or non-goal. JVM futures/executors/virtual-thread facades, broad Commons-style
wrappers, global logging facades, and helper packages without repeated Go call
sites are default non-goals.

## Implementation Defaults

- Format touched files with repo tooling/`gofmt`.
- Use table-driven tests and compile-checked examples.
- Wrap causal errors with `%w`; preserve typed/sentinel inspection.
- Close owned resources deterministically.
- Use explicit client/server timeouts where the package owns them.
- Use `context.Context` and deterministic shutdown for workers; use `errgroup`
  only when already accepted or justified.
- Prefer `slices`, `maps`, `iter`, and small repo helpers over new abstractions.
- Preserve caller keys and document lease/TTL overlap for distributed helpers.
- Keep reusable execution state local to one call or explicitly synchronized.
- Keep logging caller-owned (`log/slog`, injected logger, explicit hook),
  guarded, sampled where needed, and low-cardinality.

## Validation

## Mandatory Go Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **GO-01 — Classify scope and load hardening triggers**
  - **Action:** Identify touched packages, public/release surfaces, concurrency/resources, and advanced domains; load hardening lessons for every matching trigger.
  - **Evidence:** Scope and trigger-to-reference map.
  - **Failure:** Keep planning/review blocked until triggers are classified.
- [ ] **GO-02 — Approve a Go-native contract**
  - **Action:** Define API/zero-value/errors/non-goals, context ownership, goroutine/channel close ownership, cleanup, and distributed side effects before implementation.
  - **Evidence:** Spec/plan mapping with source-parity classification and real call-site anchors.
  - **Failure:** Reject mechanical ports, broad wrappers, or unowned lifecycle behavior.
- [ ] **GO-03 — Implement with ownership and compatibility**
  - **Action:** Use standard/repo helpers, `%w`, deterministic cleanup/timeouts/shutdown, caller-owned keys/logging, and synchronized per-run state.
  - **Evidence:** Scoped diff mapped to the approved contract and explicit raw/dependency rationale.
  - **Failure:** Record P0/P1 and block progression on unsafe or ambiguous ownership.
- [ ] **GO-04 — Prove normal and failure behavior**
  - **Action:** Run formatting, lint/config, fresh package tests, examples, and failure/cancellation/cleanup cases.
  - **Evidence:** Fresh commands/results and compile-checked examples when public usage changes.
  - **Failure:** Do not issue PASS from smoke-only or stale evidence.
- [ ] **GO-05 — Prove concurrent claims**
  - **Action:** For shared state, workers, retry, timeout, cache, fanout, or uniqueness, run race plus bounded stress with exact outcome assertions.
  - **Evidence:** `go test -race` and stress outputs, or concrete risk-based N/A.
  - **Failure:** No-panic evidence is insufficient; keep the claim blocked.
- [ ] **GO-06 — Verify integration and release surfaces**
  - **Action:** Serialize real services, prove connection readiness, run make/CI when defined, and complete triggered release/docs/diagram rows.
  - **Evidence:** Service and CI results plus reference checklist counts, or concrete exclusions.
  - **Failure:** Log readiness, missing configured checks, or unverified public evidence blocks completion.
- [ ] **GO-07 — Render the Go verdict**
  - **Action:** Report reviewed diff/baseline, commands, file:line findings, gaps, counts, and parent DoD.
  - **Evidence:** X=Y, Blocked=0, exact P0=0/P1=0 for PASS.
  - **Failure:** Expose unchecked rows and severity findings instead of declaring PASS.

Run the smallest proving set, then expand by blast radius:

1. `git diff --check` and formatter;
2. configured lint/config verification;
3. `go test -count=1 ./<pkg>`;
4. `go test -race -count=1 ./<pkg>` for changed packages with concurrency,
   shared state, cache, worker, retry, timeout, uniqueness, or fanout risk;
5. bounded stress test under normal and race execution for concurrent claims;
6. `go test -run Example -count=1 ./<pkg>` for examples/README API changes;
7. `make ci` and GitHub checks when defined/in scope.

Run Testcontainers/real services serially and prove connection readiness rather
than log readiness. If broader tests are blocked by an unrelated failure, record
the exact package/error and run the strongest unaffected targeted/repo command.

## Review Output

Report reviewed diff/baseline, evidence commands, findings with `file:line`,
exact `P0=<n> P1=<n>`, verdict, and verification gaps. PASS requires P0=0 and
P1=0.
