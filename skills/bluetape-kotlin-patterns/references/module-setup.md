# Kotlin Module Setup

Use for module add/move/rename/removal, artifact rename, or a new benchmark
module. Also load the workflow repository-hazards reference.

## Registration Chain

- Follow the repository's existing `settings.gradle.kts` include helper.
- Update root/module README locale sets and repo-local module maps/AGENTS.
- Add `src/test/resources/junit-platform.properties` and `logback-test.xml` for
  new tested modules.
- Update CI path filters/jobs, summary `needs`, Nightly/examples coverage,
  Kover artifact names, BOM/catalog constraints, and generated checks.
- Expose publication/BOM entries only when the module is publishable.
- Preserve centrally governed versions and compatibility-line aliases; start
  shared version changes in `bluetape4k-dependencies`.

## Benchmark Modules

- Place under `benchmark/<name>-benchmark` or an existing benchmark directory.
- Use `kotlinx.benchmark` plus `kotlin("plugin.allopen")`; do not hand-roll a
  raw-JMH-only module.
- Verify generated task names with `./gradlew :<module>:tasks --all`.
- Keep Testcontainers-backed benchmarks serial.
- Document Gradle commands, run conditions, raw JSON, metric direction, result
  tables, and README locale/chart assets. Load `bluetape-diagram` for charts.

## Verification

- `./gradlew projects` shows the intended module graph.
- Affected compile/test and publication/catalog checks pass.
- Workflow paths/jobs/artifacts cover both old and new names as appropriate.
- Public docs and dependency snippets name the actual artifact.

## Blocking Module Checklist

- [ ] **KT-MOD-01 — Synchronize registration**
  - **Action:** Update settings, README locales, module maps/AGENTS, test resources, CI/Nightly/summary, Kover, BOM/catalog, and generated checks as triggered.
  - **Evidence:** Registration-chain diff and `./gradlew projects` result.
  - **Failure:** Any missing triggered link blocks module completion.
- [ ] **KT-MOD-02 — Preserve dependency governance**
  - **Action:** Keep centrally governed versions in dependencies and expose publication entries only for publishable modules.
  - **Evidence:** Catalog/BOM source mapping and publication classification.
  - **Failure:** Remove duplicated/drifting governance or leaked artifacts.
- [ ] **KT-MOD-03 — Validate benchmark modules**
  - **Action:** For benchmarks, use kotlinx-benchmark/allopen, verify generated tasks, serialize infrastructure, and document commands/data/metrics/assets.
  - **Evidence:** Task listing, benchmark configuration, raw result paths, and diagram checklist; or concrete N/A.
  - **Failure:** Reject raw-JMH-only or unmeasured module setup.
- [ ] **KT-MOD-04 — Prove the final module surface**
  - **Action:** Run affected compile/tests/publication checks and verify workflows/docs use actual old/new names.
  - **Evidence:** Fresh commands and name searches with no stale registration.
  - **Failure:** Keep the module change blocked until all surfaces agree.
