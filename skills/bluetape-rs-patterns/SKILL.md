---
name: bluetape-rs-patterns
description: Use when implementing, planning, reviewing, testing, packaging, or releasing Rust code in bluetape-rs or another bluetape ecosystem Rust repository.
---

# bluetape-rs Patterns

When used inside a bluetape workflow, the parent owns Step DoD, approvals,
GitHub metadata, and side effects. This skill owns Rust-specific API, async,
Cargo, SQL, testing, and P0/P1 rules.

## Non-Negotiables

- Keep APIs Rust-native with explicit ownership, narrow traits, typed
  config/builders, and small crate/module boundaries.
- Use Rust 2024 unless a documented compatibility constraint applies.
- Public APIs need English Rustdoc and success/error/boundary/feature tests.
- Match sibling `lib.rs`/README style. Keep `lib.rs` focused; roadmap, issue
  history, long guides, and non-goal lists belong in README/spec/plan docs.
- Preserve typed errors and `source()`; do not stringify caller-visible causes.
- Avoid `unsafe`; isolate and document invariants plus safe-boundary tests when
  unavoidable.
- Feature flags are additive and heavy integrations are opt-in by default.
- Tokio is the default async runtime; move blocking work behind an explicit
  `spawn_blocking`-style boundary.
- P0/P1 blocks progression. Reviews report P0/P1/P2/P3 with `file:line`.

## P0/P1 Gate

### P0

- memory unsafety, UB, unsound `unsafe`, or invalid `Send`/`Sync`;
- data race, deadlock, unbounded task/thread/resource growth, or task leak;
- auth/trust bypass, secret leak, injection, unsafe deserialization, or SQL
  injection;
- silent data loss, duplication, corruption, or misordering;
- version/tag/changelog mismatch publishing the wrong/unreproducible crate.

### P1

- error contract loses typed cause/`source()`, returns ambiguous success/none,
  or panics on caller input;
- cancellation/shutdown/backpressure/timeout/retry ownership is missing or
  blocking work runs on core async tasks;
- connection, transaction, stream, file, timer, task, worker, or container not
  closed/aborted on every path;
- broad/JVM-shaped/lifetime-hostile/duplicative public API;
- global/interior mutable state, cache, once cell, lock, or atomic without clear
  ownership, ordering, and concurrency proof;
- non-additive/default-heavy feature flags or broken all-features workspace;
- tests omit error/boundary/cancellation/concurrency/type-level proof;
- SQL mixes text and values, lacks transaction semantics, or claims real DB
  support without container-backed evidence;
- FFI/serde/crypto/network/filesystem boundary lacks validation and hostile
  input tests.

## Spec and Plan Gate

Verify ownership/lifetimes, public error variants/source chain, runtime/task
lifecycle, cancellation/timeout/backpressure/shutdown, blocking boundary,
shared-state/lock/channel/atomic ownership, additive feature matrix, and tests.

SQL plans keep SQL text and bind values separate, define dialect rendering and
transaction semantics, and include SQLx/Testcontainers PostgreSQL proof. New
crate plans compare at least two sibling `src/lib.rs` and README pairs before
choosing documentation placement.

## Implementation Defaults

- Run `cargo fmt --all`.
- Prefer `#[must_use]` where ignored results are bugs and `#[non_exhaustive]`
  where public values may grow compatibly.
- Return typed errors for caller input; reserve panic for impossible internal
  invariants/tests.
- Avoid production `unwrap`/`expect` unless a local invariant is obvious and
  documented.
- Prefer simple owned values when lifetime-heavy generics do not buy real
  ergonomics.
- Use `tokio::time`, explicit shutdown signals, and tested `JoinHandle`
  join/abort policy.
- Prefer ownership transfer; use locks/atomics/channels only with an explicit
  lifecycle and contention model.
- For SQL, start with inspectable AST/dialect renderer plus adapter. Do not claim
  ORM behavior before relations, migrations, transactions, and lifecycle exist.

## Testing and Validation

## Mandatory Rust Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **RS-01 — Pin crate and feature boundaries**
  - **Action:** Classify touched crates/modules, Rust compatibility, public API/docs, additive feature matrix, external integrations, SQL, and release authority when applicable.
  - **Evidence:** Crate/feature map, sibling style anchors, public surface, non-goals, and exact release identity fields.
  - **Failure:** Block planning or publication on ambiguous crate, feature, or target boundaries.
- [ ] **RS-02 — Define ownership and failure contracts**
  - **Action:** Specify lifetimes/ownership, typed errors/source chain, task/resource lifecycle, cancellation/timeout/backpressure/shutdown, blocking boundary, shared-state model, and tests.
  - **Evidence:** Spec/plan mapping to success, error, boundary, feature, type-level, lifecycle, and contention proof.
  - **Failure:** Reject panicking caller paths, JVM-shaped APIs, or unowned runtime state.
- [ ] **RS-03 — Implement safe Rust-native behavior**
  - **Action:** Preserve typed errors, isolate unavoidable unsafe, use explicit async shutdown/join/abort, favor ownership transfer, and separate SQL text from values.
  - **Evidence:** Scoped diff with invariants, cleanup paths, bind semantics, and dependency/tool rationale.
  - **Failure:** Record P0/P1 for unsoundness, leaks, lost causes, injection risk, or ambiguous lifecycle.
- [ ] **RS-04 — Prove behavior and type contracts**
  - **Action:** Run focused unit/integration/Tokio tests, compile-fail checks when applicable, bounded concurrency stress, and hostile-input tests at exposed boundaries.
  - **Evidence:** Fresh targeted results tied to every touched contract.
  - **Failure:** Smoke-only or panic-free evidence does not satisfy ownership, concurrency, or type claims.
- [ ] **RS-05 — Prove feature and external integration matrices**
  - **Action:** Run workspace/all-features validation for public/feature changes and serial Testcontainers/SQLx proof for real integrations.
  - **Evidence:** Feature matrix commands/results and real-service lifecycle/transaction evidence, or concrete N/A.
  - **Failure:** Block default-heavy/non-additive features or unproved real-DB claims.
- [ ] **RS-06 — Run the fresh validation ladder**
  - **Action:** Run diff check, fmt, targeted tests, workspace tests, triggered all-features/clippy, and targeted integration/container checks.
  - **Evidence:** Fresh successful commands or exact unrelated blocker plus strongest unaffected proof.
  - **Failure:** Do not issue PASS from stale, partial, or unexplained missing validation.
- [ ] **RS-07 — Render the Rust verdict**
  - **Action:** Report scope/baseline, commands, file:line findings, gaps, feature/release state, and parent DoD counts.
  - **Evidence:** X=Y, Blocked=0, exact P0=0/P1=0 for PASS.
  - **Failure:** Expose unchecked rows and blocking findings instead of declaring completion.

- focused unit tests for pure logic; integration tests for runtime/IO;
- `#[tokio::test]` for Tokio semantics;
- `trybuild`/compile-fail for macro, trait-bound, or type-level contracts;
- property/loom-style tooling only when already accepted or justified;
- Testcontainers for real external integrations, executed serially when state
  or ports can interfere;
- bounded stress tests for concurrent contracts.

Run the smallest proving set, then expand:

1. `git diff --check` and `cargo fmt --all --check`;
2. targeted `cargo test -p <crate> [test]`;
3. `cargo test --workspace`;
4. `cargo test --workspace --all-features` for public/feature changes;
5. `cargo clippy --workspace --all-targets --all-features -- -D warnings`
   when the repository baseline supports it;
6. targeted compile-fail/integration/container checks.

If broader validation is blocked by an unrelated baseline/environment failure,
record the exact error and run the strongest unaffected targeted/workspace
commands.

## Review Output

Report reviewed diff/baseline, evidence commands, findings with `file:line`,
exact `P0=<n> P1=<n>`, verdict, and gaps. PASS requires P0=0 and P1=0.
