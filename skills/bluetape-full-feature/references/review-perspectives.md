# Spec and Plan Review Perspectives

Use after the artifact exists. Set `artifact_kind=spec` for Step 2-R or
`artifact_kind=plan` for Step 3-R. Use canonical installed roles from the
workflow model-routing reference; the perspective names below are prompt
lenses, not agent types.

## Six Independent Lanes

Each lane returns only evidence-backed P0/P1/P2/P3 findings and required edits.

| Lens | Spec focus | Plan focus |
|---|---|---|
| Performance | Hot paths, latency, allocation, contention, round trips, benchmark/stress acceptance | Task-level performance evidence, benchmark commands, hot-path validation |
| Stability | Race/deadlock/leak, retry, cancellation/deadline, lifecycle, recovery | Failure-path tasks, cleanup, retry/cancellation tests, Testcontainers stability |
| Security | Trust boundaries, authn/authz, secrets, injection, deserialization, safe defaults | Security tasks, controlled inputs, negative tests, configuration defaults |
| Operator/Ops | Observability, rollback, migration, ownership, runbook and release impact | Diagnostics, health/readiness, rollout/rollback, release evidence |
| Developer/API | API shape, codebase fit, compatibility, language conventions, testability | Atomic ordered tasks, module boundaries, patterns, exact commands |
| User/caller | Ergonomics, misuse resistance, examples, unsupported behavior, migration | README/KDoc/Rustdoc/examples, caller validation, migration tasks |

## Main-Session Integration

Using the same artifact and research/spec basis:

1. deduplicate and normalize findings;
2. identify contradictions and unsupported assumptions;
3. cover documentation, release readiness, and evidence integrity;
4. check repo-local AGENTS and bluetape4k conventions;
5. map each P0/P1 to an exact artifact edit and rerun lens;
6. surface open user decisions instead of guessing.

For specs, verify boundaries, failure modes, alternatives, acceptance criteria,
testability, compatibility, and operational behavior. For plans, additionally
load `step-3r-plan-review.md` and verify implementable ordering plus complete
spec-to-task mapping.

## Output

```markdown
| Priority | Lens | Evidence | Required edit | Rerun lane |
|---|---|---|---|---|
| P1 | stability | {artifact section} | {specific repair} | stability |
```

Record reviewed scope and a reason for any N/A. Close only when the latest
integrated result is P0=0 and P1=0. P2/P3 must be fixed, deferred with rationale,
or filed as follow-up.
