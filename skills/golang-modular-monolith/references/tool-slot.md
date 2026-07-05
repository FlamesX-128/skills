# The `tool/` slot

`tool/` = directory of helpers local to parent layer. Exists at root of adapter or main layer; sub-directories never own `tool/`.

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

- Files named for what they resolve, no entity prefix: `parse.go`, `scan.go`, `format.go`.
- Helpers private to layer. `interface/http/tool/` not callable from `service/`.
- Helper needed in more than one module → promote to `internal/shared/`, don't duplicate under each module's `tool/`.
- Create directory only when at least one file exists to put inside.
