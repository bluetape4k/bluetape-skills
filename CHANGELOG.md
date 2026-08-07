# Changelog

All notable changes to Bluetape Skills are documented in this file.

## [Unreleased]

## [1.3.1] - 2026-08-07

### 변경

- 한국 개발자가 주 독자인 기준으로 GitHub issue/PR 제목·본문·댓글과 push 대상 commit message를 한국어로 작성하도록 운영 규칙을 통일했습니다.
- KDoc, RustDoc, Go doc comment, Python docstring 등 독자가 읽는 코드 주석을 한국어로 작성하도록 기준을 정리했습니다.
- `WIP.md`, `docs/**/*.md`, `CHANGELOG.md`, release notes는 한국어로 작성하고, `AGENTS.md`, `CLAUDE.md`, `SKILL.md` 등 AI-facing 운영 문서는 영어로 유지하도록 경계를 명확히 했습니다.
- 코드 식별자, 명령, URL, 정확한 오류 메시지, machine-readable token은 원문을 보존하도록 예외를 명시했습니다.

## [1.3.0] - 2026-07-31

### Changed

- Simplified the canonical workflow contracts for GPT-5.6 by assigning shared
  semantics to one owner and keeping leaf skills focused on type-specific
  deltas.
- Updated `$bluetape-diagram` with a reusable workflow reference and clearer
  validation boundaries for deterministic public diagrams.
- Strengthened `$bluetape-writer` Korean register and naturalness guidance
  without retaining article-specific examples in the reusable reference.
- Kept new and meaningfully updated Kotlin guidance Korean-first across the
  canonical Kotlin and full-feature skill surfaces.

## [1.2.2] - 2026-07-27

### Added

- Added reusable workflow lessons for repository-practice discovery, hook
  target resolution, receipt lifecycle recovery, public-bundle test
  portability, and completion-gate discipline.
- Added operational logging requirements to the Go, Kotlin, Python, and Rust
  implementation patterns.

### Changed

- Adopted `develop` as the default integration branch and reserved `main` for
  reviewed stable-release promotion only.
- Expanded `$bluetape-diagram` guidance for DOM-native HTML/CSS charts,
  deterministic capture, bilingual fonts, and localized visual assets.
- Strengthened `$bluetape-workflow` worktree isolation, GNO fallback,
  delegation deadlines, run-command contracts, and failure-resolution rules.
- Clarified `$bluetape-writer` language selection, audience register, and
  Korean naturalness checks.

### Fixed

- Allowed append-only coordinator completion after a failed review lane is
  explicitly linked to a completed correction or exact-head rereview lane,
  while unresolved and invalid failure-resolution claims remain blocking.
- Made source-only workflow contract tests skip explicitly when private
  `AGENTS.md` and external companion skills are absent from the public bundle.

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
[1.2.2]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.2.2
[1.3.1]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.3.1
[1.3.0]: https://github.com/bluetape4k/bluetape-skills/releases/tag/v1.3.0
[Unreleased]: https://github.com/bluetape4k/bluetape-skills/compare/v1.3.1...develop
