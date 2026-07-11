---
name: bluetape-py-patterns
description: Use when implementing, planning, reviewing, packaging, or releasing Python code in bluetape-py or another bluetape ecosystem Python repository.
---

# bluetape-py Patterns

When used inside a bluetape workflow, the parent owns Step DoD, approvals,
GitHub metadata, and side effects. This skill owns Python-specific code,
packaging, async, testing, and P0/P1 review rules.

## Non-Negotiables

- Keep APIs Python-native; do not port Kotlin/Go/Rust package shapes.
- Target Python 3.13+ unless a documented compatibility constraint says
  otherwise.
- Keep the `bluetape` meta distribution thin (`bluetape-core` by default),
  `bluetape-core` stdlib-only, logging stdlib-first, and heavier integrations in
  focused distributions/extras.
- Do not create a root `bluetape/__init__.py` convenience surface. Focused
  distributions own imports such as `bluetape.core` and `bluetape.logging`.
- Prefer stdlib/repo helpers. New dependencies need explicit boundary,
  tradeoff, and validation evidence.
- Public contracts require success, failure, empty/boundary, type/protocol, and
  cancellation/timeout tests when relevant.
- A P0/P1 finding blocks progression. Reviews return P0/P1/P2/P3 with
  `file:line` evidence or explicit no findings.

## P0/P1 Gate

### P0

- unsafe deserialization, injection/traversal/SSRF, spoofable trust boundary,
  auth bypass, or secret leakage;
- silent loss, duplication, corruption, misordering, or mutation of
  caller-owned data;
- task/thread/process/file/socket/DB/container leak capable of hanging or
  exhausting production;
- release metadata that publishes the wrong distribution, Python requirement,
  dependency boundary, or unreproducible artifact.

### P1

- swallowed/retried `asyncio.CancelledError` or caller timeout without a proven
  translation contract;
- file, tempdir, response, cursor/connection, timer, subprocess, contextvar
  token, container, or background task not cleaned on every path;
- broad/non-Pythonic/duplicative API or ambiguous `None`/`False` operational
  failure;
- broad exception handling that loses cancellation, public exception type, or
  causal context;
- mutable default/global/cache/singleton/context-local ownership without
  isolation and concurrency evidence;
- optional integration leaking into the thin default install, duplicated extras,
  missing workspace source, or stale lock/build metadata;
- tests missing failure/boundary/cancellation/package-build proof;
- global logger state, secret/raw-provider logging, context reset leak, or
  high-cardinality defaults;
- docs/metadata claiming nonexistent modules, extras, commands, or adapters.

## Spec and Plan Gate

Verify API shape, public exceptions, package/import/extras boundaries,
active/internal/planned status, async task/cancellation/timeout ownership,
blocking boundaries, contextvar reset semantics, tests, and realistic examples.

Release plans additionally pin issue/PR metadata, `pyproject.toml`, `uv.lock`,
built artifacts, target branch/tag, latest observed version, and publish
authority before any external action.

## Implementation Defaults

- Use modern Python 3.13 typing; add `Protocol`/dataclasses only when they remove
  real ambiguity.
- Prefer explicit exceptions over ambiguous sentinels.
- Rethrow `asyncio.CancelledError` before broad exception handling.
- Use context managers or `try/finally` for every owned resource/token/task.
- Keep logging caller-owned with stdlib `logging`, filters/adapters, and
  `contextvars`; no global registry.
- Keep pure helpers deterministic and avoid importing optional integrations at
  module import time.
- For package changes, update package `pyproject.toml`, workspace sources,
  relevant README locale set, and `uv.lock` when resolution changes.
- Do not add web/cache/Redis/Testcontainers/serde/benchmark adapters before the
  distribution boundary and validation target are recorded.

## Testing and Validation

## Mandatory Python Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **PY-01 — Pin Python and package boundaries**
  - **Action:** Classify touched distributions/imports/extras, Python compatibility, active/internal/planned status, dependency boundaries, and release authority when applicable.
  - **Evidence:** Package map, pyproject/workspace/lock anchors, public surface, non-goals, and exact authority/version fields for release work.
  - **Failure:** Block implementation or publication on ambiguous namespace, dependency, or target identity.
- [ ] **PY-02 — Define public and async contracts**
  - **Action:** Specify API shape, exceptions, empty/boundary behavior, task/cancellation/timeout/blocking ownership, contextvar reset, cleanup, and realistic examples.
  - **Evidence:** Spec/plan mapping to tests for success, failure, boundary, typing/protocol, and lifecycle behavior.
  - **Failure:** Reject ambiguous sentinels, broad ports, or unowned async/resources.
- [ ] **PY-03 — Implement with isolation and cleanup**
  - **Action:** Use modern typing, explicit exceptions, cancellation rethrow, context managers/finally, caller-owned logging, deterministic helpers, and lazy optional imports.
  - **Evidence:** Scoped diff with every owned resource/token/task cleanup path and dependency rationale.
  - **Failure:** Record P0/P1 for leaks, swallowed cancellation, global state, secrets, or optional-integration leakage.
- [ ] **PY-04 — Prove behavior and isolation**
  - **Action:** Run parametrized success/failure/boundary tests, bounded cancellation/timeout cleanup, logging/context reset/redaction, and no-global-side-effect tests.
  - **Evidence:** Fresh targeted pytest output tied to each touched contract.
  - **Failure:** Smoke-only or long-sleep evidence does not satisfy lifecycle claims.
- [ ] **PY-05 — Prove packaging changes**
  - **Action:** When metadata, dependencies, workspace, namespace, or extras change, sync locks, build all packages, and run isolated wheel/import/extra smoke checks.
  - **Evidence:** Updated package/workspace/lock files, build artifacts, and isolated import results, or concrete N/A.
  - **Failure:** Block on stale metadata, missing workspace source, wrong Python requirement, or default-install leakage.
- [ ] **PY-06 — Run the fresh validation ladder**
  - **Action:** Run diff check, ruff format/lint, targeted pytest, triggered sync/build, and proportional broader tests/workflow/CI; serialize shared external state.
  - **Evidence:** Fresh successful commands or exact unrelated blocker plus strongest unaffected proof.
  - **Failure:** Do not issue PASS from stale, partial, or unexplained missing validation.
- [ ] **PY-07 — Render the Python verdict**
  - **Action:** Report scope/baseline, commands, file:line findings, gaps, package/release state, and parent DoD counts.
  - **Evidence:** X=Y, Blocked=0, exact P0=0/P1=0 for PASS.
  - **Failure:** Expose unchecked rows and blocking findings instead of declaring completion.

- pytest unit/import tests; `pytest-asyncio` for loop-dependent async behavior;
- parametrized success/invalid/empty/boundary and caller-value preservation;
- bounded cancellation/timeout tests with cleanup assertions, not long sleeps;
- logging/context isolation, reset, redaction, and no-global-side-effect tests;
- package build plus isolated wheel/import/extra smoke checks when metadata or
  namespace packages change;
- serialize Testcontainers/shared external-state tests.

Run the smallest proving set, then expand:

1. `git diff --check`;
2. `uv run ruff format --check .` and `uv run ruff check .`;
3. targeted `uv run pytest <path>`;
4. `uv sync --all-packages` when dependency/workspace state matters;
5. `uv build --all-packages` plus isolated import smoke for packaging changes;
6. broader pytest, workflow lint, and GitHub CI proportional to scope.

If broader validation is blocked by an unrelated baseline/environment failure,
record the exact error and run the strongest unaffected targeted/workspace
commands.

## Review Output

Report reviewed diff/baseline, evidence commands, findings with `file:line`,
exact `P0=<n> P1=<n>`, verdict, and gaps. PASS requires P0=0 and P1=0.
