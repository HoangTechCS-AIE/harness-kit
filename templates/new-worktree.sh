#!/usr/bin/env bash
# new-worktree.sh — create a git worktree + its own branch for a parallel/long task.
#
# Level 4 (long-running): each heavy task should have its OWN working tree, so parallel runs
# don't step on each other (no constant stash/switch, no overwriting each other's edits).
#
# Usage:  ./new-worktree.sh <task-name>
# E.g.:   ./new-worktree.sh refactor-auth
#   -> creates branch 'refactor-auth' + dir ../<repo>-refactor-auth (NEXT TO the repo, not nested).

set -euo pipefail

name="${1:-}"
[ -n "$name" ] || { echo "usage: $0 <task-name>   (e.g. refactor-auth)"; exit 1; }

# Must be inside a git repo.
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || { echo "not a git repo"; exit 1; }

root="$(git rev-parse --show-toplevel)"
repo="$(basename "$root")"
dir="$root/../${repo}-${name}"          # place it NEXT TO the repo, not nested -> git status stays clean

[ -e "$dir" ] && { echo "already exists: $dir"; exit 1; }   # fail-fast, don't overwrite

# Branch from the latest base. Change 'main' if your repo uses a different name.
base="$(git symbolic-ref --quiet --short HEAD || echo main)"

if git show-ref --verify --quiet "refs/heads/${name}"; then
  git worktree add "$dir" "$name"            # branch exists -> check it out into the new worktree
else
  git worktree add -b "$name" "$dir" "$base" # new branch from the current base
fi

echo "worktree: $dir   (branch: $name)"
echo "  cd \"$dir\" to start. When done: git worktree remove \"$dir\""
