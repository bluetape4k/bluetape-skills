# Stable Preflight and Dispatch

## Preflight Checklist

- [ ] **PRE-01 — Confirm release eligibility**
  - **Action:** Verify repository class and requested version class from current source and topology.
  - **Evidence:** Eligible class, exact version, and authority.
  - **Failure:** Stop or route to the correct snapshot/consumer flow.
- [ ] **PRE-02 — Confirm live closeout**
  - **Action:** Verify the milestone plus release-affecting issues and PRs are closed or dispositioned.
  - **Evidence:** Live milestone/issue/PR results.
  - **Failure:** Block dispatch while relevant work remains open.
- [ ] **PRE-03 — Validate release documentation**
  - **Action:** Verify the target changelog section has a date and reader-usable summary.
  - **Evidence:** Exact changelog path and target section.
  - **Failure:** Repair public release context before dispatch.
- [ ] **PRE-04 — Validate candidate execution**
  - **Action:** Verify required Nightly/full and matching-state snapshot checks passed or have an explicit authorized waiver.
  - **Evidence:** Run URLs/conclusions, SHAs, catalog state, and waiver authority when applicable.
  - **Failure:** Failed, missing, mismatched, or unauthorized waived execution blocks dispatch.
- [ ] **PRE-05 — Match source version state**
  - **Action:** Verify `snapshotVersion=` is empty and requested version matches base/tag inputs.
  - **Evidence:** Source values and planned tag/input.
  - **Failure:** Repair version drift before continuing.
- [ ] **PRE-06 — Verify internal release references**
  - **Action:** Check every internal release reference is public and non-SNAPSHOT.
  - **Evidence:** Central HTTP/POM proof per internal reference.
  - **Failure:** Wait for public artifacts or correct the reference.
- [ ] **PRE-07 — Audit generated BOM and POMs**
  - **Action:** Scan for SNAPSHOTs, Maven-shaped dependency-version defects, wrong license, and leaked non-publishable artifacts. For a catalog/shared-version train, run the exact cross-repository contract in `publication-pom-gate.md` rather than representative POM sampling.
  - **Evidence:** Generated BOM/POM paths, complete publisher inventory, structural audit, Maven effective-model output, and clean audit result.
  - **Failure:** Missing publisher coverage, a versionless dependency-management entry, an unmanaged regular dependency, or a failed Maven model blocks the train and publication.
- [ ] **PRE-08 — Validate signing and publishing diagnostics**
  - **Action:** Run the repository's declared signing/publishing diagnostics.
  - **Evidence:** Fresh successful diagnostic output.
  - **Failure:** Stop; never test signing by irreversible publication.
- [ ] **PRE-09 — Pin the artifact matrix**
  - **Action:** Enumerate every expected group/artifact/version and representative POM.
  - **Evidence:** Complete expected matrix used for post-dispatch verification.
  - **Failure:** Do not dispatch an unknown publication surface.
- [ ] **PRE-10 — Re-read workflow inputs**
  - **Action:** Inspect `workflow_dispatch.inputs` in the exact target YAML immediately before dispatch.
  - **Evidence:** Workflow path/SHA and declared required/optional input set.
  - **Failure:** Omit unsupported optional fields and stop when a required selected-flow input is absent.

Record snapshot repo/SHA, catalog ref/path, local commands, Nightly and snapshot
URLs, metadata timestamp, and retained-version decisions. Gradle `help
--refresh-dependencies` is the minimum resolution check; add affected compile
and tests, normally including `compileTestKotlin`.

## Dispatch

Read `workflow_dispatch.inputs` from the target YAML. Pass only declared
`version`, `snapshotVersion`, `catalogRef`, `diagnoseSigning`, or repo-specific
fields. Omit unsupported optional fields; stop if a required selected-flow input
is absent. Do not infer schema from another repo or memory.

Immediately before dispatch rerun the checklist hold. After dispatch, monitor
the exact run and verify public artifacts independently.

## Failure Guards

- SNAPSHOT drift in catalog/POM/release branch.
- missing generated dependency version or wrong license.
- non-publishable module leakage.
- hand-written raw-JMH harness replacing `kotlinx.benchmark`.
- Central Portal accepted while public Maven returns 404.
- wrong tag recovery without explicit safe authority.
- undeclared workflow inputs.
- catalog ref confused with consumer BOM version.
- zsh script variable named `path`; use `artifact_path`.

On failure, stop and propose the smallest corrective flow. Never classify a
successful workflow alone as a published artifact.
