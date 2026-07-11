# Bluetape Skill Taxonomy

Use this reference only for skill catalog maintenance: add, rename, alias,
archive, or routing changes. `bluetape-workflow` remains the runtime router.

## Canonical Surfaces

| Category | Canonical skill | Role |
|---|---|---|
| Router | `bluetape-workflow` | Classify Type A/B/C/D/E/P/F and route to the narrowest workflow. |
| Type A | `bluetape-full-feature` | Full design, implementation, verification, review, and PR lifecycle. |
| Type B | `bluetape-fast-track` | Small feature or API additions with lighter gates. |
| Type C | `bluetape-bugfix` | Reproduce, root-cause, fix, verify, and report a defect. |
| Type E | `bluetape-maintenance` | Docs, config, AGENTS, workflow, skill, and guidance cleanup. |
| Type P | `bluetape-publish-jvm` | JVM/Maven snapshot, release, catalog train, and release topology. |
| Type P Go | `bluetape-publish-go` | Go tag, milestone, changelog, and GitHub Release workflow. |
| Type F | `bluetape-self-improve` | Benchmark-gated iterative improvement. |
| Blog | `bluetape-writer` | Blog/article writing, localization, and validation. |
| Diagram | `bluetape-diagram` | README/docs/blog diagrams and charts. |
| Kotlin guidance | `bluetape-kotlin-patterns` | Kotlin implementation, tests, modules, Spring, and review rules. |
| Go guidance | `bluetape-go-patterns` | Go implementation, tests, concurrency, API, and review rules. |
| Rust guidance | `bluetape-rs-patterns` | Rust implementation, tests, async, SQL, Cargo, and review rules. |
| Python guidance | `bluetape-py-patterns` | Python implementation, tests, async, packaging, and review rules. |

## Naming and Alias Policy

- Verify the live and managed catalogs before documenting an alias as current.
- Keep a compatibility alias only while an installed caller or demonstrated
  current user habit still depends on it. Historical documents alone do not
  justify an alias.
- An alias contains only a pointer to the canonical skill and its removal
  condition; durable guidance belongs in the canonical skill or its references.
- Cross-language workflow names use `bluetape-<domain>`; language-specific
  names use `bluetape-<language>-<domain>`.
- Repository, package, organization, and GNO collection identifiers retain
  their established `bluetape4k-*` names unless their own identity changes.
- Do not recreate historical aliases merely because an old document names them.
- Keep language-specific code guidance separate where failure modes differ; do
  not duplicate Type A/B/C workflow state machines in language skills.

Historical names such as `bluetape4k-patterns`, `bluetape4k-design`,
`bluetape4k-bugfix-workflow`, and `bugfix-workflow` are not current aliases
unless catalog inspection proves that they are installed again. See
`wiki/pages/bluetape-skill-name-migration.md` for the current migration map.

## Validation

1. Search managed and live skills for the old and new names.
2. Verify every documented canonical skill exists in both catalogs.
3. Verify each retained alias resolves to exactly one canonical skill.
4. Apply managed changes and prove source/live parity.
5. Run `$self-audit` and the targeted broken-reference check.
