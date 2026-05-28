#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Format Python (validator)
(cd scripts && uv run ruff format .)

# Format Markdown (skill-scoped)
uv run mdformat --number --wrap keep \
    --exclude '**/.venv/**' \
    --exclude '**/__pycache__/**' \
    --exclude '**/node_modules/**' \
    .
