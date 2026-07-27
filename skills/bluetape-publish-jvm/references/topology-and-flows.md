# Repository Topology and Release Flows

## Repository Classes

- Stable candidate: `bluetape4k-*`, not workshop/experimental, registered in
  dependencies, with publish workflow support.
- `bluetape4k-dependencies`: final consumer BOM and internal catalog source;
  release after every imported internal BOM it references is public.
- `bluetape4k-experimental`: snapshot-only; never in stable train/final BOM.
- Workshops, examples, apps, `.github`, and site are consumers/handoffs, not
  stable library releases unless a distinct deployment flow is requested.

## Edge Types

- `releaseDependsOn`: stable order.
- `snapshotDependsOn`: snapshot order.
- `catalogManagedBy`: catalog alignment only.
- `testOnlyDependsOn`: validation only.
- `exampleOnlyDependsOn`: never stable order.

The graph must be acyclic for release edges. A requested repo is a seed: compute
upstreams, affected downstream validation, and final order. Reject missing
stable topology entries and any library release path depending on the final
dependencies BOM.

## Topology Checklist

- [ ] **TOP-01 — Classify every repository**
  - **Action:** Assign each selected or affected repository to the stable, dependencies, experimental, or consumer/handoff class.
  - **Evidence:** Repository-to-class map with exclusions.
  - **Failure:** Do not place an unclassified repository in a release batch.
- [ ] **TOP-02 — Type every edge**
  - **Action:** Mark each relationship as release, snapshot, catalog, test-only, or example-only dependency.
  - **Evidence:** Edge list with source evidence and no example/test/catalog edge promoted to stable ordering.
  - **Failure:** Repair ambiguous or incorrectly promoted dependencies.
- [ ] **TOP-03 — Prove an acyclic execution graph**
  - **Action:** Compute upstream closure, affected downstream validation, final order, and batches from the requested seed.
  - **Evidence:** Acyclic DAG and batch plan with prerequisites.
  - **Failure:** Block release on cycles, missing entries, or a library depending on the final dependencies BOM.
- [ ] **TOP-04 — Select one release flow and class**
  - **Action:** Choose catalog-train snapshot, routine snapshot, stable release, or the appropriate dependencies/repo train class from current scope.
  - **Evidence:** Selected flow/class with rationale and retained-version decisions.
  - **Failure:** Stop when multiple flows remain plausible or external version semantics are unconfirmed.
- [ ] **TOP-05 — Validate incremental train transitions**
  - **Action:** Require public upstream artifacts before stable references, update dependencies only to published versions, and keep future work on explicit next snapshots.
  - **Evidence:** Central HTTP/POM proof and exact source/consumer version transitions.
  - **Failure:** Never reference a future stable version or expose the final BOM before all internal references are public.

## Flows

### Catalog Train Snapshot

Pin `catalog/YYYY-MM-DD-NN`; validate consumers through supported catalog
path/ref properties; resolve without `mavenLocal()`; run affected compile/tests
and required Nightly/full. Before candidate-ready, run the complete
cross-repository publication contract in `publication-pom-gate.md`; the train's
own no-publication status does not make downstream Maven models N/A. Publish
snapshots in DAG order; record runs and metadata. This proves readiness but does
not authorize stable release.

### Routine Snapshot

Use intended `develop` SHA, keep `snapshotVersion=` empty in source, dispatch
only declared snapshot inputs, include experimental only here, and verify
Central snapshot metadata.

### Stable Release

Refresh checklist; prove complete selected state by snapshots; confirm class;
compute DAG batches; require upstream Central HTTP 200 when consumed; pass
preflight/hold before dispatch.

## Dependencies Train Classes

- `dependencies-major-train`: every stable publishable repo gets a new release;
  experimental excluded.
- `dependencies-minor-train`: coordinated feature/compatibility train; retained
  stable versions allowed when intentional and Central-visible.
- `dependencies-patch-train`: selective repo patches; unchanged public versions
  remain.
- `dependencies-only`: external/plugin/BOM metadata change with all internal
  refs retained stable and non-SNAPSHOT.
- `repo-release`: one internal repo release independent of final BOM.

Confirm major/minor/patch when external version contracts change; recommend
with evidence first.

## Incremental Internal Train

Release one repo, verify BOM plus representative module POMs, then update
dependencies `develop` to that stable version. If post-release work is needed,
open/publish its next snapshot line and point direct active consumers there;
never reference a future stable version. Do not publish the final dependencies
BOM or update Maven BOM consumers until that BOM itself is public. Before final
BOM, every managed internal reference must be stable and Central-visible.
