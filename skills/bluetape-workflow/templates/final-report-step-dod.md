# Final Report Template - Step DoD

Use this for user-facing `bluetape4k-*` completion reports. Use Korean when the conversation is Korean, but keep GitHub titles, PR bodies, and pushed commit messages in English unless the user says otherwise.

```markdown
## Completion Report - {task title}

Required checks: {checked}/{total}; N/A: {count}; Blocked: {count}

| Check | Action | Status | Evidence | Failure / Next Action |
|------|--------|--------|----------|-----------------------|
| {id} - {name} | {action performed} | PASS / FAIL / PENDING / N/A | {fresh command, file, PR, issue, review comment, CI run; N/A requires concrete scope evidence} | {none, repair, rollback, blocker, or next action} |
| {id} - {name} | {action performed} | PASS / FAIL / PENDING / N/A | {evidence} | {failure handling} |

### P0/P1 Gate

- P0 (CRITICAL): {N} -> 0 (resolved: {list or "none"})
- P1 (HIGH): {N} -> 0
- P2/P3: {fixed/deferred/follow-up issue numbers}

### Validation

- `{command}`: PASS/FAIL ({short evidence})
- `{command}`: PASS/FAIL ({short evidence})

### Metadata / CI

- Issue: #{number}, milestone `{milestone}`, assignee `{user}`
- PR: #{number}, head `{sha}`, milestone `{milestone}`, assignee `{user}`, merge state `{state}`
- CI: {run/check URL or N/A with concrete scope evidence}
- Delivery stage: {CG-14 CI/review PENDING / CG-15 merge-ready / CG-16 fresh approval PENDING / CG-18 closeout DONE / no-PR N/A}

### Changed Files

- `{path}`: {why it changed}

### Commits

{git log ... --oneline}

Final status: DONE / PENDING ({explicit gate ID, exact target/head, and remaining step}) / BLOCKED ({reason})

Unchecked required items: {none or checklist IDs}
```

At merge-ready, do not claim `X=Y`: CG-16 through CG-18 remain applicable and
unchecked. Use `PENDING (CG-16 fresh merge approval for PR #{number} at
{head-sha})`. Report `DONE` only after CG-17 live merge verification and CG-18
sync/cleanup, or after the no-PR branch records CG-11 through CG-18 N/A.
The no-PR branch reaches `DONE` only when every other applicable
router/common/leaf row is PASS or evidence-backed N/A.
