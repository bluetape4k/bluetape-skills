# Cross-Repository Publication POM Gate

Apply this gate to every catalog train or shared version-authority change that
can alter a JVM library publication. A train that publishes no artifact can
still generate invalid downstream Maven metadata; Gradle configuration,
resolution, build, and representative POM checks do not replace this gate.

## Publisher Inventory

The executable inventory is `PUBLISHERS` in
`bluetape4k-dependencies/scripts/verify-publication-poms.py`. Reconcile it with
current publish workflows before each train. The expected publishers are:

- `bluetape4k-dependencies`
- `bluetape4k-projects`
- `bluetape4k-aws`
- `bluetape4k-exposed`
- `bluetape4k-graph`
- `bluetape4k-image`
- `bluetape4k-javers`
- `bluetape4k-leader`
- `bluetape4k-text`

`bluetape4k-experimental`, workshops, and applications remain catalog
consumers but are not publication-POM targets unless they gain a real publish
workflow. Missing or extra live publishers block candidate-ready until the
inventory and rationale are corrected.

## Exact Candidate Command

From `bluetape4k-dependencies`, validate ordinary sibling checkouts with:

```bash
scripts/verify-publication-poms.py --workspace .. --summary
```

For candidate worktrees, use the same exact path/branch/HEAD map as the catalog
adoption guard:

```bash
scripts/sync-shared-versions.py \
  --repository-map <candidate-worktrees.json> --check --summary
scripts/verify-publication-poms.py \
  --repository-map <candidate-worktrees.json> --summary
```

The verifier must configure each publisher against the candidate central
catalog, regenerate all publication POMs, structurally audit every POM, and
build every Maven effective model. `--skip-generation` is diagnostic-only and
is not candidate-ready evidence unless generation already passed for the exact
same repository SHAs and catalog bytes.

## Maven-Shaped Version Rules

- Every `dependencyManagement` entry requires a version, including imported
  BOMs. A Gradle versionless alias is not evidence that the published entry is
  managed.
- A regular dependency may omit its direct version only when the same POM has
  a versioned management entry for that coordinate or a versioned imported BOM
  actually manages it.
- Structural presence of any versioned BOM is only a preliminary allowance;
  Maven effective-model validation is authoritative for whether it manages the
  dependency coordinate.
- Generated publication POMs must not contain Maven profiles. Inactive profiles
  escape the default reactor model and can hide consumer-only version defects;
  move publication dependency management to the unconditional model.
- Invalid XML, stale or missing publisher output, publisher registry/workflow
  drift, duplicate/broken Maven models, Gradle generation failure, or any
  uncovered publisher fails the gate.

Record repository/catalog SHAs, publisher counts, POM/dependency/model counts,
and the final zero-failure summary in the durable train checklist. Do not mark
the train candidate-ready with representative-only or stale generated output.
