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
- PR: #{number}, milestone `{milestone}`, assignee `{user}`, merge state `{state}`
- CI: {run/check URL or N/A with concrete scope evidence}

### Changed Files

- `{path}`: {why it changed}

### Commits

{git log ... --oneline}

Final status: DONE / PENDING ({explicit boundary or remaining step}) / BLOCKED ({reason})

Unchecked required items: {none or checklist IDs}
```
