# Changelog

All notable changes to Bluetape Skills are documented in this file.

## [1.2.1] - 2026-07-17

### Added

- A fail-closed SVG text normalizer that removes renderer-sensitive text halos
  and preserves lane and relationship labels in CairoSVG PNG output.
- Semantic token highlighting for explicit code snippets, with regression
  coverage for CSS cascade, inline attributes, token styles, and idempotence.

### Changed

- `$bluetape-diagram` now requires `text_hazards=0` and
  `code_without_highlight=0` before canonical PNG rendering.

## [1.2.0] - 2026-07-17

### Added

- Automatic `$bluetape-diagram` connector checks for relationship-label collisions and shared connector segments.

### Changed

- Connector audit failures now use `data-from`/`data-to` relationship names when available, apply SVG affine transforms, and keep disconnected path subpaths separate.

## [1.1.0] - 2026-07-14

### Added

- Phase 2 native workflow runtime with guarded run/lane lifecycle commands, topology-based completion, liveness handling, receipt-backed recovery, handoff, and immutable live reports.
- Workflow manifest 1.1, receipt/topology/liveness contracts, and regression coverage for coordinator lifecycle, recovery, security, locking, scale, and rendered layouts.

### Changed

- Synchronized all 14 canonical Bluetape skills so router, maintenance, publishing, bug-fix, fast-track, full-feature, and self-improvement gates share the current workflow contract.
- Expanded bundle validation to check the manifest inventory, rendered executable names, declared external companion skills, workflow contracts, and the complete workflow test suite.
- Updated English and Korean installation, update, runtime, and verification guidance for the 1.1.0 bundle.

### Security

- Hardened owner fencing, filesystem containment, permission checks, stale-lock recovery, receipt verification, and recovery-run provenance.

## [1.0.0] - 2026-07-11

### Added

- First stable public bundle of 14 canonical Bluetape development skills with their references, templates, scripts, and agent prompts.
- Safe install and update scripts with private runtime state and retired aliases excluded from distribution.
- Bilingual installation and usage guidance, including the public bundle boundary, workflow router, and 7-Tier review gates.
- Validation for canonical inventory, required skill front matter, and forbidden private or secret-like payloads.

[1.0.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.0.0
[1.1.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.1.0
[1.2.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.0
[1.2.1]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.1
