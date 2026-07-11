# Native Agent Routing

Read this reference only immediately before native subagent dispatch. Resolve
the concrete model and reasoning effort from the current workspace `AGENTS.md`
and installed agent catalog; this skill does not pin model IDs.

## Boundaries

- The workflow owns the step and evidence contract. The installed role owns
  its narrow execution surface.
- Use only installed canonical `agent_type` values. Security, performance,
  stability/Ops, developer/API, and user/caller are prompt lenses, not agent
  type names.
- `explore` owns read-only repository facts. `researcher` owns official
  external documentation. `dependency-expert` owns package/SDK comparison.
- The main session owns plan approval, mutations outside a delegated write
  scope, integration, severity normalization, final P0/P1 verdict, and external
  side effects.
- Never route commits, PRs, merges, dispatches, releases, publishes, destructive
  cleanup, or durable guidance writes through an untrusted-content lane.

## Canonical Lenses

| Perspective | Installed role | Prompt focus |
|---|---|---|
| Architecture | `architect` | Boundaries, interfaces, compatibility, long-horizon tradeoffs |
| Security | `code-reviewer` | Trust boundaries, authn/authz, input validation, secrets |
| Performance | `code-reviewer` | Hot paths, allocation, contention, latency, benchmark validity |
| Stability/Ops | `verifier` | Lifecycle, recovery, cancellation, observability, rollback |
| Developer/API | `code-reviewer` | API contracts, compatibility, idioms, tests, docs accuracy |
| User/caller | `writer` or `verifier` | Ergonomics, examples, misuse resistance, migration clarity |
| Build/CI/tests | `test-engineer` | Gradle, CI, coverage, module registration, test strategy |
| Failure diagnosis | `debugger` | Root cause of compile, test, CI, or toolchain failures |
| Implementation | `executor` | Bounded code/doc write scope after approval |

Multiple independent lanes may use the same installed role with different lens
prompts. Each prompt names exactly one perspective, exact files/artifacts,
write permission, heavy-command limit, output format, and stop condition.

## Workflow Mapping

| Step | Default role |
|---|---|
| Classification/requirements | `analyst` or main session; `explore` for repo facts |
| External reference gathering | `researcher` |
| Dependency adoption/upgrade choice | `dependency-expert` |
| Spec/design | `architect` |
| Plan | `planner`; `test-engineer` for test/build shape |
| Implementation/refactor | `executor`; `code-simplifier` only for behavior-preserving cleanup |
| Reproduction/unclear failure | `debugger` |
| Test execution/strategy | `test-engineer` |
| Review | `code-reviewer` plus triggered lenses |
| Verification/DoD | `verifier`; main session owns final acceptance |
| Documentation/lessons | `writer` |
| Git history/PR preparation | `git-master` or main session |

Type B/C uses the smallest triggered subset. Type A uses independent spec,
plan, and implemented-diff perspectives where risk warrants them. Type D stays
read-only. Type E uses `explore` for discovery, `writer` or `executor` for the
narrow approved edit, and `verifier` for parity/audit. Type P keeps irreversible
actions in the main session. Type F uses `test-engineer`, `executor`,
`code-reviewer`, and `verifier` around one candidate at a time.

## Lane Lifecycle

1. State lane count, scopes, command limits, and stop condition.
2. Use fresh gate-scoped agents; do not reuse unrelated completed work.
3. Continue main-session local verification while lanes run.
4. Wait in bounded intervals. Close or replace an unresponsive lane rather
   than making it the critical-path owner.
5. Rerun only affected lenses after fixes.
6. If a required role is unavailable, perform a main-session local equivalent
   and record the missing role; never silently substitute an invented label.

Heavy Testcontainers, real database, native, JNI, and emulator checks remain
sequential regardless of lane count.
