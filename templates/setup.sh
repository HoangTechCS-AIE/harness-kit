#!/usr/bin/env bash
# setup.sh — environment bootstrap: "one command makes the repo runnable".
#
# Level 4 (long-running): a background/looping agent CANNOT stop to ask "what do I install now".
# This script must bring a clean checkout to a runnable state, non-interactively.
#
# 2 mandatory principles:
#   - IDEMPOTENT: safe to run many times (no duplication, no broken state).
#   - FAIL-FAST:  if something is missing, report it NOW and stop; don't continue blind.
#
# THIS IS A SKELETON — every repo installs different things. Fill in the TODOs for your repo,
# then point CLAUDE.md here ("Build / Test / Run: run ./setup.sh first").

set -euo pipefail   # error -> stop; unset var -> stop; mid-pipe error -> stop

cd "$(dirname "$0")"

# --- 1. Check prerequisites (fail-fast) ------------------------------------
# Missing base tools are reported immediately; don't let a vague error surface later.
require() {
  command -v "$1" >/dev/null 2>&1 || { echo "missing '$1' — install it then re-run"; exit 1; }
}
# TODO: list the tools your repo needs
require git
# require node
# require python3

# --- 2. Install dependencies (idempotent) ----------------------------------
# Most package managers are already idempotent — re-running is a no-op.
# TODO: replace with your repo's commands
# npm ci
# uv sync
# go mod download

# --- 3. Config / secrets (fail-fast, do NOT invent values) -----------------
# If .env.example exists but .env doesn't -> tell the runner to fill it in; don't guess values.
# if [ -f .env.example ] && [ ! -f .env ]; then
#   echo "no .env yet — copy .env.example and fill in the secrets"; exit 1
# fi

# --- 4. Supporting services (idempotent) -----------------------------------
# TODO: DB/queue... — use create-only-if-missing commands
# docker compose up -d

# --- 5. Verify: prove the environment actually runs ------------------------
# Don't end with a blind "done" — run one cheap check to be sure.
# TODO: your repo's fastest smoke test
# npm run build --silent
# python -c "import yourpkg"

echo "environment ready"
