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
engines, spatial SQL or remote graph adapters, external provider adapters
(including broker request/response boundaries), external crypto/KMS or envelope
boundaries, observability hooks, Testcontainers readiness, benchmarks, or
public example/diagram evidence.

## Non-Negotiables

- Design Go-native narrow APIs; do not mechanically port Kotlin extensions.
- Prefer the standard library and repo helpers. New dependencies need explicit
  comparative evidence and approval.
- Logging is mandatory for production components with operational behavior.
  Record lifecycle transitions, external IO failures, retries/fallbacks, and
  terminal failures through caller-owned `log/slog`, an injected logger, or an
  explicit hook. Pure deterministic helpers and side-effect-free adapters that
  expose safe operation errors to a caller-owned observer are exempt from an
  internal logger; the adapter must not install global logging state or emit
  raw provider errors.
- Never use `fmt.Print*`, `log.Print*`, or direct stdout/stderr writes as
  operational logging. Use stable low-cardinality fields and never log secrets,
  credentials, tokens, or raw provider payloads.
- Specify success, failure, zero-value/nil, cancellation, timeout, cleanup, and
  error contracts where applicable.
- External provider adapters must inject the narrowest client surface, validate
  bounded request data before dispatch, preserve caller identity separately
  from provider-assigned IDs, classify transport and per-item responses
  deterministically, and let caller cancellation win at every response
  boundary. Provider messages and payloads stay out of public error strings;
  fake clients must deep-copy requests and prove malformed, partial, and
  cancellation responses without live credentials.
- For conditional key-value providers, model contention separately from
  transport ambiguity: a failed compare/condition is a normal no-write result,
  while a dispatched mutation error, malformed output, or output-plus-error is
  commit-unknown until an explicitly bounded, consistency-appropriate probe
  proves the owner/value state. Keep lease correctness in an absolute deadline
  field and treat provider TTL/expiry metadata as cleanup or retention hints
  only. Strictly parse Lua/SDK result shapes before decoding payloads, and never
  decode or publish a result after a response-time cancellation checkpoint.
  Preflight serialized writes and bound reads/CAS probes before handing bytes to
  a codec; use a narrow range/length check or equivalent provider primitive so a
  legacy oversized value cannot be fully materialized. Return a typed size error
  while preserving the existing value when the operation is non-destructive.
  Fakes must atomically emulate compare-and-set, capture deep-copied payloads and
  request metadata, and support output-plus-error plus late-cancellation cases.
- Observability SDKs (metrics, logs, traces, and audit sinks) use the same
  adapter discipline with one extra boundary: keep each signal's batching,
  ordering, cardinality, and deprecation rules explicit instead of inventing a
  shared publisher. Preflight documented service limits (item count, byte
  budget, dimensions/labels, event span, and finite numeric values) before the
  SDK call; never make raw payloads or high-cardinality values default
  log/metric fields. Compile-checked examples should inject fake method
  subsets, deep-copy captured requests, assert cancellation before dispatch and
  after a response, and prove provider diagnostics are redacted. If a service
  deprecates a sequencing token or allows parallel writes, document that
  current contract and test that stale serialization is not reintroduced.
  Configuration, credentials, retries, timeouts, global registries/loggers, and
  live endpoints remain caller-owned.
- External execution/polling adapters must define a finite wait budget or make
  the caller deadline explicit, bound and cancel timers/backoff, allowlist
  terminal statuses (including an unknown-status policy), and never stop or
  retry implicitly as a side effect of waiting cancellation. Fakes must prove
  delay/backoff sequencing, terminal failure mapping, timeout ownership, and
  no late response publication.
- Concurrent/shared-state claims require bounded stress evidence and
  `go test -race`; no-panic smoke tests are insufficient.
- A P0/P1 finding blocks the workflow. Reviews report P0/P1/P2/P3 with
  `file:line` evidence or explicit no-finding evidence.

### HTTP adapter boundaries and synchronous compatibility

- Check a nil downstream handler before parsing request data or invoking any
  parser, limiter, policy, or external dependency. Return the adapter's
  documented terminal response and prove the dependency call count is zero;
  do not let a framework default status hide a missing chain.
- Treat a response write error after the framework has committed the response
  as an observation boundary, not a retry signal. Preserve the committed
  response, never re-enter an outer error handler or issue a second write, and
  expose only a fixed low-cardinality redacted observer. Keep the caller-owned
  cause available through `errors.Is`/`errors.As` without including provider or
  transport text in the observer's public message. Custom callbacks own their
  own response and observation policy.
- Do not wrap a synchronous legacy provider in a goroutine merely to return on
  cancellation. Check context before and after the call, wait for a
  non-cooperative call to return, and make the lifecycle explicit in the
  migration contract. Add a context-aware method/interface for providers that
  can cooperate, and test pre-cancel, in-flight cancellation, late cancel,
  bounded completion, and zero detached goroutines.
- When a legacy configuration can carry a provider that also implements the
  context-aware interface, detect that capability once during adapter
  construction, preserve explicit context-aware option precedence, and route
  through the context method. Test auto-upgraded in-flight cancellation and
  reject any late-success result observed after the cancellation checkpoint.

### External crypto and envelope boundaries

- Keep cloud KMS credentials, client construction/close, retry policy, key
  policy, rotation, cache, and logging caller-owned. Inject the smallest SDK
  method subset needed by the Go package; document whether the injected client
  must support concurrent calls and cooperative `context.Context` cancellation.
- Reject a nil KMS client before any call, including a nil interface and typed
  nil values of every `reflect.IsNil`-capable kind (`Chan`, `Func`, `Interface`,
  `Map`, `Pointer`, and `Slice`). Prove no panic and zero provider calls for
  each kind, and keep the zero-value provider failure explicit.
- For a plaintext data-key response, if the SDK returns a non-nil output,
  reserve `defer zeroBytes(output.Plaintext)` immediately before checking the
  SDK error or plaintext length. For encrypted data-key responses, reserve the
  corresponding zeroing of `output.CiphertextBlob` and every local blob copy
  before validation or return. Zero SDK slices and every mutable local copy on
  success, error, cancellation, validation failure, and panic. Call this
  best-effort because Go copies, compiler/GC behavior, and expanded crypto keys
  cannot be promised to disappear.
- Define a canonical, versioned envelope encoding before implementation. Bind
  version, algorithm, key identity, encrypted data key, sorted context, and
  caller associated data to the local AEAD with an explicit domain and length
  encoding. Reject unknown/duplicate/case-variant fields, invalid UTF-8,
  non-canonical base64, trailing bytes, and oversized input before expensive
  KMS or crypto work. For map-like KMS encryption context, preserve keys and
  values byte-for-byte: matching is case-sensitive, `tenant` and `Tenant` are
  distinct, only exact duplicate keys are rejected, and no trim, case-fold, or
  Unicode normalization is implicit. Require deterministic field/array order,
  reject null/whitespace ambiguity, and prove byte-for-byte canonical
  re-marshal plus canonical padded-base64 round trips. Bound raw JSON string
  tokens before `json.Unmarshal`/canonical re-encoding; a decoded-size limit
  alone does not prevent allocation amplification from escape-heavy or giant
  source strings. When replacing a wire encoder, keep a fixed fixture produced
  by the prior writer and prove the new reader remains backward-compatible.
- Check cancellation before parsing or KMS, after each external response, and
  at the final result-publication boundary. Do not add a goroutine to force-stop
  a non-cooperative client; prove no local crypto or result publication occurs
  after a cancellation checkpoint fails.
- Fakes for external crypto must deep-copy request maps and byte slices, record
  logical method calls and observed contexts, support blocking/cancellation and
  output-plus-error cases, return fresh output buffers, and assert the provider
  never retains SDK-owned response slices. Assert metadata mismatch causes zero
  KMS calls. Add redaction tests (including `%+v`), bounded input tests,
  concurrent stress, race execution, and fake-only allocation benchmarks with
  fixture identity, environment, and logical call-count evidence; never treat
  live-cloud latency as a local benchmark. Public error values must also
  sanitize externally constructible sentinel/operation fields to the documented
  safe allowlist; test manual construction as well as internal wrapping.

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
- Keep reader-facing Go doc prose in Korean, but begin each exported declaration
  comment with the exact identifier followed by an ASCII space. Write
  `// Point 값은 ...` or `// NewPoint 함수는 ...`; a directly attached Korean
  particle such as `// Point는 ...` fails `revive`'s exported-comment rule. Run
  the configured linter after the first public declaration so the defect does
  not spread across a new package.
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
  - **Action:** Use standard/repo helpers, `%w`, deterministic cleanup/timeouts/shutdown, caller-owned keys, mandatory operational logging, and synchronized per-run state.
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
