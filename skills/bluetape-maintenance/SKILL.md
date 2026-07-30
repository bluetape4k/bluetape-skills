---
name: bluetape-maintenance
description: Use when bluetape4k work changes README, KDoc, docs, AGENTS.md, workflow guidance, skills, plugins, Codex or OMX harness configuration, or other non-production maintenance surfaces.
---

# bluetape4k Maintenance

## Parent Contract

**REQUIRED SUB-SKILL:** Use `bluetape-workflow` first for Type E classification, plan approval, gate progression, and Step DoD reporting.

Use this skill only for maintenance that does not change production behavior.

Route writing, diagrams, publishing, and production-code changes to their
canonical support skill or Type A/B/C workflow.

## Required Shape

- Query `bluetape4k-github` and `bluetape4k-docs` before durable guidance edits.
- Keep edits small, manual, and reviewable; avoid broad regex rewrites.
- For reusable skills/config/harness resources, update chezmoi source first, apply live, verify source/live match, then commit and push dotfiles.
- For Codex/OMX harness changes, run `$self-audit` after live apply; include `codex mcp list` when MCP config, plugin registration, or server command paths changed.
- Do not change Codex global permission policy, sandbox mode, network policy, auto-update behavior, or hook trust state unless the user explicitly requested that exact policy change and the DoD records a rollback path.
- Use canonical names in active guidance. Create or retain a thin compatibility
  alias only when catalog inspection proves that an installed caller or a
  demonstrated current user habit still depends on it; historical documents
  alone do not justify alias recreation.
- Keep agent-facing guidance in concise English.
- Run `git diff --check` and a targeted `rg` reference check before claiming completion.
- For documentation-only changes, verify content and links; do not run heavyweight CI unless rendered docs or branch protection require it.
- Use the parent workflow's final-report and PR-body templates.

## Mandatory Type E Checklist

Apply `bluetape-workflow/references/checklist-contract.md`.

- [ ] **E-01 — Route support skills**
  - **Action:** Select blog, diagram, publish, or language support skills triggered
    by the changed surface.
  - **Evidence:** loaded skills or concrete N/A scope evidence.
  - **Failure:** STOP before editing with a missing route.
- [ ] **E-02 — Discover current guidance**
  - **Action:** Read current source/live files, relevant GNO GitHub/docs, lessons,
    and reproduction chain before editing.
  - **Evidence:** queries, paths, and current source/target mapping.
  - **Failure:** remain read-only until authority is known.
- [ ] **E-03 — Preserve behavior and ownership**
  - **Action:** Keep production behavior unchanged, edit managed source first, and
    exclude Claude/global policy surfaces unless explicitly included.
  - **Evidence:** scoped diff and exact authority for any conditional exception.
  - **Failure:** revert unauthorized scope or reclassify Type A/B/C.
- [ ] **E-04 — Apply and prove parity**
  - **Action:** targeted chezmoi apply and source/rendered/live comparison.
  - **Evidence:** apply result and zero parity mismatches.
  - **Failure:** repair source chain; live-only success is FAIL.
- [ ] **E-05 — Run maintenance verification**
  - **Action:** run diff check, targeted references, triggered actionlint/docs
    build/MCP check, sync status, and self-audit.
  - **Evidence:** fresh command results and explicit N/A scope proof.
  - **Failure:** leave unchecked and repair before commit/push.
- [ ] **E-06 — Complete durable pre-PR proof**
  - **Action:** Verify duplicates, aliases, language, capability, source/live
    parity, and pruning candidates so the parent can run CG-09 and CG-10.
  - **Evidence:** Final diff, zero parity mismatches, reference results, pruning
    decision, and every triggered maintenance check PASS or valid N/A.
  - **Failure:** Keep PR publication blocked until the maintenance proof and
    common pre-PR gates pass.
- [ ] **E-07 — Deliver and report through the common PR gates**
  - **Action:** Execute CG-11 through CG-15, or the common no-PR branch, without
    redefining those gates.
  - **Evidence:** Parent-gate receipts plus the maintenance proof from E-06.
  - **Failure:** preserve the parent gate's PENDING/FAIL state.
- [ ] **E-08 — Close out only after fresh merge approval**
  - **Action:** After E-07, follow CG-16 through CG-18 or record the common
    no-PR N/A branch.
  - **Evidence:** Parent-gate receipts for approval, merge verification, sync,
    and cleanup.
  - **Failure:** preserve the parent gate's PENDING/FAIL state.

## Skill / Plugin Diet

When adding, renaming, aliasing, archiving, or rerouting a bluetape4k skill,
read `references/skill-taxonomy.md` before editing the catalog.

- Prefer disabling unused plugins before deleting local skills; plugin disablement is reversible and removes injected skill descriptions from future sessions.
- Keep first-party or high-use plugins enabled only when they add capability not already covered by local skills.
- Disable duplicate plugin skill families when local canonical skills already exist.
- Archive local skills only when they are deprecated, duplicated by a canonical skill, or outside the user's active workflow.
- Do not archive `.system`, OpenAI docs, GitHub, Browser, or active bluetape4k skills without an explicit replacement.
- After pruning, recount live `~/.codex/skills` descriptions and record whether the Codex skill-budget warning is expected to persist.

## Rule Mining Loop

Use this loop when recent lessons, PR review comments, CI failures, or user
corrections suggest recurring workflow misses.

1. **Collect**: gather the bounded evidence set, such as recent `docs/lessons`,
   PR review comments, failed CI summaries, or current-session corrections.
2. **Cluster**: group repeated misses by failure mode, not by repository name.
3. **Generate**: write small candidate rules that would have prevented the miss.
4. **Verify**: challenge each candidate with a skeptic pass: would the rule have
   prevented a real recurrence, and does it avoid false positives or excess
   workflow cost?
5. **Promote**: add only surviving rules to the narrowest durable surface:
   repo-local `AGENTS.md`, `bluetape-workflow`, a Type-specific skill, or a
   reference file.
6. **Validate**: run `git diff --check`, targeted text search, and source/live
   checks for managed skills before reporting completion.

Do not promote chat-only observations or one-off failures directly into broad
skill rules. Keep Claude CLI or vendor-specific workflow dependencies out of
the canonical bluetape4k skills unless the user explicitly reintroduces them.

## Stop / Escalate

Escalate to `bluetape-full-feature` when maintenance work changes architecture or public behavior. Escalate to `bluetape-bugfix` when maintenance reveals a concrete defect that needs a fix cycle.
The parent common gates define merge-ready, DONE, and no-PR terminal states.
