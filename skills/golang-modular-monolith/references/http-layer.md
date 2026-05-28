# HTTP layer

Files in `interface/http/handler/`, `interface/http/dto/`, `service/mapper/http/` use **HTTP methods** as operation suffix — and only HTTP methods.

Route -> file:

- `GET /employees/:id` -> `employee_get.go`
- `POST /employees` -> `employee_post.go`
- `PATCH /employees/:id` -> `employee_patch.go`
- `DELETE /employees/:id` -> `employee_delete.go`
- `GET /employees?filter=...` (list with filters) -> `employee_query.go`

Note: `query` is used as HTTP-method suffix for list/filter endpoints, in addition to standard verbs. Not a generic word for "any query".

## Domain actions: sub-resource vs PATCH on parent

Domain actions ("login", "archive", "publish", "reset password") never become HTTP-method files like `book_archive.go`. Model one of two ways — pick by what the action *produces*, not by the verb the product team uses.

**Sub-resource** when action creates an independently-trackable thing — new row, token, audit event, anything with its own lifecycle. File named after sub-entity:

- `POST /clients/:id/sessions` -> `session_post.go` — session row (own id, expiry, revocation)
- `POST /clients/:id/password-resets` -> `password_reset_post.go` — one-shot reset token
- `DELETE /clients/:id/sessions/:sid` -> `session_delete.go` — revokes specific session

**`PATCH /<entity>/:id` on parent** when action just flips a field on the existing entity — `archived_at`, `published_at`, `locked_at`, `approved_at`. No new thing created; the resource's own state changes. File = entity's PATCH handler:

- Archive (soft-delete) book: `PATCH /books/:id` body `{"archived": true}` -> `book_patch.go`
- Publish article: `PATCH /articles/:id` body `{"published": true}` -> `article_patch.go`
- Lock user: `PATCH /users/:id` body `{"locked": true}` -> `user_patch.go`

Service action keeps domain name in `service/` (`book_archive.go`, `article_publish.go`). SQL still uses closed vocabulary (`book_update_archived.sql`). Only HTTP file name follows REST shape of actual transport.

> WARNING: Common mistake — inventing noun-form sub-resource (`archival`, `publication`, `lock`) for what is a field flip. If the only thing changing on the server is a timestamp column on the parent row, it's `PATCH`, not a new resource.

## Forbidden HTTP file names

- Domain verbs as suffix: `employee_login.go`, `user_archive.go`. Suffix must be HTTP method; *action* belongs in `service/`.
- Bare verb without entity: `post.go`, `get.go`. Always prefix with entity (or sub-entity for action-resources).
- Made-up sub-entities for field flips: `archival_post.go`, `publication_post.go`. Use `PATCH /<entity>/:id` instead — see above.

If an operation genuinely resists REST modeling, stop and ask before inventing a name.

## `register.go`

Single file at `interface/http/<module>/register.go` declares all routes for the whole module. Only file in `interface/http/`'s root without entity prefix. Add new route here when creating a handler.
