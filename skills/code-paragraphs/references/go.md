# Go reference

Vertical-layout recipes for Go. Applies to any Go codebase regardless of architecture.

For deeper structural conventions (file naming, layered module layout, validator) -> see [golang-modular-monolith](https://github.com/FlamesX-128/skills/tree/main/skills/golang-modular-monolith) skill.

Examples use generic `book` domain. Replace with own.

## Struct field grouping

Field order, blank between groups:

| Group               | Examples                                |
| ------------------- | --------------------------------------- |
| Identity            | `ID`                                    |
| Foreign keys        | `AuthorID`, `CategoryID`, `OwnerID`     |
| Content             | `Title`, `Summary`, `Price`             |
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

Domain timestamp like `RevokedAt` stays in domain-timestamps block, separated from `CreatedAt`:

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

Hierarchy (IDs, FKs), content, flags. Same blank-line grouping as model:

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

Pagination embed at end, separated from filter block:

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

Group fields by operation triggered:

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

Standard goimports grouping: stdlib, third-party, internal. Blanks between groups, no blanks within:

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

Let `goimports` handle order. No manual reorder.

## Multi-line function calls

Function call with `ctx`, payload, options, one arg per line:

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
- Blank before successful `return &result, nil`.
- **No** blank before `return nil, err` in intermediate error returns.

## Param literals in function calls

Group struct fields in literal by role, same as struct definition:

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

## HTTP error handling: specific then generic

- Specific response (`404`, `409`, `401`): no mandatory `slog`.
- Between specific branch and generic **500**: blank, `slog`, blank, `return`.

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

`fiber.NewError` style same:

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
| Return after `slog`, before 500                     | Yes (between slog and return) |
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

Every path returning **500** (or unexpected internal error) must log with `slog.ErrorContext` using request context:

```go
slog.ErrorContext(c.Context(), "could not list books", "error", err)
```

Include useful attributes: `user_id`, `book_id`, `author_id`, etc.

### No `slog.Error` without context in HTTP code

Always `ErrorContext` in handlers and middleware, needed to correlate with traces.

### Partial errors (non-500)

Main op succeeded but secondary step fails (e.g. revoking sessions after password change), log only, no change response:

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

Keep returning generic 401 to client, log real error on server:

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
| Structs               | `ID`, FKs, content, domain dates, registry timestamps, archived, embeds         |
| Imports               | stdlib, third-party, internal. Let `goimports` order                            |
| Multi-line calls      | One arg per line when `ctx` + payload                                           |
| Scan (sqlx)           | Blank before `var result`; blank before success `return`; no blank before error |
| HTTP error paths      | Specific first, then blank + `slog.ErrorContext` + blank + 500 generic          |
| Returns               | Blank only on terminal-success and between `slog` and 500                       |
| JSON / param literals | Same field grouping as struct definition                                        |
