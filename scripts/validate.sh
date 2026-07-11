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

echo "PASS: ${#expected_skills[@]} canonical skills have valid front matter and no private/runtime payload."
