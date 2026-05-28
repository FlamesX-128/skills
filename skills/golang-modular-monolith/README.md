# Golang Modular Monolith

Naming + layout convention for Go modular monoliths. **File location computable from intent**: `module` + `layer` + `entity` + `operation` → exact path, no invention.

Codebase predictable for humans **and** LLMs. Closed vocab per layer, enforced `<entity>_<operation>` shape, bundled validator. Both navigate by composition, not exploration.

## What's bundled with this skill

- **[`SKILL.md`](SKILL.md)** - Canonical spec. Agent loads on trigger.
- **[`scripts/validate.py`](scripts/validate.py)** - Python validator. Self-contained `uv` project: 74 tests (pytest), `ruff`, `mypy` strict.
- **[`examples/book/`](examples/book/)** - Worked `book` module: CRUD endpoints, soft-delete via `PATCH`, mappers, DTOs, SQL. Every `.go` = stub (`package <name>` only). Demos *file placement*, not Go logic.
- **[`format.bash`](format.bash)** - Formats skill Python (`ruff`) + Markdown (`mdformat`).
- **[`LICENSE`](LICENSE)** - MIT, © 2026 FlamesX-128.

## Quick start

### Install the skill

Published as [Agent Skill](https://agentskills.io/home). Install via [`skills`](https://github.com/vercel-labs/skills) CLI:

```bash
pnpm dlx skills add FlamesX-128/skills --skill=golang-modular-monolith
```

Add `-g` for global install. Agent loads `SKILL.md` for spec, runs `scripts/validate.py` after every change (Claude Code: `${CLAUDE_SKILL_DIR}/scripts/validate.py`; other runtimes: equivalent install-path var).

### Validate a project against the convention

From this skill dir:

```bash
python3 scripts/validate.py /path/to/your/project
```

Exit `0` = no errors. Warnings on empty structural slots are advisory.

### Explore the example

```bash
python3 scripts/validate.py examples/book
```

Read [`SKILL.md`](SKILL.md) alongside file tree under `examples/book/`. Each file demos a specific rule.

### Format

Two `format.bash` scripts, one per subproject:

- **[`format.bash`](format.bash)** - `ruff format` for validator Python + `mdformat` for skill Markdown.
- **[`examples/book/format.bash`](examples/book/format.bash)** - `gofmt` for Go + `sql-formatter` for `.sql`. Empty stubs skipped.

## The convention in one screen

- **Layers**: `model/`, `service/`, `infrastructure/`, `interface/`. Strict separation; deps flow inward.
- **Closed vocabularies per layer**:
  - SQL: `select / insert / update / delete / merge / truncate`
  - HTTP: `get / post / put / patch / delete / head / options / query`
  - Service: free-form domain verbs (`create`, `archive`, `login`, …)
- **File naming**: `<entity>_<operation>.<ext>` everywhere. Exceptions: `model/<entity>.go`, `interface/http/register.go`, helpers in `tool/`.
- **`tool/` slot**: layer-local helpers. Allowed at root of each major layer; forbidden in leaf subdirs.
- **Domain actions**: REST sub-resource only if produces new tracked entity (`sessions`, `password-resets`). Field flips (archive, publish, lock) → `PATCH /<entity>/:id`.

See [`SKILL.md`](SKILL.md) for full spec, multi-entity decision rule, counter-examples.

## Why a convention, not a framework

Most "clean architecture" docs = advice, decay on interpretation. This is thin opinionated convention + validator. Every rule has check, every check has test, validator decides compliance. Safe to delegate to LLMs: cannot quietly invent path that fits training but breaks layout — validator catches on next run.
