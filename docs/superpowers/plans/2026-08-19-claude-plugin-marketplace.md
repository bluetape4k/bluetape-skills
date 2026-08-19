# Claude Code Plugin Marketplace Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add Claude Code plugin marketplace support to this repository without disturbing its existing Codex skill distribution.

**Architecture:** Add a `.claude-plugin/` directory at the repository root containing `plugin.json` and `marketplace.json`. The repo root doubles as the plugin root, so the existing `skills/` directory is reused unmodified via Claude Code's default skill auto-discovery (no `skills` field needed in `plugin.json`). Extend `scripts/validate.sh` with a validation step for the two new JSON files. Document the new install path in both READMEs and note it in CHANGELOG.md.

**Tech Stack:** Bash, Python 3 (`json` stdlib), `claude` CLI (`claude plugin validate`), existing `rg`/`uv` toolchain already required by `validate.sh`.

**Spec:** `docs/superpowers/specs/2026-08-19-claude-plugin-marketplace-design.md`

## Global Constraints

- Do not modify `skills/*/SKILL.md`, `skills/manifest.json`, `scripts/install.sh`, or `AGENTS.md`.
- All 14 skills stay as a single unified plugin named `bluetape-skills`.
- `plugin.json` and `marketplace.json` both use version string `1.3.4`, matching the current CHANGELOG/tag baseline (do not bump the repo's actual release version as part of this work).
- `owner.name` is `bluetape4k`; `owner.url` is `https://github.com/bluetape4k/bluetape-skills`.
- `marketplace.json`'s single plugin entry uses `"source": "./"`.
- `validate.sh` must keep working in environments without the `claude` CLI installed (e.g., CI) by falling back to a plain JSON-validity/required-field check.
- Every new user-facing doc snippet must appear in both `README.md` (English) and `README.ko.md` (Korean).

---

### Task 1: Add `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`
- Test: manual JSON validity check via `python3 -m json.tool` (this task has no automated test suite yet — Task 2 wires it into `validate.sh`)

**Interfaces:**
- Consumes: nothing from earlier tasks (first task).
- Produces: two files at fixed repo-relative paths (`.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`) that Task 2's validation step reads by path, and that Task 3's README snippets reference by the plugin name `bluetape-skills` and marketplace name `bluetape-skills`.

- [ ] **Step 1: Create the `.claude-plugin` directory and `plugin.json`**

Create `.claude-plugin/plugin.json` with exactly this content:

```json
{
  "name": "bluetape-skills",
  "displayName": "Bluetape Skills",
  "version": "1.3.4",
  "description": "Installable, canonical Codex/Claude skills for Bluetape development workflows.",
  "author": {
    "name": "bluetape4k"
  },
  "homepage": "https://github.com/bluetape4k/bluetape-skills",
  "repository": "https://github.com/bluetape4k/bluetape-skills",
  "license": "MIT",
  "keywords": ["bluetape", "workflow", "kotlin", "codex"]
}
```

Note: no `skills` field — Claude Code auto-discovers the top-level `skills/`
directory when the field is omitted.

- [ ] **Step 2: Create `marketplace.json`**

Create `.claude-plugin/marketplace.json` with exactly this content:

```json
{
  "name": "bluetape-skills",
  "owner": {
    "name": "bluetape4k",
    "url": "https://github.com/bluetape4k/bluetape-skills"
  },
  "description": "Bluetape Skills marketplace",
  "version": "1.3.4",
  "plugins": [
    {
      "name": "bluetape-skills",
      "source": "./",
      "description": "Canonical Bluetape workflow, language, and publishing skills",
      "version": "1.3.4"
    }
  ]
}
```

- [ ] **Step 3: Validate both files are well-formed JSON**

Run:

```bash
python3 -m json.tool .claude-plugin/plugin.json >/dev/null && echo "plugin.json OK"
python3 -m json.tool .claude-plugin/marketplace.json >/dev/null && echo "marketplace.json OK"
```

Expected: both print `OK`, no `json.decoder.JSONDecodeError`.

- [ ] **Step 4: Run `claude plugin validate` against the repo root**

Run:

```bash
claude plugin validate . --strict
```

Expected: `✔ Validation passed` (or "passed with warnings" — if warnings appear, read them; fix anything that indicates a wrong field name or missing required field, but do not add fields beyond what's specified above just to silence a stylistic warning).

- [ ] **Step 5: Commit**

```bash
git add .claude-plugin/plugin.json .claude-plugin/marketplace.json
git commit -m "feat: add Claude Code plugin marketplace manifests"
```

---

### Task 2: Extend `scripts/validate.sh` with plugin/marketplace validation

**Files:**
- Modify: `scripts/validate.sh`

**Interfaces:**
- Consumes: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (from Task 1), at paths `$repo_root/.claude-plugin/plugin.json` and `$repo_root/.claude-plugin/marketplace.json`.
- Produces: `validate.sh` exits non-zero with a clear stderr message if either file is missing, invalid JSON, or missing a required field. This is the only consumer of the new files within the validation pipeline; no later task depends on new interfaces from this one.

- [ ] **Step 1: Read the current end of `scripts/validate.sh`**

The file currently ends with:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest -q "$workflow_root/tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s "$diagram_root/tests" \
  -p 'test_*.py'

echo "PASS: ${#expected_skills[@]} canonical skills, workflow contracts, diagram audits, tests, and public bundle boundaries are valid."
```

- [ ] **Step 2: Insert a new validation block before the final `echo "PASS: ..."` line**

Replace:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest -q "$workflow_root/tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s "$diagram_root/tests" \
  -p 'test_*.py'

echo "PASS: ${#expected_skills[@]} canonical skills, workflow contracts, diagram audits, tests, and public bundle boundaries are valid."
```

with:

```bash
PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest -q "$workflow_root/tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s "$diagram_root/tests" \
  -p 'test_*.py'

plugin_manifest="$repo_root/.claude-plugin/plugin.json"
marketplace_manifest="$repo_root/.claude-plugin/marketplace.json"

[[ -f "$plugin_manifest" ]] || { echo "missing plugin manifest: $plugin_manifest" >&2; exit 1; }
[[ -f "$marketplace_manifest" ]] || { echo "missing marketplace manifest: $marketplace_manifest" >&2; exit 1; }

python3 - "$plugin_manifest" "$marketplace_manifest" <<'PY'
import json
import sys
from pathlib import Path

plugin_path, marketplace_path = sys.argv[1], sys.argv[2]

plugin = json.loads(Path(plugin_path).read_text(encoding="utf-8"))
if not plugin.get("name"):
    raise SystemExit("plugin.json missing required field: name")

marketplace = json.loads(Path(marketplace_path).read_text(encoding="utf-8"))
if not marketplace.get("name"):
    raise SystemExit("marketplace.json missing required field: name")
if not marketplace.get("owner", {}).get("name"):
    raise SystemExit("marketplace.json missing required field: owner.name")
plugins = marketplace.get("plugins")
if not isinstance(plugins, list) or not plugins:
    raise SystemExit("marketplace.json missing non-empty plugins array")
for entry in plugins:
    if not entry.get("name") or not entry.get("source"):
        raise SystemExit("marketplace.json plugin entry missing name or source")
PY

if command -v claude >/dev/null; then
  claude plugin validate "$repo_root" --strict
else
  echo "claude CLI not found; skipped 'claude plugin validate' (JSON/required-field checks above still ran)"
fi

echo "PASS: ${#expected_skills[@]} canonical skills, workflow contracts, diagram audits, tests, plugin/marketplace manifests, and public bundle boundaries are valid."
```

- [ ] **Step 3: Run the full validation script**

Run: `./scripts/validate.sh`

Expected: script completes and prints
`PASS: 14 canonical skills, workflow contracts, diagram audits, tests, plugin/marketplace manifests, and public bundle boundaries are valid.`
with no non-zero exit.

- [ ] **Step 4: Verify failure detection works**

Temporarily corrupt the marketplace file, confirm validate.sh fails, then restore it:

```bash
cp .claude-plugin/marketplace.json /tmp/marketplace.json.bak
python3 -c "import json,pathlib; d=json.loads(pathlib.Path('.claude-plugin/marketplace.json').read_text()); del d['owner']; pathlib.Path('.claude-plugin/marketplace.json').write_text(json.dumps(d))"
./scripts/validate.sh; echo "exit code: $?"
cp /tmp/marketplace.json.bak .claude-plugin/marketplace.json
rm /tmp/marketplace.json.bak
```

Expected: the middle run prints `marketplace.json missing required field: owner.name` to stderr and exits non-zero; after restoring, `git status --short` shows `.claude-plugin/marketplace.json` unchanged (clean).

- [ ] **Step 5: Commit**

```bash
git add scripts/validate.sh
git commit -m "test: validate Claude plugin/marketplace manifests in validate.sh"
```

---

### Task 3: Document the Claude Code install path in both READMEs and CHANGELOG

**Files:**
- Modify: `README.md`
- Modify: `README.ko.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: plugin name `bluetape-skills` and marketplace name `bluetape-skills` (from Task 1).
- Produces: nothing consumed by later tasks (final task).

- [ ] **Step 1: Add a new subsection to `README.md` right after the existing "Install" section**

Find this point in `README.md` (end of the "Install" section, right before the "## Update" heading):

```
Restart Codex after installation so the new skills are discovered.

To follow unreleased changes, clone the default `develop` branch by omitting the `--branch v1.3.4 --depth 1` options. The `main` branch is reserved for reviewed stable-release promotion. Published versions and downloadable bundles are available from [GitHub Releases](https://github.com/bluetape4k/bluetape-skills/releases).

## Update
```

Insert a new subsection between the `develop` paragraph and `## Update`:

```markdown
Restart Codex after installation so the new skills are discovered.

To follow unreleased changes, clone the default `develop` branch by omitting the `--branch v1.3.4 --depth 1` options. The `main` branch is reserved for reviewed stable-release promotion. Published versions and downloadable bundles are available from [GitHub Releases](https://github.com/bluetape4k/bluetape-skills/releases).

### Install via Claude Code plugin marketplace

The same skills are also published as a Claude Code plugin. From inside Claude Code:

```
/plugin marketplace add bluetape4k/bluetape-skills
/plugin install bluetape-skills@bluetape-skills
```

The skills' `$skill-name` trigger phrasing in each `SKILL.md` is Codex-style notation; Claude Code recognizes the same skills by name automatically, so no rewrite is needed.

## Update
```

- [ ] **Step 2: Add the matching subsection to `README.ko.md`**

Find this point in `README.ko.md` (end of the "설치" section, right before the "## 업데이트" heading):

```
설치 뒤에는 Codex를 다시 시작해야 새 skill을 인식합니다.

아직 릴리스되지 않은 변경까지 따라가려면 `--branch v1.3.4 --depth 1` 옵션을 빼고 기본 브랜치인 `develop`을 복제하세요. `main`은 검토를 거친 안정 릴리스 승격에만 사용합니다. 공개 버전과 다운로드 가능한 묶음은 [GitHub Releases](https://github.com/bluetape4k/bluetape-skills/releases)에서 확인할 수 있습니다.

## 업데이트
```

Insert:

```markdown
설치 뒤에는 Codex를 다시 시작해야 새 skill을 인식합니다.

아직 릴리스되지 않은 변경까지 따라가려면 `--branch v1.3.4 --depth 1` 옵션을 빼고 기본 브랜치인 `develop`을 복제하세요. `main`은 검토를 거친 안정 릴리스 승격에만 사용합니다. 공개 버전과 다운로드 가능한 묶음은 [GitHub Releases](https://github.com/bluetape4k/bluetape-skills/releases)에서 확인할 수 있습니다.

### Claude Code plugin marketplace로 설치

동일한 skill 묶음을 Claude Code plugin으로도 배포합니다. Claude Code 안에서 다음을 실행하세요.

```
/plugin marketplace add bluetape4k/bluetape-skills
/plugin install bluetape-skills@bluetape-skills
```

각 `SKILL.md`에 있는 `$skill-name` 트리거 표기는 Codex 표기법입니다. Claude Code도 동일한 이름으로 스킬을 자동 인식하므로 별도로 고칠 필요가 없습니다.

## 업데이트
```

- [ ] **Step 3: Add a CHANGELOG.md entry**

Find the top of `CHANGELOG.md`:

```
# 변경 기록

Bluetape Skills의 주요 변경 사항을 이 파일에 기록합니다.

## [Unreleased]

## [1.3.4] - 2026-08-13
```

Replace with:

```
# 변경 기록

Bluetape Skills의 주요 변경 사항을 이 파일에 기록합니다.

## [Unreleased]

### 추가

- `.claude-plugin/plugin.json`과 `.claude-plugin/marketplace.json`을 추가해
  Claude Code plugin marketplace(`bluetape-skills`)로도 설치할 수 있도록
  했습니다. 기존 Codex 배포 경로(`skills/`, `install.sh`, `manifest.json`)는
  변경하지 않았습니다.

## [1.3.4] - 2026-08-13
```

- [ ] **Step 4: Verify the docs render sensibly and validate.sh still passes**

Run:

```bash
./scripts/validate.sh
```

Expected: same `PASS: ...` line as Task 2 Step 3 (this task doesn't touch validation logic, only docs).

Manually skim the edited sections of `README.md` and `README.ko.md` to confirm the fenced code blocks are closed correctly (no stray triple-backtick nesting — the `/plugin marketplace add ...` example line itself is not fenced as bash so it doesn't get misread as a shell prompt).

- [ ] **Step 5: Commit**

```bash
git add README.md README.ko.md CHANGELOG.md
git commit -m "docs: document Claude Code plugin marketplace install path"
```

---

## Self-Review Notes

- **Spec coverage:** `.claude-plugin/plugin.json` + `marketplace.json` (Task 1), `validate.sh` extension (Task 2), README/README.ko/CHANGELOG updates (Task 3) — all spec sections covered. `scripts/install.sh`, `skills/manifest.json`, and `skills/*/SKILL.md` are explicitly left untouched per the spec's "변경하지 않는 파일" list, and no task modifies them.
- **No placeholders:** every step has literal file content or literal commands, no "TBD"/"handle edge cases" left in.
- **Type/name consistency:** plugin name `bluetape-skills` and marketplace name `bluetape-skills` are identical across Task 1's JSON, Task 2's validation script, and Task 3's README snippets (`bluetape-skills@bluetape-skills` install command matches the `name`/`source` pairing set in Task 1).
