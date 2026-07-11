# Step 6-R Code Review Prompts

Use this reference from `bluetape-full-feature` Step 6-R before PR creation.

## Module-Slice Strategy

When the branch spans multiple bluetape4k modules, run Step 6-R **per module slice** — not once at the aggregate level. Review in dependency order (core before adapters).

Each slice must produce:
- Six perspective-lane findings table with P0/P1/P2/P3 counts
- Current-session integration result
- Final `P0 = 0, P1 = 0` convergence record

Record the baseline P0/P1 list, each review iteration result, and the final gate as an explicit PR artifact (in the PR body or PR comment). Do not keep it as a private review state.

## Tier 1: Performance Review

Use `verifier`, `critic`, `code-reviewer`, or local review with this prompt.

```text
Review the branch diff from a performance perspective.

Focus:
1. Apply `performance-stability-scan.md` to the current diff.
2. Verify benchmark, stress, or race-test evidence for performance claims.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
If not applicable, record N/A with reviewed scope and reason.
```

## Tier 2: Stability Review

Use `verifier`, `critic`, or local review.

```text
Review the branch diff from a runtime stability perspective.

Focus:
1. Apply `performance-stability-scan.md` to the current diff.
2. Verify backend recovery and Testcontainers/integration stability evidence.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
```

## Tier 3: Security Review

Use `code-reviewer` with the security lens. Use `verifier` only for supporting
evidence or a documented main-session fallback.

```text
Review the branch diff for changed Kotlin, Go, Rust, and configuration files.

Focus:
1. OWASP Top 10 risks.
2. Secrets, credentials, key material, and unsafe defaults.
3. SQL/NoSQL injection and unsafe deserialization.
4. Auth/authz boundary gaps and algorithm confusion.
5. User-controlled input validation and tenant/namespace separation.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
```

## Tier 4: Operator/Ops Review

Use `verifier` with the stability/Ops lens, or a documented main-session
fallback.

```text
Review the branch diff from an operator/Ops perspective.

Focus:
1. Logging, metrics, tracing, and useful diagnostic context.
2. Health/readiness, startup, graceful shutdown, and resource ownership.
3. Configuration, namespace/key format, migration, rollback, and runbook clarity.
4. Release readiness and operational verification evidence.
5. Failure diagnosis without leaking sensitive data.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
```

## Tier 5: Developer/API Review

Use native `code-reviewer`; add `architect` or `test-engineer` only for a
triggered architecture or test-strategy lens.

```text
Review changed Kotlin, Go, and Rust files from a developer/API perspective.

Focus:
1. Public API compatibility, module boundaries, dependency direction, inheritance, extension, and interface contract changes.
2. Kotlin idioms, null-safety, validation helpers, value classes, sealed classes, DSL design, coroutine correctness, dispatcher boundaries, and Flow semantics.
3. `bluetape-kotlin-patterns`, `bluetape-go-patterns`, and `bluetape-rs-patterns` compliance.
4. Go context propagation, error wrapping, goroutine/resource cleanup, race/leak risk, HTTP trust boundaries, and API placement.
5. Rust ownership/lifetime/API shape, typed errors, async cancellation/shutdown, resource cleanup, feature flags, unsafe boundaries, and SQL bind separation.
6. Public API KDoc/Rustdoc/docs consistency, deprecations, SOLID/DRY, and maintainability.
7. Test names, assertions, error expectations, silent-failure paths, and over-wide same-type parameter surfaces.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
```

### Production Concurrency Quick Scan (Tier 5)

Run against `src/main/kotlin`, Go package roots, and Rust crate roots before declaring Tier 5 clean:

```bash
rg "GlobalScope|runBlocking\(|Thread\.sleep|delay\(|synchronized\(|@Synchronized|runCatching\s*\{" src/main/kotlin
rg "unsafe|unwrap\\(|expect\\(|panic!|todo!|unimplemented!|std::thread::spawn|tokio::spawn|spawn_blocking|Mutex|RwLock|Atomic|static mut" crates src tests
rg "context\\.TODO\\(|context\\.Background\\(|go func|time\\.Tick\\(|http\\.ListenAndServe\\(|panic\\(|RealIP|X-Forwarded-For" .
```

Document each hit as: intentional (adapter, lifecycle), known limitation, or P1/P0 finding. A zero-result scan is passing evidence.

## Tier 6: User/Caller Review

Use `writer` or `verifier` with the user/caller lens, or a documented
main-session fallback.

```text
Review the final branch diff from a library user/caller perspective.

Focus:
1. Caller ergonomics, misuse resistance, examples, and README/KDoc/Rustdoc clarity.
2. Unsupported backend capabilities are documented explicitly and tested as unsupported.
3. Error messages and migration notes help callers diagnose common mistakes.
4. Public capability claims grep-match actual source names and behavior.
5. Benchmark-backed recommendations include a chart when benchmark data is material, not only raw tables or prose.

Return P0/P1/P2/P3 findings with file:line evidence when possible.
If no issue is found, record N/A with reviewed scope and reason.
```

## Main-Session Integration Review

Always run for design-workflow tasks.

```text
Integrate the six independent perspective lane findings for the same module slice and diff base.

Focus:
1. Deduplicate and normalize findings into P0/P1/P2/P3.
2. Resolve conflicts between lanes.
3. Cover documentation, release readiness, and evidence integrity.
4. Confirm README.md and localized README updates when user-facing behavior changes.
5. Confirm public API KDoc/Rustdoc is English and matches actual source names.
6. Confirm CHANGELOG/release-note/migration impact is assigned or explicitly N/A.
7. Confirm module registration, CI/Nightly, coverage, lessons, PR body, and verification artifacts are sufficient and current.

Return P0/P1/P2/P3 findings with file:line or artifact evidence when possible.
If no issue is found, record N/A with reviewed scope and reason.
```

Do not spawn a seventh Tier subagent for this integration lane. The main Codex
session owns the final Step 6-R gate verdict.

## CI Workflow Quick Checks

When workflow YAML is touched, load
`../../bluetape-workflow/references/repository-hazards.md` and apply its
GitHub Actions, module-registration, Nightly, and coverage gates. Record the
exact `actionlint` command and any required dispatch URL as review evidence.

## Convergence

Normalize all findings into P0/P1/P2/P3.

P0 and P1 block PR creation. Fix them, rerun affected review lanes, and close Step 6-R only after P0 = 0 and P1 = 0. P2/P3 may be applied, deferred with rationale, or filed as follow-up.
