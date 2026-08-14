# AGENTS.md - bluetape-skills

## Guidance hierarchy

Before applying this repository overlay, read and follow the guidance in this
order:

1. User scope: `${CODEX_HOME:-$HOME/.codex}/AGENTS.md`.
2. Workspace scope: `/Users/debop/work/bluetape4k/.github/docs/workspace/AGENTS.md`.

Apply both broader scopes before repository-specific rules.

Read and follow the workspace guidance in `../AGENTS.md` first. This file is a
thin repository-specific overlay.

## Repository Authority

- This repository is the public distribution surface for reviewed, stable
  Bluetape skills and their reusable resources.
- It is independent from a maintainer's live `${CODEX_HOME:-~/.codex}/skills`
  tree and from the private chezmoi source that manages that maintainer's
  machine configuration.
- Do not treat this checkout as the source of truth for live skills or
  dotfiles, and do not automatically synchronize changes in either direction.
- Promote a stabilized skill version into this repository through an explicit
  review and release step. Adopting a repository change into live skills or
  dotfiles is a separate, explicit maintenance task.
- Keep personal configuration, hooks, memories, runtime state, secrets, plugin
  caches, and machine-specific compatibility resources outside this public
  bundle.

## Branch And Release Boundary

- Use `develop` for reviewed distribution updates.
- Reserve `main` for stable release promotion.
- Treat release tags as immutable public artifacts.
