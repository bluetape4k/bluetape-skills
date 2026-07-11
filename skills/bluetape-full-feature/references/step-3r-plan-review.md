# Step 3-R Plan Review Check Items

Use these checks during Step 3-R critic integration.

## Required Checks

1. Every spec requirement and DoD item maps to a concrete plan task.
2. Task ordering is implementable against the current codebase.
3. No task depends on code or artifacts produced by a later task.
4. Test tasks cover success, failure, edge, concurrency, coroutine, lifecycle, and backend-capability paths when relevant.
5. Verification commands are concrete and targeted.
6. README.md and existing localized README files are covered when public behavior changes.
7. English KDoc, GitHub PR/issue text, changelog, or release notes are covered when contributor-facing artifacts change.
8. New modules include settings registration, BOM constraints when publishable, CI/Nightly scope, test resources, and coverage aggregation checks.
9. Spring Boot auto-configuration tasks include conditional class/property guards and registration ordering checks.
10. Exposed tasks include deprecated import avoidance and receiver-shadowing checks.
11. Coroutine tasks preserve cancellation and dispatcher boundaries.
12. Performance/stability tasks cover allocation pressure, blocking calls, resource cleanup, polling/backpressure, and Testcontainers stability.
13. Cross-module duplication has a reuse or extraction decision.
14. Rollback, compatibility, or migration risks are explicit for broad API changes.

## Conditional Checks

- Domain-constrained fields: validate semantic constraints at task level rather
  than leaving them to implementation intuition.
- Client/resource work: name creation, ownership, close, and startup/shutdown
  position.
- Streaming APIs: name logical EOF, truncated final input, post-terminal reuse,
  and double-terminal-call tests.
- Suspend APIs: include explicit cancellation-propagation tests.
- JDK preview APIs: record binary-incompatibility risk and a stable migration
  path for the next major JDK version.

## Output

Return a concise table:

```markdown
| Priority | Area | Finding | Required plan edit |
|---|---|---|---|
| P1 | Tests | {summary} | {edit} |
```

P0/P1 findings block Step 3-R closure.
