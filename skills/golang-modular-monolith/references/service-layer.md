# Service layer

`service/` holds business rules. One file per domain action; action verb free-form snake_case:

- `employee_create.go`, `employee_archive.go`, `user_login.go`, `user_reset_password.go`.

Service = only layer allowed to translate between HTTP DTO and Postgres DTO. Mappers in `service/mapper/{http,postgres}/` do conversion; service calls them.

## Function naming per layer

- `service/` — domain action: `Create`, `Archive`, `Login`, `ResetPassword`
- `service/mapper/postgres/` — `To<Op>Params`: `ToInsertParams`, `ToSelectByIDParams`
- `service/mapper/http/` — `To<Modifier>Response`: `ToGetByIDResponse`, `ToGetAllResponse`
- `infrastructure/postgres/` — `<Op>[<Modifier>]`: `Insert`, `SelectByID`, `UpdateArchived`, `Delete`
- `interface/http/handler/` — domain action: `Create`, `GetByID`, `Login`

Package holds more than one entity → suffix entity to disambiguate: `CreateRole`, `SelectByIDUser`, `UpdateSession`. Single-entity modules omit suffix when no ambiguity.

## Banned in function names

These tokens indicate layering smell:

- Layer suffix in function name: `HTTP`, `Service`, `Handler`, `Repo`. Package path already says layer.
- URL segments: `Security`, `Admin`, `V1`. Route lives in `register.go`, not function name.
- Redundant HTTP verb: `PostCreate`, `GetGetByID`. Pick one.
