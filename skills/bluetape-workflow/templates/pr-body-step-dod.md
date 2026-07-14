# PR Body Template - Step DoD Last Section

Use this for `bluetape4k-*` pull requests. Keep the PR body in English unless the user says otherwise.

Do not add any section after `## DoD Status`.
Do not start the PR body with DoD. DoD is execution history; the body must first explain why the PR exists and what it solves.

```markdown
## Summary

Closes #{issue-number}

{1-3 lines explaining why this PR exists and the outcome it is meant to achieve.}

## Background

{What happened before this PR? Name the milestone, issue, defect, gap, user request, or review finding that made the PR necessary.}

## What This Solves

- {problem/gap/risk solved by this PR}
- {problem/gap/risk solved by this PR}

## Work Done

- {change}: {what changed and how it addresses the solved problem}
- {change}: {what changed and how it addresses the solved problem}

## Validation

- `{command}`: PASS/FAIL ({short evidence})
- `{command}`: PASS/FAIL ({short evidence})

## Review Notes

- P0/P1: {0 or list remaining blockers}
- P2/P3: {fixed/deferred/follow-up issue numbers}
- Review evidence: {review comment URL, formal review URL, or local review artifact}

## Metadata

- Issue: #{issue-number}, milestone `{milestone}`, assignee `{user}`
- PR: #{pr-number}, head `{head-sha}`, milestone `{milestone}`, assignee `{user}`
- CI: {run/check URL or N/A with concrete scope evidence}

## DoD Status

Required checks: {checked}/{total}; N/A: {count}; Blocked: {count}

| Check | Action | Status | Evidence | Failure / Next Action |
|------|--------|--------|----------|-----------------------|
| {id} - {name} | {action performed} | PASS / FAIL / PENDING / N/A | {fresh command, file, PR, issue, review comment, CI run; N/A requires concrete scope evidence} | {none, repair, rollback, blocker, or next action} |
| {id} - {name} | {action performed} | PASS / FAIL / PENDING / N/A | {evidence} | {failure handling} |

Final status: PENDING (CG-14 CI/review for PR #{pr-number} at {head-sha}) / PENDING (CG-16 fresh merge approval after CG-15 for PR #{pr-number} at {head-sha}; unchecked: CG-16, CG-17, CG-18) / blocked ({reason})

Unchecked required items: {none or checklist IDs}
```
