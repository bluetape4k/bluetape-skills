#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: scripts/install.sh [--codex-home PATH] [--force] [--dry-run]

Install the canonical Bluetape skills into the Codex skills directory. Existing canonical
skill directories are left untouched unless --force is supplied. With --force,
each replaced directory is moved to a timestamped backup before installation.
EOF
}

codex_home="${CODEX_HOME:-$HOME/.codex}"
force=0
dry_run=0

while [[ "$#" -gt 0 ]]; do
  case "$1" in
    --codex-home)
      codex_home="${2:?missing path after --codex-home}"
      shift
      ;;
    --force)
      force=1
      ;;
    --dry-run)
      dry_run=1
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
source_root="$repo_root/skills"
target_root="$codex_home/skills"
backup_root="$codex_home/skills-backup/bluetape-$(date -u +%Y%m%dT%H%M%SZ)"

[[ -d "$source_root" ]] || { echo "skills directory is missing: $source_root" >&2; exit 1; }

for source_dir in "$source_root"/*; do
  [[ -d "$source_dir" && -f "$source_dir/SKILL.md" ]] || continue
  skill="$(basename "$source_dir")"
  target_dir="$target_root/$skill"

  if [[ -e "$target_dir" && "$force" -ne 1 ]]; then
    echo "refusing to replace existing skill: $target_dir (use --force to back it up first)" >&2
    exit 1
  fi
done

if [[ "$dry_run" -eq 1 ]]; then
  echo "Would install canonical Bluetape skills from $source_root to $target_root"
  exit 0
fi

mkdir -p "$target_root"
for source_dir in "$source_root"/*; do
  [[ -d "$source_dir" && -f "$source_dir/SKILL.md" ]] || continue
  skill="$(basename "$source_dir")"
  target_dir="$target_root/$skill"

  if [[ -e "$target_dir" ]]; then
    mkdir -p "$backup_root"
    mv "$target_dir" "$backup_root/$skill"
  fi

  cp -R "$source_dir" "$target_dir"
done

echo "Installed canonical Bluetape skills into $target_root"
if [[ -d "$backup_root" ]]; then
  echo "Backed up replaced skills under $backup_root"
fi
