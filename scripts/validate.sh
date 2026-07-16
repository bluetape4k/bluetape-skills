#!/usr/bin/env bash
set -euo pipefail

readonly expected_skills=(
  bluetape-bugfix bluetape-diagram bluetape-fast-track bluetape-full-feature
  bluetape-go-patterns bluetape-kotlin-patterns bluetape-maintenance
  bluetape-publish-go bluetape-publish-jvm bluetape-py-patterns
  bluetape-rs-patterns bluetape-self-improve bluetape-workflow bluetape-writer
)

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
skills_root="$repo_root/skills"
workflow_root="$skills_root/bluetape-workflow"
diagram_root="$skills_root/bluetape-diagram"

for command in rg python3 uv; do
  command -v "$command" >/dev/null || { echo "missing required command: $command" >&2; exit 1; }
done

python3 - "$skills_root/manifest.json" "${expected_skills[@]}" <<'PY'
import json
import sys
from pathlib import Path

manifest_path = Path(sys.argv[1])
expected = sys.argv[2:]
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
if manifest.get("schemaVersion") != 1:
    raise SystemExit("unexpected manifest schemaVersion")
if manifest.get("distribution") != "canonical-public-bundle":
    raise SystemExit("unexpected manifest distribution")
if manifest.get("skills") != expected:
    raise SystemExit("manifest skill inventory does not match the canonical order")
if manifest.get("externalSkills") != ["code-review", "self-audit"]:
    raise SystemExit("unexpected external skill dependency inventory")
PY

for skill in "${expected_skills[@]}"; do
  skill_file="$skills_root/$skill/SKILL.md"
  [[ -f "$skill_file" ]] || { echo "missing skill: $skill" >&2; exit 1; }
  [[ "$(sed -n '1p' "$skill_file")" == '---' ]] || { echo "missing front matter: $skill" >&2; exit 1; }
  rg -q "^name: $skill$" "$skill_file" || { echo "name mismatch: $skill" >&2; exit 1; }
  rg -q '^description: .+' "$skill_file" || { echo "missing description: $skill" >&2; exit 1; }
done

actual_count="$(find "$skills_root" -mindepth 1 -maxdepth 1 -type d | wc -l | tr -d ' ')"
[[ "$actual_count" == "${#expected_skills[@]}" ]] || { echo "unexpected skill directory count: $actual_count" >&2; exit 1; }

if find "$skills_root" -type d \( -name memories -o -name rules -o -name hooks -o -name .system \) -print -quit | rg -q .; then
  echo "forbidden private/runtime directory found in bundle" >&2
  exit 1
fi

if find "$skills_root" -type f \( -name '.env' -o -name '*.pem' -o -name '*.key' \) -print -quit | rg -q .; then
  echo "forbidden secret-like file found in bundle" >&2
  exit 1
fi

if find "$skills_root" -name '.DS_Store' -print -quit | rg -q .; then
  echo "forbidden macOS metadata file found in bundle" >&2
  exit 1
fi

if find "$skills_root" -type f -name 'executable_*' -print -quit | rg -q .; then
  echo "unrendered chezmoi executable filename found in bundle" >&2
  exit 1
fi

readonly workflow_scripts=(
  audit-token-budget.py bluetape-flow.py validate-contracts.py
)
for script in "${workflow_scripts[@]}"; do
  script_path="$workflow_root/scripts/$script"
  [[ -x "$script_path" ]] || { echo "missing executable workflow script: $script" >&2; exit 1; }
done

set +e
contract_json="$(python3 "$workflow_root/scripts/validate-contracts.py" \
  --skill-root "$workflow_root" \
  --skills-root "$skills_root" \
  --json)"
contract_status=$?
set -e

python3 - "$skills_root/manifest.json" "$contract_status" "$contract_json" <<'PY'
import json
import sys
from pathlib import Path

manifest = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
status = int(sys.argv[2])
result = json.loads(sys.argv[3])
external = set(manifest["externalSkills"])
observed_external = set()
unexpected = []
for issue in result.get("issues", []):
    code = issue.get("code")
    message = issue.get("message", "")
    dependency = message.rsplit(" ", 1)[-1].removeprefix("$")
    if code not in {"unknown_skill_reference", "manifest_route_missing"} or dependency not in external:
        unexpected.append(issue)
    else:
        observed_external.add(dependency)
if unexpected or observed_external != external or status != 1:
    print(json.dumps({
        "contract_status": status,
        "declared_external": sorted(external),
        "issues": unexpected,
        "observed_external": sorted(observed_external),
        "ok": False,
    }, sort_keys=True), file=sys.stderr)
    raise SystemExit(status or 1)
print(json.dumps({"external_skills": sorted(external), "issues": [], "ok": True}, sort_keys=True))
PY

PYTHONDONTWRITEBYTECODE=1 uv run --with pytest pytest -q "$workflow_root/tests"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -v \
  -s "$diagram_root/tests" \
  -p 'test_*.py'

echo "PASS: ${#expected_skills[@]} canonical skills, workflow contracts, diagram audits, tests, and public bundle boundaries are valid."
