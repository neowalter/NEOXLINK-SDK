#!/usr/bin/env bash
# Safely stage README / SDK facade changes and push to GitHub.
# Usage:
#   ./scripts/push_readme_to_github.sh              # commit + push
#   DRY_RUN=1 ./scripts/push_readme_to_github.sh   # show diff only
#   COMMIT_MSG="..." ./scripts/push_readme_to_github.sh
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

REMOTE="${REMOTE:-origin}"
BRANCH="${BRANCH:-$(git rev-parse --abbrev-ref HEAD)}"
DRY_RUN="${DRY_RUN:-0}"
COMMIT_MSG="${COMMIT_MSG:-docs: refresh README (EN/ZH); add neoxlink.SDK entrypoint}"

FILES=(
  "README.md"
  "README_zh.md"
  "README.zh-CN.md"
  "neoxlink/__init__.py"
  "pyproject.toml"
  "scripts/push_readme_to_github.sh"
)

missing=0
for f in "${FILES[@]}"; do
  if [[ ! -e "$f" ]]; then
    echo "error: missing expected file: $f" >&2
    missing=1
  fi
done
[[ "$missing" -eq 0 ]] || exit 1

if [[ "$DRY_RUN" == "1" ]]; then
  git diff --stat -- "${FILES[@]}" || true
  echo "DRY_RUN=1: no commit or push performed."
  exit 0
fi

git add -- "${FILES[@]}"

if git diff --cached --quiet; then
  echo "Nothing to commit (staged area empty)."
  exit 0
fi

git commit -m "$COMMIT_MSG"
git push "$REMOTE" "$BRANCH"
