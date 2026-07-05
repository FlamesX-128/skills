#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Prevent the caller's activated venv from clashing with the per-directory uv projects in this skill (root for mdformat, scripts/ for ruff).
unset VIRTUAL_ENV

# Format Python (uses ruff config from root pyproject.toml)
(cd scripts && uv run ruff format ..)

# Format Markdown
pnpm dlx prettier --write "**/*.md"
