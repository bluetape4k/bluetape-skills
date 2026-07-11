#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: validate-sealed.sh [--repo PATH] [--settings PATH] [--base REV]

Checks that all changes from a trusted candidate base, including committed and
untracked changes, do not overlap settings.json sealed_files.
settings.json defaults to .omx/self-improve/config/settings.json under --repo.
EOF
}

repo="."
settings=""
base=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      repo="$2"
      shift 2
      ;;
    --settings)
      settings="$2"
      shift 2
      ;;
    --base)
      base="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ -z "${settings}" ]]; then
  settings="${repo}/.omx/self-improve/config/settings.json"
fi

if [[ ! -f "${settings}" ]]; then
  echo "ERROR: self-improve settings file not found: ${settings}" >&2
  exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq is required to read sealed_files from ${settings}" >&2
  exit 1
fi

if ! git -C "${repo}" rev-parse --git-dir >/dev/null 2>&1; then
  echo "ERROR: ${repo} is not a git repository." >&2
  exit 1
fi

if ! jq -e '(.sealed_files | type) == "array"' "${settings}" >/dev/null; then
  echo "ERROR: sealed_files must be an array in ${settings}" >&2
  exit 1
fi

sealed_count="$(jq -r '.sealed_files | length' "${settings}")"
if [[ "${sealed_count}" == "0" ]]; then
  echo "ERROR: sealed_files must contain at least one protected path." >&2
  exit 1
fi

if [[ -z "${base}" ]]; then
  base="$(jq -r '.trusted_base_revision // empty' "${settings}")"
fi

if [[ -z "${base}" ]]; then
  echo "ERROR: trusted candidate base is required via --base or trusted_base_revision." >&2
  exit 1
fi

if ! git -C "${repo}" rev-parse --verify "${base}^{commit}" >/dev/null 2>&1; then
  echo "ERROR: trusted candidate base is not a commit: ${base}" >&2
  exit 1
fi

changed_files="$(
  {
    git -C "${repo}" diff --name-only --no-renames "${base}" --
    git -C "${repo}" ls-files --others --exclude-standard
  } | sort -u
)"

violations=()
while IFS= read -r sealed; do
  [[ -z "${sealed}" ]] && continue
  if [[ "${sealed}" == /* || "${sealed}" == ".." || "${sealed}" == ../* || "${sealed}" == */../* ]]; then
    echo "ERROR: sealed path must be repository-relative without '..': ${sealed}" >&2
    exit 1
  fi

  sealed_path="${sealed%/}"
  sealed_is_dir=false
  if [[ "${sealed}" == */ || -d "${repo}/${sealed_path}" ]]; then
    sealed_is_dir=true
  elif [[ "$(git -C "${repo}" cat-file -t "${base}:${sealed_path}" 2>/dev/null || true)" == "tree" ]]; then
    sealed_is_dir=true
  fi

  while IFS= read -r changed; do
    [[ -z "${changed}" ]] && continue
    if [[ "${sealed_is_dir}" == true ]]; then
      [[ "${changed}" == "${sealed_path}" || "${changed}" == "${sealed_path}/"* ]] && violations+=("${changed}")
    else
      [[ "${changed}" == "${sealed_path}" ]] && violations+=("${changed}")
    fi
  done <<< "${changed_files}"

  ignored_or_untracked="$(
    git -C "${repo}" status --porcelain=v1 --untracked-files=all \
      --ignored=matching -- "${sealed_path}" 2>/dev/null || true
  )"
  if [[ -n "${ignored_or_untracked}" ]]; then
    violations+=("${sealed_path}")
  fi
done < <(jq -r '.sealed_files[]?' "${settings}")

if [[ "${#violations[@]}" -gt 0 ]]; then
  printf 'ERROR: sealed file modified: %s\n' "${violations[@]}" >&2
  exit 1
fi

echo "OK: sealed files unchanged."
