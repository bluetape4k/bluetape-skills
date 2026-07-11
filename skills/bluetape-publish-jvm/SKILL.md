---
name: bluetape-publish-jvm
description: Use when planning, validating, dispatching, recovering, or closing a bluetape4k snapshot, Maven Central release, BOM/catalog train, or consumer synchronization.
---

# Bluetape Publish JVM

## Parent and Safety Contract

Use `bluetape-workflow` for Step DoD, first-plan approval, research
preservation, language policy, GitHub metadata, and side-effect authority.
Publishing snapshots/stable artifacts, pushing tags, closing staging, creating
GitHub Releases, and dispatching workflows are external side effects. Execute
only when explicitly requested or already included in the approved release
scope. Stable publication is irreversible.

If the user cites this skill or reports a procedure violation, stop the publish
branch, reread the applicable reference, repair that gate, and then continue.

## Required Reference Routing

Load only what the selected phase needs:

| Phase | Required reference |
| --- | --- |
| any stable release or consumer closeout | `references/release-checklist.md` |
| repo classification, DAG, catalog/snapshot/stable flow, train class | `references/topology-and-flows.md` |
| preflight, workflow input, dispatch hold, Maven/POM verification | `references/preflight-dispatch.md` |
| drafting or validating a GitHub Release | `references/release-notes.md` |

Stable work normally loads the first three. A read-only status question loads
only the references needed to answer it.

## Source Authorities

- `bluetape4k-dependencies`: registry for managed BOMs, versions, external
  dependencies/plugins, and the Gradle catalog.
- publish topology: release/snapshot ordering and edge semantics.
- target workflow YAML: the only dispatch-input schema.
- Maven Central HTTP/metadata: immutable artifact availability.
- GitHub live milestone/issues/PRs/releases: closeout state.

Do not infer a dependency version from `catalog/YYYY-MM-DD-NN`; catalog refs and
published `bluetape4k-dependencies` versions are separate authorities. Query
current GNO GitHub/docs evidence before planning a release-affecting change.

## Primary Flow

Choose exactly one:

- `catalog-train-snapshot`: catalog/import/shared-version change; pin immutable
  catalog ref, validate downstream, run full checks, publish snapshots in DAG
  order.
- `routine-snapshot`: refresh requested snapshots from intended `develop` SHAs;
  verify snapshot metadata, not stable POM URLs.
- `stable-release`: refresh checklist, prove the same state by snapshots, run
  preflight, confirm release class, respect DAG batches, and dispatch only after
  the irreversible hold passes.

For Go modules, use `bluetape-publish-go` instead of Maven-specific commands.

## Execution Skeleton

Apply `bluetape-workflow/references/checklist-contract.md` and render the
selected reference checklists. The following rows are the top-level blocking
state; reference rows remain required subchecks.

- [ ] **PUB-01 — Pin release identity and authority**
  - **Action:** Select exactly one flow and record repos, versions, class, branches/SHAs, artifact matrix, consumer scope, catalog role, and side-effect authority.
  - **Evidence:** Fresh durable release checklist with every identity field concrete and no version inferred from a catalog ref.
  - **Failure:** Stop before validation or dispatch; resolve ambiguity from live authorities.
- [ ] **PUB-02 — Close live planning and topology gaps**
  - **Action:** Query current issues, PRs, releases, workflows, artifacts, docs, and GNO evidence; classify repositories and compute an acyclic release DAG.
  - **Evidence:** Live URLs/results, selected execution list/batches, edge rationale, and disposition of excluded or retained versions.
  - **Failure:** Block the train on open release work, missing topology, cycles, or superseded targets.
- [ ] **PUB-03 — Prove the exact candidate state**
  - **Action:** Validate local dependency/catalog state, required Nightly/full checks, and matching-state snapshots in DAG order.
  - **Evidence:** Exact SHAs/catalog ref, commands, run URLs, metadata timestamps, and snapshot artifact matrix.
  - **Failure:** Do not promote a candidate whose snapshots, source, or public metadata differ from the intended stable state.
- [ ] **PUB-04 — Pass stable preflight**
  - **Action:** Complete every applicable row in `references/preflight-dispatch.md`, including generated POM/BOM, license, signing, artifact, changelog, and workflow-schema checks.
  - **Evidence:** Preflight checklist at X=Y with Blocked=0 and explicit evidence-backed N/A rows only.
  - **Failure:** Keep dispatch blocked and execute the smallest corrective flow.
- [ ] **PUB-05 — Refresh the irreversible hold**
  - **Action:** Immediately before each tag, workflow dispatch, staging close, or release creation, re-read the workflow schema and refresh every hold row from live state.
  - **Evidence:** Timestamped hold evidence newer than prior mutable events, with tag/release absence and exact declared inputs.
  - **Failure:** Stale, unknown, missing, pending, or guessed evidence blocks the side effect.
- [ ] **PUB-06 — Dispatch and verify publication**
  - **Action:** Dispatch only authorized declared inputs, monitor the exact run to terminal state, then verify every expected public artifact independently.
  - **Evidence:** Workflow URL/conclusion plus Central or snapshot HTTP/metadata proof for the complete artifact matrix.
  - **Failure:** Workflow success without public artifacts is FAIL; never overwrite, retag, or republish an immutable bad version.
- [ ] **PUB-07 — Close GitHub release state**
  - **Action:** Complete the authorized GitHub Release and milestone closeout using the release-notes checklist.
  - **Evidence:** Live release body/metadata and milestone/issue state, or concrete evidence that GitHub closeout is outside scope.
  - **Failure:** Keep public release closeout partial until the live state matches the published artifacts.
- [ ] **PUB-08 — Synchronize downstream consumers**
  - **Action:** Retarget superseded branches, align governed versions, and run resolution plus repository-level validation for every approved consumer.
  - **Evidence:** Per-consumer version, diff, commands/results, and concrete exclusions.
  - **Failure:** Do not count Gradle `help` alone or a stale consumer branch as complete.
- [ ] **PUB-09 — Open the next development line**
  - **Action:** When authorized, set and publish the approved next snapshot line from the exact develop SHA and update direct unreleased consumers.
  - **Evidence:** Source SHA/version, workflow URL, public snapshot metadata, consumer mapping, or concrete evidence this row is outside scope.
  - **Failure:** Keep stable branches non-SNAPSHOT and never reference a future stable version.
- [ ] **PUB-10 — Complete public documentation handoff**
  - **Action:** Update current install/baseline content and locale indexes to live published versions while preserving historical narratives.
  - **Evidence:** Stale-version searches, Central POM, live Releases, diff check, site build, or concrete evidence docs are outside scope.
  - **Failure:** Keep documentation closeout blocked until current guidance matches published reality.
- [ ] **PUB-11 — Report release truth**
  - **Action:** Render every publish and reference row with counts, URLs, SHAs, versions, artifacts, waivers, exclusions, residual risks, and side-effect state.
  - **Evidence:** `Required checks: X/Y; N/A: N; Blocked: 0` with X=Y for completed scope and no missing artifact evidence.
  - **Failure:** Do not claim published or complete; identify the blocked row and recovery action.

1. Pin repo(s), target version, class, branch/SHA, artifact matrix, consumer
   scope, and authority in the checklist.
2. Query live issue/PR/release/workflow state and current external artifacts.
3. Build/validate the release DAG and selected execution list.
4. Validate the exact dependency/catalog state locally and through required
   Nightly/full plus snapshots.
5. Re-run the preflight and dispatch-hold rows immediately before each
   irreversible action.
6. Dispatch only declared workflow inputs; monitor to terminal state.
7. Verify every expected artifact from the public endpoint, not merely workflow
   success.
8. Complete GitHub Release/milestone closeout, next development line, downstream
   consumer sync, and public-doc handoff that are in scope.
9. Report Step DoD with URLs, SHAs, versions, artifact matrix, waivers, and
   remaining risks.

Run dependent releases sequentially. Stable batches may run in parallel only
when DAG prerequisites are already public and workflows do not mutate shared
catalog state. Run heavyweight integration validation sequentially.

## Fail-Closed Rules

- Unknown/stale/failed checklist row blocks dispatch.
- Missing or undeclared workflow input blocks/gets omitted; never guess.
- Maven Central 404 blocks downstream release even if Central Portal accepted.
- Stable BOM/POM containing `-SNAPSHOT`, missing versions, or leaked
  example/benchmark/workshop/experimental artifacts blocks publication.
- An immutable bad publication is never overwritten or retagged; use the
  smallest corrective patch and refresh every consumer target.
- `./gradlew help --refresh-dependencies` proves resolution only, not consumer
  completion; run repo-level tests or record a failed/waived consumer.
- Active repositories explicitly excluded by the user remain untouched.

## Stop Conditions

Stop before side effects when target version/class/authority is ambiguous,
snapshot evidence does not match the stable state, topology has a cycle, open
release-affecting work remains, workflow schema changed, signing/POM/artifact
checks fail, or a consumer target was superseded. Provide the smallest repair
flow and preserve the checklist evidence.

## Completion Output

Report selected flow/class, execution order/batches, repos and SHAs, workflow
URLs, Central/snapshot evidence, artifact matrix, retained/skipped versions,
consumer/docs/next-line status, waivers, residual risks, and the parent Step DoD
table. PR bodies end with `## DoD Status`; verify live bodies.
