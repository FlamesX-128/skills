# The `tool/` slot

`tool/` = directory of helpers local to the parent layer. Exists at root of adapter or main layer; sub-directories never have their own `tool/`.

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
- Helpers are private to the layer. `interface/http/tool/` is not callable from `service/`.
- If a helper is needed in more than one module, promote to `internal/shared/` instead of duplicating under each module's `tool/`.
- Create the directory only once there is at least one file to put inside.
