# GitHub Release Note Quality

Release notes are public English consumer documentation. Apply the parent
checklist contract.

- [ ] **NOTE-01 — State the release purpose**
  - **Action:** Start with `## Highlights` covering purpose, train context, and feature/maintenance/patch/corrective class.
  - **Evidence:** Rendered Highlights section with the exact release identity.
  - **Failure:** Reject link-only or checklist-only notes.
- [ ] **NOTE-02 — Organize for readers**
  - **Action:** Group changes by features, runtime, security, compatibility, build/CI, docs, and migration impact as applicable.
  - **Evidence:** Meaning-based sections with actual change explanations rather than a chronological PR dump.
  - **Failure:** Rewrite opaque or trace-only content before publication.
- [ ] **NOTE-03 — Preserve traceability**
  - **Action:** Explain each change first, then add related issue/PR links on one physical line.
  - **Evidence:** `Related:` lines for available traceability.
  - **Failure:** Repair missing or misleading links without replacing the explanation.
- [ ] **NOTE-04 — Identify corrective targets**
  - **Action:** For a corrective release, name the bad prior version and the exact version consumers should use.
  - **Evidence:** Explicit migration target, or concrete evidence that the release is not corrective.
  - **Failure:** Do not publish ambiguous corrective guidance.
- [ ] **NOTE-05 — Verify the live final body**
  - **Action:** End with the verified Full Changelog link using the actual previous tag and inspect the live release body.
  - **Evidence:** `gh release view ... --json body` showing Highlights, related links when available, and correct final compare range.
  - **Failure:** Keep release-note closeout blocked until the live body matches the checked draft.

Verify the live body with `gh release view <tag> -R <owner>/<repo> --json body`:
Highlights present, related links present where available, and final compare
range correct.
