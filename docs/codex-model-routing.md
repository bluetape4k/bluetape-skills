# Codex and OMX model settings (manual reference)

English | [한국어](codex-model-routing.ko.md)

This guide shows how to manually select `gpt-6-luna` and `max` for a Codex user default and current OMX agent roles. It is an optional reference, not a required Bluetape setting or a performance recommendation. The Bluetape Skills installer does not apply these settings.

Before changing your files, confirm that your signed-in account, workspace, and Codex client expose the model and reasoning level. Availability can differ by surface and may change. Keep a backup, merge only the keys you want into existing files, and preserve unrelated settings.

## Set the Codex user default

By default, Codex reads `~/.codex/config.toml`. If you set `CODEX_HOME`, use `$CODEX_HOME/config.toml` instead. Add or update these root-level values:

```toml
model = "gpt-6-luna"
model_reasoning_effort = "max"
```

The selected model and client must support the configured reasoning effort. Check the [Codex configuration reference](https://developers.openai.com/codex/config-reference) and [GPT-6 Luna model page](https://developers.openai.com/api/docs/models/gpt-6-luna) for current support.

## Set OMX agent-role overrides

For user-scope OMX setup, the file is `${CODEX_HOME:-$HOME/.codex}/.omx-config.json`. Project-scope setup uses its project Codex home (commonly `./.codex/.omx-config.json`). Confirm the active scope and resolved paths with `omx doctor`; do not copy personal settings into a shared repository unless that is intentional.

Merge these two objects into the existing JSON file, key by key. Keep unrelated top-level keys and any existing role entries not listed below; this example only updates the listed roles. The 22 role names below reflect the Bluetape runtime registry used for this reference as of 2026-10-17; use only roles recognized by your installed OMX version, and add newly available roles if you want the same override for them.

```json
{
  "agentModels": {
    "analyst": "gpt-6-luna",
    "architect": "gpt-6-luna",
    "code-reviewer": "gpt-6-luna",
    "code-simplifier": "gpt-6-luna",
    "critic": "gpt-6-luna",
    "debugger": "gpt-6-luna",
    "dependency-expert": "gpt-6-luna",
    "designer": "gpt-6-luna",
    "executor": "gpt-6-luna",
    "explore": "gpt-6-luna",
    "git-master": "gpt-6-luna",
    "planner": "gpt-6-luna",
    "prometheus-strict-metis": "gpt-6-luna",
    "prometheus-strict-momus": "gpt-6-luna",
    "prometheus-strict-oracle": "gpt-6-luna",
    "researcher": "gpt-6-luna",
    "scholastic": "gpt-6-luna",
    "team-executor": "gpt-6-luna",
    "test-engineer": "gpt-6-luna",
    "verifier": "gpt-6-luna",
    "vision": "gpt-6-luna",
    "writer": "gpt-6-luna"
  },
  "agentReasoning": {
    "analyst": "max",
    "architect": "max",
    "code-reviewer": "max",
    "code-simplifier": "max",
    "critic": "max",
    "debugger": "max",
    "dependency-expert": "max",
    "designer": "max",
    "executor": "max",
    "explore": "max",
    "git-master": "max",
    "planner": "max",
    "prometheus-strict-metis": "max",
    "prometheus-strict-momus": "max",
    "prometheus-strict-oracle": "max",
    "researcher": "max",
    "scholastic": "max",
    "team-executor": "max",
    "test-engineer": "max",
    "verifier": "max",
    "vision": "max",
    "writer": "max"
  }
}
```

`agentModels` and `agentReasoning` are separate from the Codex root defaults. OMX reads them as per-role overrides; `max` must also be supported by the selected model and receiving Codex surface. OMX does not automatically downgrade an unsupported role effort. See the [OMX model/config routing reference](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/docs/reference/omx-config-schema-routing.md) for the current schema and precedence rules.

OMX setup manages more than role overrides. Depending on delivery mode and scope, it can create or refresh prompts, skills, native agents, `config.toml`, hooks, `AGENTS.md`, and `.omx` runtime/HUD files. It can also persist scope and delivery-mode choices, archive or remove legacy OMX-managed prompts/skills in plugin mode, update `developer_instructions`, and change setup-owned Team/notification integration. Read the [OMX setup guide](https://github.com/Yeachan-Heo/oh-my-codex/blob/main/skills/omx-setup/SKILL.md) and preview the exact scope before applying changes:

```bash
omx setup --dry-run --scope user
# Or, for project-local settings:
omx setup --dry-run --scope project
```

Review the preview for creates, updates, archives, removals, and persisted choices; proceed only if they are all intended. Use the same delivery mode for preview and application, adding `--plugin` or `--legacy` to both commands when selecting one explicitly. Then run the matching scope; `--force` overwrites or reinstalls managed artifacts:

```bash
omx setup --scope user --force
# Or, for project-local settings:
omx setup --scope project --force
omx doctor
```

Run setup from the same shell and project context used to launch OMX. `omx doctor` helps inspect the resulting installation and resolved scope.

## Verify and maintain

1. Confirm the effective Codex home and OMX setup scope.
2. Confirm `gpt-6-luna` and `max` are accepted by the exact account, workspace, and client you use.
3. Check that the installed OMX role registry matches the keys you configured.
4. Revisit the official references after upgrading Codex or OMX; model availability and role registries can change.

The examples are manual. `./scripts/install.sh` installs the Bluetape skill folders under `${CODEX_HOME:-$HOME/.codex}/skills`; it does not write `config.toml` or `.omx-config.json`.
