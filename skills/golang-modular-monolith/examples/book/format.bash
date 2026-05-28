#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

# Format Go (skip empty stub files; gofmt rejects them as invalid Go)
find cmd internal -name '*.go' -type f ! -empty -print0 \
    | xargs -0 -r gofmt -w

# Format SQL
rg --files --null cmd internal -g "*.sql" \
    | xargs -0 -r -I{} node_modules/.bin/sql-formatter --fix "{}"
