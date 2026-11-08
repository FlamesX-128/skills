# FlamesX-128 Skills

Agent skills I build and maintain — my own conventions and tooling, packaged as reusable [Agent Skills](https://agentskills.io/home). Compatible w/ the [`skills`](https://github.com/vercel-labs/skills) CLI (Claude, Codex, other agent runtimes). Each skill lives at `skills/<name>/`.

## Skills

| Skill                                                          | Description                                                                                                           |
| -------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **[blind-subagents](skills/blind-subagents/)**                 | Independent reviews with fresh context, using only the supplied task, artifacts, and authorized tools.                |
| **[code-paragraphs](skills/code-paragraphs/)**                 | JavaScript/TypeScript style rules with sequential specialists for syntax, imports, members, paragraphs, and comments. |
| **[golang-modular-monolith](skills/golang-modular-monolith/)** | Strict file-layout convention for Go modular monoliths.                                                               |

## Layout

Each skill contains a `SKILL.md` and can include documentation, a license, runtime scripts, references, or templates. Repository maintenance tooling lives at the root. Skills install independently w/ the `skills` CLI:

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

For TS/JS style work, `code-paragraphs` runs specialists sequentially on each file; separate file batches can run in parallel. See its [workflow](skills/code-paragraphs/README.md#workflow) and [optional shared ESLint/Prettier tooling](skills/code-paragraphs/README.md#optional-shared-tooling).

## Development

Requirements: Bash, git, Node.js with pnpm, Python >= 3.10 with uv, and Go (for `gofmt`).

Install the shared formatters from the repository root:

```bash
pnpm install --frozen-lockfile
uv sync --locked
```

Format repository Markdown, Python, Go, and SQL with one command:

```bash
./format.bash
./format.bash --check   # report formatting differences without changing files
```

The same commands are available as `pnpm format` and `pnpm format:check`. The script resolves the repository root, so it can also be called by path from another directory.

Shared configuration: `.prettierrc` for Markdown, `pyproject.toml` for Ruff/Python, `.sql-formatter.json` for PostgreSQL, and `.gitignore` for generated files and local agent installations. Go uses `gofmt`. Empty Go placeholders in examples are skipped. New skills are included automatically.

Python CLIs keep self-contained projects under their `scripts/` directories for tests, linting, and type checks. For example, from the repository root:

```bash
uv run --locked --directory skills/golang-modular-monolith/scripts pytest
uv run --locked --directory skills/golang-modular-monolith/scripts mypy validate.py
```

## Validating skills

Every skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate w/ [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref), the reference validator from the spec authors.

Ephemeral run (no install, recommended):

```bash
uvx --from 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref' \
    skills-ref validate skills/code-paragraphs
```

Or install once, reuse:

```bash
uv tool install 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref'
skills-ref validate skills/code-paragraphs
```

## License

See each skill directory for its license terms.
