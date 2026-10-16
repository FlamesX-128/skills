#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

MODE="--write"
RUFF_ARGS=()
if (( $# > 1 )); then
    echo "Usage: $0 [--check]" >&2
    exit 2
fi
case "${1:-}" in
    "") ;;
    --check)
        MODE="--check"
        RUFF_ARGS=(--check)
        ;;
    -h|--help)
        echo "Usage: $0 [--check]"
        echo "Format Markdown, Python, Go, and SQL throughout the repository."
        exit 0
        ;;
    *)
        echo "Usage: $0 [--check]" >&2
        exit 2
        ;;
esac

# Use the repository's uv environment even if the caller has activated another one.
unset VIRTUAL_ENV

pnpm exec prettier --config .prettierrc --ignore-path .gitignore "$MODE" '**/*.md'
uv run --locked ruff format --config pyproject.toml "${RUFF_ARGS[@]}" .

# Include new files while respecting all .gitignore rules and local agent installs.
while IFS= read -r -d '' path; do
    [[ -f "$path" && ! -L "$path" ]] || continue
    case "$path" in
        *.go)
            # Empty files are intentional placeholders in the layout examples.
            [[ -s "$path" ]] || continue
            if [[ "$MODE" == "--check" ]]; then
                unformatted="$(gofmt -l "$path")"
                if [[ -n "$unformatted" ]]; then
                    echo "Go file needs formatting: $path" >&2
                    exit 1
                fi
            else
                gofmt -w "$path"
            fi
            ;;
        *.sql)
            if [[ "$MODE" == "--check" ]]; then
                pnpm exec sql-formatter --config .sql-formatter.json "$path" | diff -u "$path" -
            else
                pnpm exec sql-formatter --config .sql-formatter.json --fix "$path"
            fi
            ;;
    esac
done < <(git ls-files --cached --others --exclude-standard --deduplicate -z -- '*.go' '*.sql')
