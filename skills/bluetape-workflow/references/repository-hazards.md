# Repository Hazard Gates

Load only the sections triggered by the approved scope.

## Module Registration

For module add, move, rename, removal, or artifact rename, verify the entire
registration chain: `settings.gradle.kts`, README locale set, repo-local module
maps, CI path filters/jobs, Nightly/examples workflows, summary `needs`, Kover
artifacts, BOM/catalog constraints, generated checks, and `./gradlew projects`.
Container-backed modules normally belong in Full Nightly rather than daily
smoke. Missing coverage usually means a missing job/artifact before low code
coverage.

## Shared Catalog and Dependency Trains

- Start centrally governed changes in `bluetape4k-dependencies`.
- Keep the managed catalog and dependencies BOM distinct.
- Use the repository sync/check helper; do not hand-edit generated entries.
- Verify published dependency versions separately from catalog ref names.
- Preserve compatibility lines such as Spring Boot 3/4, Kafka 3/4, and
  Jackson 2/3 rather than collapsing them accidentally.
- Validate prerequisite producers before opening downstream consumer PRs.

## GitHub Actions and Coverage

- Use unescaped single quotes inside expressions, for example
  `${{ needs.changes.outputs['key'] == 'true' }}`. Never write `\'` inside an
  expression.
- Avoid broad regex edits to workflow YAML; use small anchored edits or a
  structured YAML tool, then run `actionlint` and inspect neighboring `env:`
  blocks.
- Keep Kover XML and Codecov visibility. Expected coverage artifacts must fail
  when absent; do not accept silent zero coverage.
- Do not add or restore hard Kover thresholds without an explicit policy
  decision. Exclude benchmark, generated, and other non-production sources.

## Benchmarks

- Put benchmark harnesses under `benchmark/<name>-benchmark` or an existing
  benchmark module; do not place harness code in production modules.
- Use the `kotlinx.benchmark` Gradle plugin. Do not create raw-JMH-only modules.
- Run `./gradlew :<module>:tasks --all` before naming generated benchmark tasks
  or filters.
- Record command, environment, raw JSON path, metric direction, result table,
  and caveats. Local short-window results are comparable snapshots, not broad
  production rankings.
- Load `bluetape-diagram` when chart assets are produced, and update all
  existing README locales.

## HTTP, HC5, and Testcontainers

- Verify external API placement with source/jar inspection before implementing
  factories and cover started/unstarted lifecycle contracts.
- Extend shared adapter conformance before backend-specific assertions. Test
  cancellation before enqueue and in flight, delayed body cleanup, timeout
  exposure, and request-tag propagation when relevant.
- Shared Testcontainers launchers must be SDK-neutral, expose endpoint and
  credential properties, define singleton reuse, and verify bind/host-port
  behavior when image tags or flags change.
- Do not use an ABI-sensitive codec in a generic smoke test unless that ABI is
  the explicit objective.

## Broad Backend Matrices

Split broad multi-backend work into a core/API/SPI PR, one backend or narrow
backend-family PR per slice, then a cross-cutting adoption/smoke PR after the
backend slices converge. Each PR must be independently reviewable and tested.

## Nightly and Cleanup

- Treat open PRs, non-default branches, dirty status, ahead commits, and stale
  worktrees as explicit closeout state.
- If a workflow fails then passes on retry, investigate lifecycle,
  Testcontainers, or timing risk.
- Remove worktrees/branches only when ancestry or patch-equivalence proves the
  work is integrated; preserve modified or untracked worktrees.
