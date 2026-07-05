---
name: golang-modular-monolith
description: Apply when structuring or adding files inside `cmd/` or `internal/`.
license: MIT. See bundled LICENSE for full terms.
compatibility: Designed for AI coding agents working on Go projects. Requires Python 3.12+ and uv to run the bundled validator.
allowed-tools: Read Edit Write Glob Grep Bash(go:*) Bash(python3:*) Bash(uv:*) Bash(git:*) Agent AskUserQuestion
metadata:
    author: FlamesX-128
    version: 1.0.0
---

# Golang Modular Monolith

Naming + layout convention for Go modular monoliths. File path from intent: `module` + `layer` + `entity` + `operation` -> exact path. Doesn't fit? **Ask — don't invent.**

References:

- HTTP endpoints, routes, handlers, DTOs -> [HTTP layer](./references/http-layer.md)
- SQL queries, inserts, updates, deletes -> [Postgres layer](./references/postgres-layer.md)
- Business actions, domain operations -> [Service layer](./references/service-layer.md)
- Helper file placement -> [The tool/ slot](./references/tool-slot.md)
- Sub-entity vs own module -> [Multi-entity decisions](./references/multi-entity.md)
- Extending the validator -> [Validator development](./references/validator-development.md)
- Vertical layout within files (struct field order, import groups, blank-line rules, `slog` placement) -> [code-paragraphs](https://github.com/FlamesX-128/skills/tree/main/skills/code-paragraphs) skill

## Cardinal rules

1. **Every operation file has entity prefix: `<entity>_<operation>.<ext>`.** Except: `interface/http/register.go`, per-entity files in `model/`, helpers inside `tool/`.
2. **Each layer has closed vocabulary.**
    - **SQL** (`infrastructure/postgres/*`, `service/mapper/postgres/`): `select / insert / update / delete / merge / truncate`.
    - **HTTP** (`interface/http/*`, `service/mapper/http/`): `get / post / put / patch / delete / head / options / query`.
    - **Service** (`service/`): free-form snake_case domain actions (`create`, `archive`, `login`).
3. **One operation per `.sql` file.** CTEs fine; chaining independent mutations not.
4. **Infrastructure speaks SQL only.** Domain verbs live in `service/` and `handler/`, never `infrastructure/`.
5. **Go package name == directory name.** Clash → import alias, never rename.
6. **Only create files for operations the module uses.** Empty files = smell.
7. **When in doubt, stop and ask.**

## Module layout

Single-entity: entity name == module name. Multi-entity: tightly-coupled entities grouped (e.g. `auth` → `user`, `role`, `session`). Same directory shape, different file prefixes.

```
internal/<module>/
├── model/
│   └── <entity>.go                       canonical entity (db: + json: tags)
├── service/
│   ├── <entity>_<action>.go              domain actions
│   ├── mapper/
│   │   ├── http/<entity>_<method>.go     service result -> HTTP response DTO
│   │   └── postgres/<entity>_<op>.go     request -> postgres params struct
│   └── tool/                             local helpers (no entity prefix)
├── infrastructure/
│   ├── postgres/
│   │   ├── <entity>_<op>.go              Go function running SQL
│   │   ├── dto/<entity>_<op>.go          sqlx struct (db: tags only)
│   │   ├── sql/<entity>_<op>[_<mod>].sql one final statement per file
│   │   └── tool/
│   └── redis/{dto,tool}/                 optional, same shape
└── interface/
    └── http/
        ├── register.go                   all routes for the module
        ├── dto/<entity>_<method>.go      request + response DTOs
        ├── handler/<entity>_<method>.go  Fiber handler
        ├── middleware/                   optional
        └── tool/
```

Trailing `/` dirs = **structural slots** — allowed empty, validator warns but doesn't fail.

## shared and platform

`internal/shared/` — Pure types + stateless functions reused across modules. No I/O, no state. Free-form layout.

`internal/platform/` — Stateful services with own lifecycle (oauth client, audit pipeline, message bus). Free-form layout.

Neither follows strict module layout; validator skips them.

## cmd/ entry points

Binary at `cmd/<name>/main.go`. Heavy init in `cmd/<name>/bootstrap/bootstrap.go`. Keep `main.go` small: parse env, call `bootstrap.Run(...)`, exit.

## Validator

Run after any structural change:

```bash
python3 ${SKILL_DIR}/scripts/validate.py .
```

Exit 0 = clean. Non-zero = convention break. See [validator development](./references/validator-development.md) for extending rules.
