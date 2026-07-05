# Go reference

Core rules apply. Go recipe layer. Examples use generic `book` domain — use own domain.

## Contents

- Struct field grouping
- HTTP DTOs: request, query, PATCH
- Imports
- Multi-line calls, sqlx scan, param & JSON literals
- HTTP error handling: specific first, then generic
- Returns, observability (slog)
- Quick summary

## Struct field grouping

Field order; blank between groups:

| Group               | Examples                                |
| ------------------- | --------------------------------------- |
| Identity            | `ID`                                    |
| Foreign keys        | `AuthorID`, `CategoryID`, `OwnerID`     |
| Content             | `Title`, `Summary`, `Price`             |
| State / flags       | `Active`, `Verified`, `Locked`          |
| Domain timestamps   | `PublishedAt`, `ExpiresAt`, `RevokedAt` |
| Registry timestamps | `CreatedAt`, `UpdatedAt`                |
| Soft delete         | `ArchivedAt`                            |
| Embeds              | `Archivable`, `Auditable`               |

```go
type Book struct {
	ID int `db:"id" json:"id"`

	AuthorID   int `db:"author_id" json:"authorId"`
	CategoryID int `db:"category_id" json:"categoryId"`

	Title   string  `db:"title" json:"title"`
	Summary string  `db:"summary" json:"summary"`
	Price   float64 `db:"price" json:"price"`

	PublishedAt time.Time  `db:"published_at" json:"publishedAt"`
	RetiredAt   *time.Time `db:"retired_at" json:"retiredAt,omitempty"`

	Active bool `db:"active" json:"active"`

	sharedmodel.Archivable
	sharedmodel.Auditable
}
```

`RevokedAt` stays in domain-timestamps block, separate from `CreatedAt`:

```go
type Session struct {
	ID int `db:"id"`

	UserID int    `db:"user_id"`
	Hash   string `db:"hash"`

	ExpiresAt   time.Time  `db:"expires_at"`
	RefreshedAt time.Time  `db:"refreshed_at"`
	RevokedAt   *time.Time `db:"revoked_at"`

	CreatedAt time.Time `db:"created_at"`
}
```

## HTTP DTOs

### Request body

Hierarchy (IDs, FKs), content, flags. Same grouping as model:

```go
type CreateBookRequest struct {
	AuthorID   int `json:"authorId" validate:"required,min=1"`
	CategoryID int `json:"categoryId" validate:"required,min=1"`

	Title   string  `json:"title" validate:"required"`
	Summary string  `json:"summary"`
	Price   float64 `json:"price" validate:"required,gt=0"`

	PublishedAt time.Time `json:"publishedAt" validate:"required"`
}
```

### Query with pagination

Embed pagination at end, separate from filter block:

```go
type ListBooksRequest struct {
	AuthorID   int `query:"author_id" default:"0"`
	CategoryID int `query:"category_id" default:"0"`

	Active string `query:"active" default:"" validate:"omitempty,oneof=true false"`
	Search string `query:"search" default:""`

	sharedmodel.PageRequest
}
```

### PATCH with mutually exclusive operations

Group fields by operation:

```go
type UpdateBookRequest struct {
	Title   *string  `json:"title"`
	Summary *string  `json:"summary"`
	Price   *float64 `json:"price" validate:"omitempty,gt=0"`

	Published     *bool      `json:"published"`
	PublishedDate *time.Time `json:"publishedDate"`

	Retired       *bool   `json:"retired"`
	RetiredReason *string `json:"retiredReason"`
}
```

## Imports

goimports groups: stdlib, third-party, internal.

```go
import (
	"context"
	"database/sql"
	"errors"
	"log/slog"

	"github.com/gofiber/fiber/v3"
	"github.com/jmoiron/sqlx"

	"example.com/myapp/internal/book"
)
```

`goimports` handles order. No manual reorder.

## Multi-line function calls

Calls with `ctx`, payload, options: one arg per line:

```go
rows, err := db.NamedQueryContext(
	ctx,
	selectByIDSQL,
	params,
)
```

```go
_, err := db.NamedExecContext(
	ctx,
	updatePriceSQL,
	params,
)

return err
```

## Scan boilerplate (sqlx)

```go
func SelectByID(ctx context.Context, db *sqlx.DB, params *SelectByIDParams) (*Book, error) {
	rows, err := db.NamedQueryContext(
		ctx,
		selectByIDSQL,
		params,
	)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	if rows.Next() {
		var result Book

		if err := rows.StructScan(&result); err != nil {
			return nil, err
		}

		return &result, nil
	}

	if err := rows.Err(); err != nil {
		return nil, err
	}

	return nil, sql.ErrNoRows
}
```

Key:

- Blank before `var result` inside `if rows.Next()`.
- Blank before success `return &result, nil`.
- No blank before `return nil, err` in intermediate error returns.

## Param literals in function calls

Group literal fields by role, same as struct definition:

```go
result, err := db.UpdateBook(
	ctx,
	&UpdateBookParams{
		ID: id,

		Title: title,
		Price: price,
	},
)
```

## Grouped JSON responses

Same field grouping as struct definition:

```go
return c.Status(fiber.StatusOK).JSON(GetBookResponse{
	ID: updated.ID,

	AuthorID:   updated.AuthorID,
	CategoryID: updated.CategoryID,

	Title:   updated.Title,
	Summary: updated.Summary,
	Price:   updated.Price,

	PublishedAt: updated.PublishedAt,
	RetiredAt:   updated.RetiredAt,

	ArchivedAt: updated.ArchivedAt,
	CreatedAt:  updated.CreatedAt,
	UpdatedAt:  updated.UpdatedAt,
})
```

## HTTP error handling: specific first, then generic

- Specific responses (`404`, `409`, `401`): no mandatory `slog`.
- Between specific branch and generic `500`: blank, `slog`, blank, `return`.

```go
if err != nil {
	if errors.Is(err, sql.ErrNoRows) {
		return c.Status(fiber.StatusNotFound).JSON(fiber.Map{
			"error": "Book not found",
		})
	}

	slog.ErrorContext(c.Context(), "could not get book", "book_id", id, "error", err)

	return c.Status(fiber.StatusInternalServerError).JSON(fiber.Map{
		"error": "Could not get book",
	})
}
```

`fiber.NewError` same:

```go
if err != nil {
	if errors.Is(err, sql.ErrNoRows) {
		return fiber.NewError(fiber.StatusNotFound, "book not found")
	}

	slog.ErrorContext(c.Context(), "could not get book", "book_id", id, "error", err)

	return fiber.NewError(fiber.StatusInternalServerError, err.Error())
}
```

## Returns in functions

| Situation                                           | Blank before `return`?        |
| --------------------------------------------------- | ----------------------------- |
| Early-return error (`if err != nil { return ... }`) | No                            |
| Terminal success return at end                      | Yes                           |
| Return after `slog`, before `500`                   | Yes (between slog and return) |
| Return inside successful `if rows.Next()`           | Yes (before `return &result`) |

```go
func ValidatePrice(isPromotional bool, price float64) error {
	if isPromotional {
		if price > PromoMaxPrice {
			return ErrPriceExceedsMax
		}

		if price < PromoMinPrice {
			return ErrPriceBelowMin
		}

		return nil
	}

	if price > StandardMaxPrice {
		return ErrPriceExceedsMax
	}

	if price < StandardMinPrice {
		return ErrPriceBelowMin
	}

	return nil
}
```

## Observability (slog)

### Rule

Every `500` path logs with `slog.ErrorContext` and request context:

```go
slog.ErrorContext(c.Context(), "could not list books", "error", err)
```

Include useful attributes: `user_id`, `book_id`, `author_id`, etc.

### No `slog.Error` without context in HTTP code

Use `ErrorContext` in handlers and middleware to correlate traces.

### Partial errors (non-500)

Main op succeeds, secondary step fails (e.g. revoke sessions after password change): log only, no change response:

```go
if err := RevokeSessionsByUser(
	c.Context(),
	db,
	&RevokeSessionsByUserParams{
		UserID: id,
	},
); err != nil {
	slog.ErrorContext(c.Context(), "could not revoke sessions after password reset", "user_id", id, "error", err)
}

return c.SendStatus(fiber.StatusOK)
```

### Failed login

Return generic `401` to client, log real error on server:

```go
if err != nil {
	slog.ErrorContext(c.Context(), "login failed", "email", req.Email, "error", err)

	return fiber.NewError(fiber.StatusUnauthorized, "invalid credentials")
}
```

## Verification

```bash
gofmt -w .
go build ./...
```

## Quick summary

| Area                  | Rule                                                                            |
| --------------------- | ------------------------------------------------------------------------------- |
| Structs               | `ID`, FKs, content, flags, domain dates, registry timestamps, archived, embeds  |
| Imports               | stdlib, third-party, internal. `goimports` orders                               |
| Multi-line calls      | One arg per line for `ctx` + payload                                            |
| Scan (sqlx)           | Blank before `var result`; blank before success `return`; no blank before error |
| HTTP error paths      | Specific first, then blank + `slog.ErrorContext` + blank + `500` generic        |
| Returns               | Blank only on terminal success and between `slog` and `500`                     |
| JSON / param literals | Same field grouping as struct definition                                        |

## See also

Deeper conventions (file naming, layout, validator): [golang-modular-monolith](https://github.com/FlamesX-128/skills/tree/main/skills/golang-modular-monolith) skill.
