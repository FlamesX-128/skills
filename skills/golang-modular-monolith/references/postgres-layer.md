# Postgres layer

Files in `infrastructure/postgres/`, `infrastructure/postgres/dto/`, `infrastructure/postgres/sql/`, `service/mapper/postgres/` use SQL operations as suffix.

Pattern: `<table>_<sql_op>[_<modifier>].<ext>` where `<sql_op>` in `{select, insert, update, delete, merge, truncate}`.

Prefix in `sql/` = actual Postgres table name. Usually matches Go entity; differs for plural or join tables (e.g. `user_role`, `users`).

## Final statement decides suffix

CTEs = preparation; suffix follows outer statement returning result.

- `SELECT ...` or `SELECT COUNT(*)` -> `_select`
- `INSERT ... RETURNING *` -> `_insert`
- `UPDATE ... SET archived_at = NOW()` -> `_update`
- `DELETE ... RETURNING *` -> `_delete`
- `WITH d AS (DELETE ...) SELECT ...` -> `_select` (outer is SELECT)
- `WITH ins AS (INSERT ...) UPDATE ...` -> `_update` (outer is UPDATE)

## Modifiers distinguish variants of same operation

- `employee_select.sql` — base case
- `employee_select_all.sql`, `employee_select_by_id.sql`, `employee_select_by_email.sql`, `employee_select_count.sql`
- `employee_update_archived.sql`, `employee_update_unarchived.sql`, `employee_update_password.sql`

## One operation per `.sql` file

One final statement per file. CTEs valid as preparation. Independent mutations chained in one file invalid.

```sql
-- WRONG: two independent mutations in one file
WITH ins AS (INSERT INTO audit ...) UPDATE x ...

-- RIGHT: CTE prepares data for the final statement
WITH affected AS (SELECT id FROM y WHERE z = $1)
UPDATE x SET archived_at = NOW() WHERE id IN (SELECT id FROM affected);
```

Operation genuinely needs multiple writes -> expose as separate functions in `infrastructure/postgres/`. Coordinate in `service/` inside transaction.

## Words that look like SQL but aren't operations

- `archive`, `unarchive`, `lock`, `publish`, `approve` = domain action -> `UPDATE` with modifier: `employee_update_archived.sql`
- `count`, `exists`, `sum`, `avg` = aggregation inside `SELECT` -> `employee_select_count.sql`
- `upsert` = variant of `INSERT` -> goes in `insert.go` / `insert.sql`
