#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Prevent the caller's activated venv from clashing with the per-directory
# uv project (root for mdformat).
unset VIRTUAL_ENV

# Format Markdown (skill-scoped)
uv run mdformat --number --wrap keep \
    --exclude '**/.venv/**' \
    --exclude '**/__pycache__/**' \
    --exclude '**/node_modules/**' \
    .
