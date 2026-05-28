# Service layer

`service/` holds business rules. One file per domain action; action verb is free-form snake_case:

- `employee_create.go`, `employee_archive.go`, `user_login.go`, `user_reset_password.go`.

Service = only layer permitted to translate between HTTP DTO and Postgres DTO. Mappers in `service/mapper/{http,postgres}/` perform actual conversion; service calls them.

## Function naming per layer

- `service/` — domain action: `Create`, `Archive`, `Login`, `ResetPassword`
- `service/mapper/postgres/` — `To<Op>Params`: `ToInsertParams`, `ToSelectByIDParams`
- `service/mapper/http/` — `To<Modifier>Response`: `ToGetByIDResponse`, `ToGetAllResponse`
- `infrastructure/postgres/` — `<Op>[<Modifier>]`: `Insert`, `SelectByID`, `UpdateArchived`, `Delete`
- `interface/http/handler/` — domain action: `Create`, `GetByID`, `Login`

When a package holds more than one entity, suffix the entity to disambiguate: `CreateRole`, `SelectByIDUser`, `UpdateSession`. In single-entity modules omit suffix when no ambiguity.

## Banned in function names

These tokens almost always indicate a layering smell:

- Layer suffix in function name: `HTTP`, `Service`, `Handler`, `Repo`. Package path already says what layer it is.
- URL segments: `Security`, `Admin`, `V1`. Route is in `register.go`, not the function name.
- Redundant HTTP verb: `PostCreate`, `GetGetByID`. Pick one.
