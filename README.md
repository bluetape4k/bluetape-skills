# Bluetape Skills

English | [한국어](README.ko.md)

Installable, canonical [Codex skills](https://developers.openai.com/codex/skills/) for Bluetape development workflows. Each skill is shipped with the references, templates, scripts, and agent prompts it needs; retired aliases and personal runtime state are intentionally not distributed.

## What gets shared

The repository is a portable public bundle, not a copy of a maintainer's Codex home. It includes the complete reusable skill units while keeping user-specific configuration and runtime data outside the distribution boundary.

[![Public bundle boundary: canonical Bluetape skills and their reusable resources are included, while personal runtime state is excluded](docs/images/bluetape-skills-public-bundle-boundary-01.png)](docs/images/bluetape-skills-public-bundle-boundary-01.svg)

## Install

```bash
git clone https://github.com/bluetape4k/bluetape-skills.git
cd bluetape-skills
./scripts/validate.sh
./scripts/install.sh
```

The installer writes to `${CODEX_HOME:-~/.codex}/skills`. It refuses to overwrite an existing canonical skill. Use `--force` only when you want a timestamped backup of the installed skill before replacement.

```bash
./scripts/install.sh --dry-run
./scripts/install.sh --codex-home "$HOME/.codex"
./scripts/install.sh --force
```

Restart Codex after installation so the new skills are discovered.

## Update

```bash
git pull --ff-only
./scripts/validate.sh
./scripts/install.sh --force
```

Review `git log` and `git diff` before forcing an update if you have local changes to installed skills.

## Use

Start with `$bluetape-workflow` for a Bluetape ecosystem task. It classifies the work and routes it to the lightest appropriate lane.

[![Workflow router: a Bluetape task is classified and routed to the matching skill lane](docs/images/bluetape-workflow-type-router-01.png)](docs/images/bluetape-workflow-type-router-01.svg)

| Need | Skill |
| --- | --- |
| Reproducible defect | `$bluetape-bugfix` |
| Small, bounded change | `$bluetape-fast-track` |
| New module, dependency, or broad API work | `$bluetape-full-feature` |
| Kotlin/JVM implementation | `$bluetape-kotlin-patterns` |
| Go, Python, or Rust work | `$bluetape-go-patterns`, `$bluetape-py-patterns`, `$bluetape-rs-patterns` |
| Documentation and localization | `$bluetape-writer` |
| Diagrams and charts | `$bluetape-diagram` |
| JVM or Go publishing | `$bluetape-publish-jvm`, `$bluetape-publish-go` |

The `skills/manifest.json` file is the machine-readable inventory. Skill folders include their own `SKILL.md` and referenced material, so copy the complete folder rather than only `SKILL.md`.

## Guides

- [Sharing and installing Bluetape skills](https://bluetape4k.github.io/blog/bluetape-skills-sharing/) explains the public bundle, source ownership, installation, updates, and collaboration model.
- [Using the Bluetape workflow](https://bluetape4k.github.io/blog/bluetape-skills-workflow-guide/) explains task classification, checklist gates, staged multi-perspective review, and the P0/P1 zero-blocker loop.

The guides contain the detailed source-sync, execution-lane, and 7-Tier review diagrams that complement this quick-start README.

## What is deliberately excluded

This public bundle contains only canonical reusable guidance. It does not include user preferences, memories, local rules, hooks, configuration, plugin caches, secrets, or compatibility aliases such as `bluetape4k-*`. That boundary keeps the bundle safe to share and prevents private machine state from becoming part of another developer's setup.

## Contribution and release policy

This repository is a distributable mirror of the maintained canonical skill source. Open an issue for a correction or proposal; maintainers review it against the source and export it in a later bundle update. Do not rely on retired skill names in new documentation or automation.

## Verification

Run `./scripts/validate.sh` after cloning or updating. It verifies the canonical inventory, required front matter, and the absence of private/runtime payload.

## License

MIT. See [LICENSE](LICENSE).
