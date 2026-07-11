# Performance and Stability Scan

Use for Step 4-P and for performance/stability lenses in Step 6-R or 7-R. Review
the current diff, not an intermediate state.

## Performance

Check for blocking calls in suspend/event-loop paths, missing IO dispatch,
repeated regex/reflection/serialization/copying, unbounded buffering/retry/poll,
avoidable DB/cache/HTTP round trips, lock/atomic contention, repeated container
startup, and benchmark claims without reproducible evidence.

## Stability

Check cancellation/deadline propagation, resource cleanup on every exit path,
client/scope/executor/container ownership, configurable timeout/retry/backoff,
race-prone mutable state, startup/shutdown/health effects, useful diagnostic
context, backend failure recovery, and tests that can pass without proving their
named behavior.

Virtual-thread-aware code must not introduce monitor pinning. Coroutine code
must rethrow cancellation before broad exception handling. Use existing
bluetape4k concurrency/coroutine testers when they match the risk; record the
reason for any raw stress harness.

## Output

```markdown
| Priority | File:Line | Lens | Finding | Required fix/evidence |
|---|---|---|---|---|
| P1 | path/File.kt:42 | stability | {summary} | {fix or command} |
```

If clean, record the exact diff/files and commands inspected. P0/P1 blocks the
next gate and requires targeted test plus affected-lens rerun.
