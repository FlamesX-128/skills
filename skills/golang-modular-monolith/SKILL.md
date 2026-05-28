---
name: golang-modular-monolith
description: Golang Modular Monolith - strict naming + layout convention for Go modular monoliths. Layer structure (model/service/infrastructure/interface), `<entity>_<operation>` file naming, closed vocab per layer (HTTP methods, SQL ops, domain actions), tool/ slot rules, multi-entity module decisions, bundled validator. Apply skill when user touch anything inside `cmd/` or `internal/` -- add module, route, handler, DTO, SQL query, service method, mapper, model, middleware; decide where file belong; rename/restructure dirs; run validator; review diff landing in repo. Use proactively even when user no mention "conventions" -- invented names + paths silently break validator + confuse downstream LLMs.
license: MIT. See bundled LICENSE for full terms.
compatibility: Requires Python 3.12+ and uv to run the bundled validator.
allowed-tools: Bash(python3 *) Bash(uv *)
---

# Golang Modular Monolith

Naming + layout convention for Go modular monoliths. Rigid rules -> file location computable from intent (`module` + `layer` + `entity` + `operation` → exact path). Follow when edit `cmd/` or `internal/`. Every op file carry entity prefix; every layer have closed vocab. When thing no fit, **ask -- no invent.**

## How to use this skill

1. Find user intent in section index below.

2. Jump to named section for exact rules.

3. Make edit.

4. Run bundled validator from project root (replace `${SKILL_DIR}` with agent's install-path var -- `${CLAUDE_SKILL_DIR}` on Claude Code):

   ```bash
   python3 ${SKILL_DIR}/scripts/validate.py .
   ```

   Non-zero exit = real problem; warnings on empty structural slots advisory.

Section index:

- New domain or bounded context -> [Module layout](#module-layout)
- New HTTP endpoint, route, handler, DTO -> [HTTP layer](#http-layer)
- New SQL query, insert, update, delete -> [Postgres layer](#postgres-layer)
- New business action / domain operation -> [Service layer](#service-layer)
- Where helper file lives -> [The tool/ slot](#the-tool-slot)
- Sub-entity vs own module -> [Multi-entity decisions](#multi-entity-decisions)
- Reusable type or stateless function across modules -> [shared and platform](#shared-and-platform)
- New binary / entry point -> [cmd/ entry points](#cmd-entry-points)
- Running checks after change -> [Running the validator](#running-the-validator)

## Cardinal rules

Violate these = immediately wrong file. Internalize before anything else.

1. **Every op file has entity prefix: `<entity>_<operation>.<ext>`.** Exceptions: `interface/http/register.go`, per-entity files in `model/` (file name *is* entity), helpers inside `tool/` dirs.
2. **Each layer has closed vocab for op.** Mixing vocabs between layers = most common LLM mistake:
   - **SQL files** (`infrastructure/postgres/*`, `service/mapper/postgres/`): `select / insert / update / delete / merge / truncate`.
   - **HTTP files** (`interface/http/*`, `service/mapper/http/`): `get / post / put / patch / delete / head / options / query`.
   - **Service files** (`service/`): domain actions in snake_case (`create`, `archive`, `login`, `reset_password`).
3. **One op per `.sql` file.** CTEs fine as prep; chaining two independent mutations not. Coordinate multi-step writes from service inside transaction.
4. **Infrastructure speak SQL only.** Domain verbs (`archive`, `lock`, `login`, `approve`) live in `service/` + `handler/`, never inside `infrastructure/postgres/`. Infra layer no know what "login" is -- it know `select` + `update`.
5. **Go package name == directory name.** When two packages clash, resolve with import alias at caller. Never rename package or dir to escape collision.
6. **Create files only for ops module actually use.** Empty files "for completeness" = smell; validator flag them.
7. **When in doubt, stop + ask.** One-message clarify cheaper than silently invented convention other LLMs + validator must chase.

## Module layout

*Single-entity* module: entity name == module name (e.g. `employee` module -> `employee` entity). *Multi-entity* module group tightly-coupled entities (e.g. `auth` containing `user`, `role`, `session`). Dir shape identical both cases -- only file prefixes differ.

```
internal/<module>/
|-- model/
|   \-- <entity>.go                       canonical entity (db: + json: tags). One file per entity.
|-- service/
|   |-- <entity>_<action>.go              domain actions: create, archive, login, ...
|   |-- mapper/
|   |   |-- http/<entity>_<method>.go     converts service result -> HTTP response DTO
|   |   \-- postgres/<entity>_<op>.go     converts request -> postgres params struct
|   \-- tool/                             local helpers (snake_case, no entity prefix)
|-- infrastructure/
|   |-- postgres/
|   |   |-- <entity>_<op>.go              Go function that runs the SQL
|   |   |-- dto/<entity>_<op>.go          sqlx struct (db: tags only)
|   |   |-- sql/<entity>_<op>[_<mod>].sql one final statement per file
|   |   \-- tool/
|   \-- redis/{dto,tool}/                 optional, same shape
\-- interface/
    \-- http/
        |-- register.go                   declares routes for the entire module
        |-- dto/<entity>_<method>.go      request + response (json: + validate: tags)
        |-- handler/<entity>_<method>.go  Fiber handler -- parse, validate, call service
        |-- middleware/                   optional
        \-- tool/
```

Dirs with trailing `/` (`sql/`, `tool/`, `middleware/`, `redis/`) = **structural slots**. Allowed empty, populated only when module need them. Validator warn on empty slots, no fail.

Reason for rigidity: any LLM (or human) navigate to *exact file* responsible for given op by composing module + layer + entity + op. Drift in any dim defeat predictability that justify layout.

## HTTP layer

Files in `interface/http/handler/`, `interface/http/dto/`, `service/mapper/http/` use **HTTP methods** as op suffix -- only HTTP methods.

Route -> file:

- `GET /employees/:id` -> `employee_get.go`
- `POST /employees` -> `employee_post.go`
- `PATCH /employees/:id` -> `employee_patch.go`
- `DELETE /employees/:id` -> `employee_delete.go`
- `GET /employees?filter=...` (list with filters) -> `employee_query.go`

Note: in this codebase `query` used as HTTP-method suffix for list/filter endpoints, in addition to standard verbs. *Not* generic word for "any query".

### Domain actions: sub-resource vs PATCH on parent

Domain action ("login", "archive", "publish", "reset password") never become HTTP-method file like `book_archive.go`. Model one of two ways -- pick by what action *produces*, not by verb product team use.

**Sub-resource** when action create independently-trackable thing -- new row, token, audit event, anything with own lifecycle. File named after sub-entity:

- `POST /clients/:id/sessions` -> `session_post.go` -- session row (own id, expiry, revocation)
- `POST /clients/:id/password-resets` -> `password_reset_post.go` -- one-shot reset token
- `DELETE /clients/:id/sessions/:sid` -> `session_delete.go` -- revoke specific session

**`PATCH /<entity>/:id` on parent** when action just flip field on existing entity -- `archived_at`, `published_at`, `locked_at`, `approved_at`. No new thing created; resource own state changes. File = entity's PATCH handler:

- Archive (soft-delete) book: `PATCH /books/:id` body `{"archived": true}` -> `book_patch.go`
- Publish article: `PATCH /articles/:id` body `{"published": true}` -> `article_patch.go`
- Lock user: `PATCH /users/:id` body `{"locked": true}` -> `user_patch.go`

Service action keep domain name in `service/` (`book_archive.go`, `article_publish.go`). SQL still use closed vocab (`book_update_archived.sql`). Only HTTP file name follow REST shape of actual transport.

> WARNING: Common mistake: invent noun-form sub-resource (`archival`, `publication`, `lock`) for what is field flip. If only thing changing on server is timestamp column on parent row, it's `PATCH`, no new resource.

### Forbidden HTTP file names

- Domain verbs as suffix: `employee_login.go`, `user_archive.go`. Suffix must be HTTP method; *action* belong in `service/`.
- Bare verb without entity: `post.go`, `get.go`. Always prefix with entity (or sub-entity for action-resources).
- Made-up sub-entities for field flips: `archival_post.go`, `publication_post.go`. Use `PATCH /<entity>/:id` instead -- see above.

If op genuinely resist REST modeling, stop + ask before invent name.

### `register.go`

Single file at `interface/http/<module>/register.go` declare all routes for whole module. Only file in `interface/http/`'s root without entity prefix. Add new route here when create handler.

## Postgres layer

Files in `infrastructure/postgres/`, `infrastructure/postgres/dto/`, `infrastructure/postgres/sql/`, `service/mapper/postgres/` use **SQL ops** as suffix.

Pattern: `<table>_<sql_op>[_<modifier>].<ext>` where `<sql_op>` in `{select, insert, update, delete, merge, truncate}`.

Prefix in `sql/` = **actual Postgres table name**. Usually match Go entity but may differ for plural tables or join tables (e.g. `user_role`, `users`).

### Final statement decides suffix

CTEs = prep; suffix follow outer statement that return result.

- `SELECT ...` or `SELECT COUNT(*)` -> `_select`
- `INSERT ... RETURNING *` -> `_insert`
- `UPDATE ... SET archived_at = NOW()` -> `_update`
- `DELETE ... RETURNING *` -> `_delete`
- `WITH d AS (DELETE ...) SELECT ...` -> `_select` (outer is SELECT)
- `WITH ins AS (INSERT ...) UPDATE ...` -> `_update` (outer is UPDATE)

### Modifiers distinguish variants of same op

- `employee_select.sql` -- base case
- `employee_select_all.sql`, `employee_select_by_id.sql`, `employee_select_by_email.sql`, `employee_select_count.sql`
- `employee_update_archived.sql`, `employee_update_unarchived.sql`, `employee_update_password.sql`

### One op per `.sql` file

Single final statement per file. CTEs valid prep. Independent mutations chained in one file not.

```sql
-- WRONG: two independent mutations in one file
WITH ins AS (INSERT INTO audit ...) UPDATE x ...

-- RIGHT: CTE prepares data for the final statement
WITH affected AS (SELECT id FROM y WHERE z = $1)
UPDATE x SET archived_at = NOW() WHERE id IN (SELECT id FROM affected);
```

When op genuinely need multiple writes, expose as separate functions in `infrastructure/postgres/`. Coordinate in `service/` inside transaction.

### Words that look like SQL but aren't ops

- `archive`, `unarchive`, `lock`, `publish`, `approve` = domain action -> `UPDATE` with modifier: `employee_update_archived.sql`
- `count`, `exists`, `sum`, `avg` = aggregation inside `SELECT` -> `employee_select_count.sql`
- `upsert` = variant of `INSERT` -> goes in `insert.go` / `insert.sql`

## Service layer

`service/` hold business rules. One file per domain action; action verb free-form snake_case:

- `employee_create.go`, `employee_archive.go`, `user_login.go`, `user_reset_password.go`.

Service = only layer permit to translate between HTTP DTO + Postgres DTO. Mappers in `service/mapper/{http,postgres}/` do actual conversion; service call them.

### Function naming per layer

- `service/` -- domain action: `Create`, `Archive`, `Login`, `ResetPassword`
- `service/mapper/postgres/` -- `To<Op>Params`: `ToInsertParams`, `ToSelectByIDParams`
- `service/mapper/http/` -- `To<Modifier>Response`: `ToGetByIDResponse`, `ToGetAllResponse`
- `infrastructure/postgres/` -- `<Op>[<Modifier>]`: `Insert`, `SelectByID`, `UpdateArchived`, `Delete`
- `interface/http/handler/` -- domain action: `Create`, `GetByID`, `Login`

When package hold more than one entity, suffix entity to disambiguate: `CreateRole`, `SelectByIDUser`, `UpdateSession`. In single-entity modules omit suffix when no ambiguity.

### Banned in function names

These tokens almost always indicate layering smell:

- Layer suffix in fn name: `HTTP`, `Service`, `Handler`, `Repo`. Package path already say what layer it is.
- URL segments: `Security`, `Admin`, `V1`. Route in `register.go`, not fn name.
- Redundant HTTP verb: `PostCreate`, `GetGetByID`. Pick one.

## The `tool/` slot

`tool/` = dir of helpers local to parent layer. Exist at root of adapter or main layer; sub-dirs never have own `tool/`.

Has own `tool/`:

- `service/`
- `infrastructure/postgres/`
- `infrastructure/redis/`
- `interface/http/`

Does NOT have `tool/`:

- `service/mapper/`, `service/mapper/http/`, `service/mapper/postgres/`
- `infrastructure/postgres/dto/`
- `infrastructure/redis/dto/`
- `interface/http/dto/`
- `interface/http/handler/`
- `interface/http/middleware/`

Inside `tool/`:

- Files named for *what they resolve*, no entity prefix: `parse.go`, `scan.go`, `format.go`.
- Helpers private to layer. `interface/http/tool/` not callable from `service/`.
- If helper need in more than one module, promote to `internal/shared/` instead of duplicate under each module's `tool/`.
- Create dir only once at least one file to put inside.

## Multi-entity decisions

Module single-entity by default: one entity sharing module's name. Become multi-entity when entities so tightly coupled they wouldn't make sense apart -- canonical example `auth` group `user`, `role`, `session`.

Decision rule for "sub-entity vs separate module":

> *Can entity be referenced without mention parent in URL?*

- **Yes** -> separate module. Example: `GET /categories/:id` -- category independent of products, so `category` is own module.
- **No** -> sub-entity of parent. Example: `GET /areas/:id/security/roles/:rid` -- role no exist without `area_id`, so `role` live inside `area` module.

Single-entity + multi-entity modules follow exactly same prefix rules; only difference = how many distinct prefixes appear in module's files.

## shared and platform

`internal/shared/` -- Pure types + stateless functions reused across modules (`Auditable`, error helpers, value objects). No I/O, no state. Free-form internal layout.

`internal/platform/` -- Stateful services with own logic + lifecycle (oauth client, audit pipeline, message bus). Free-form internal layout. Modules consume as ordinary deps.

Neither follow strict module layout; validator skip them. Use for code that genuinely no belong to single domain.

## cmd/ entry points

Each binary live at `cmd/<name>/main.go`. Heavy init (config loading, dependency wiring, dependency injection) belong in `cmd/<name>/bootstrap/bootstrap.go`. Other files under `cmd/<name>/` free-form for binary's needs -- e.g. `cmd/setup/sql/init.sql` for one-shot DB setup binary.

Keep `main.go` small: parse env, call `bootstrap.Run(...)`, exit. Business logic stay in `internal/`.

## Running the validator

Validator bundled inside skill at `${SKILL_DIR}/scripts/`. Use install-path var supplied by agent runtime (`${CLAUDE_SKILL_DIR}` on Claude Code; equivalent on other runtimes) so path resolve whether skill installed at project, personal, or plugin scope.

Run from project root after any structural change. Pass project root as argument -- validator no assume current working dir:

```bash
python3 ${SKILL_DIR}/scripts/validate.py .
```

Exit code 0 = no errors; warnings about empty structural slots advisory, no fail run. Non-zero exit = real convention break -- read message, fix file, rerun.

### Developing or extending the validator

Bundled scripts dir = self-contained `uv` project. Install dev tooling + run validator's own tests, lint, type-check:

```bash
cd ${SKILL_DIR}/scripts
uv sync                       # install pytest, ruff, mypy into .venv
uv run pytest -q              # validator's own tests (must stay green)
uv run ruff check .           # lint
uv run mypy validate.py       # strict type check
```

If extend validator (new rule, new layer), add test in `tests/test_validate.py` cover both accept + reject cases **before** change `validate.py`. Existing tests = contract -- keep green.

## When you genuinely don't know

Conventions deliberately rigid so anything *invented* stick out. If request no fit cleanly -- domain action that resist REST modeling, query that cross module boundaries, helper that no feel local to any one layer -- stop + ask. One-message clarify much cheaper than silently invented pattern that validator + other LLMs must chase down later.
