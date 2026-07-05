# HTTP layer

Files in `interface/http/handler/`, `interface/http/dto/`, `service/mapper/http/` use HTTP methods as operation suffix — only HTTP methods.

Route -> file:

- `GET /employees/:id` -> `employee_get.go`
- `POST /employees` -> `employee_post.go`
- `PATCH /employees/:id` -> `employee_patch.go`
- `DELETE /employees/:id` -> `employee_delete.go`
- `GET /employees?filter=...` (list with filters) -> `employee_query.go`

Note: `query` = HTTP-method suffix for list/filter endpoints, not generic word for "any query".

## Domain actions: sub-resource vs PATCH on parent

Domain actions ("login", "archive", "publish", "reset password") never become HTTP-method files like `book_archive.go`. Model one of two ways — pick by what action produces, not verb product team uses.

Sub-resource when action creates independently-trackable thing — new row, token, audit event, anything with own lifecycle. File named after sub-entity:

- `POST /clients/:id/sessions` -> `session_post.go` — session row (own id, expiry, revocation)
- `POST /clients/:id/password-resets` -> `password_reset_post.go` — one-shot reset token
- `DELETE /clients/:id/sessions/:sid` -> `session_delete.go` — revokes specific session

`PATCH /<entity>/:id` on parent when action just flips field on existing entity — `archived_at`, `published_at`, `locked_at`, `approved_at`. No new thing created; resource state changes. File = entity's PATCH handler:

- Archive (soft-delete) book: `PATCH /books/:id` body `{"archived": true}` -> `book_patch.go`
- Publish article: `PATCH /articles/:id` body `{"published": true}` -> `article_patch.go`
- Lock user: `PATCH /users/:id` body `{"locked": true}` -> `user_patch.go`

Service action keeps domain name in `service/` (`book_archive.go`, `article_publish.go`). SQL still uses closed vocabulary (`book_update_archived.sql`). Only HTTP file name follows REST shape of actual transport.

> WARNING: Common mistake — inventing noun-form sub-resource (`archival`, `publication`, `lock`) for field flip. If only change is timestamp column on parent row, it's `PATCH`, not new resource.

## Forbidden HTTP file names

- Domain verbs as suffix: `employee_login.go`, `user_archive.go`. Suffix must be HTTP method; action belongs in `service/`.
- Bare verb without entity: `post.go`, `get.go`. Always prefix with entity (or sub-entity for action-resources).
- Made-up sub-entities for field flips: `archival_post.go`, `publication_post.go`. Use `PATCH /<entity>/:id` instead — see above.

Operation genuinely resists REST modeling -> stop and ask before inventing name.

## `register.go`

Single file at `interface/http/<module>/register.go` declares all routes for module. Only file in `interface/http/` root without entity prefix. Add new route here when creating handler.
