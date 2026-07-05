---
name: code-paragraphs
description: Vertical layout signals logical structure. Blank lines as paragraph breaks between groups of related lines — struct fields, interface members, component props, imports, statements, function steps. Attributes and members ordered by role. Use when adding or reordering fields/props, grouping imports, ordering tag attributes, judging when a blank line earns its place vs signals a missing extraction, or enforcing layout consistency across Go, TypeScript, Svelte, HTML.
license: MIT
compatibility: Language-agnostic core. Per-language recipes in `references/`.
allowed-tools: Read Edit Write Glob Grep Bash(gofmt:*) Bash(goimports:*) Bash(go:*) Bash(prettier:*) Bash(eslint:*) Bash(black:*) Bash(ruff:*) Bash(rustfmt:*) Bash(git:*)
metadata:
    author: FlamesX-128
    version: 2.0.0
    user-invocable: true
---

# Code Paragraphs

> "Good visual layout shows the logical structure of a program." — Steve McConnell

**One rule:** blank line = change of role. No blank = same role. Formatter owns horizontal space; you own vertical.

## References

| Context                   | File                                        |
| ------------------------- | ------------------------------------------- |
| TypeScript / JavaScript   | [typescript.md](./references/typescript.md) |
| Python                    | [python.md](./references/python.md)         |
| Svelte                    | [svelte.md](./references/svelte.md)         |
| HTML markup               | [html.md](./references/html.md)             |
| Go                        | [go.md](./references/go.md)                 |
| Authors, quotes, evidence | [literature.md](./references/literature.md) |

## Principles

1. **Openness between concepts.** Blank separates groups playing different roles — validation vs compute vs response; identity vs content vs timestamps. _(Martin Ch. 5; McConnell Ch. 31.)_
2. **Density within a concept.** No blank inside a group. A gap weakens the implied bond.
3. **Order high → low.** Public above private, caller above callee, essential above incidental. Newspaper Metaphor / Stepdown Rule. _(Martin; Beck.)_
4. **Declaration beside first use.** No hoisting locals to the top.
5. **Formatter owns horizontal.** Never hand-align `=` columns or tags. `gofmt` / Prettier / Black / rustfmt own that. _(Pike.)_
6. **Blank earns its place.** Third blank inside one function → extract method. Blanks mark sub-steps, not a substitute for naming. _(PEP 8 "sparingly"; Bugayenko "empty line is a code smell".)_

## When to blank

| Situation                                                               | Blank?          |
| ----------------------------------------------------------------------- | --------------- |
| Between top-level decls (functions, types)                              | Yes             |
| Between import groups                                                   | Yes             |
| Between member groups (by role)                                         | Yes             |
| Inside same member group                                                | No              |
| Between adjacent block statements (`for`, `while`, `if`, `with`, `try`) | Yes             |
| Between function sub-steps (validate → compute → respond)               | Yes (sparingly) |
| Before early-return on error                                            | No              |
| After an early-exit block (`return`/`raise`/`continue`/`break`)         | Yes             |
| Before terminal success return                                          | Yes             |
| Assignment whose value wraps to multiple lines                          | Yes             |
| Around a single statement                                               | No              |

## When NOT

- Between variable and first use.
- Between error check and the early return it guards.
- Inside one semantic group (sibling fields, related imports, switch case members).
- "For breathing room" with no logical reason. Function too long → extract, not whitespace.

## Order members by role

Struct fields, interface members, DTO fields, component props — one rule. Group by role, blank per group, essential → incidental.

| Group           | Role                             | Examples                                |
| --------------- | -------------------------------- | --------------------------------------- |
| Data / identity | What it _is_; core inputs        | `id`, `label`, `href`, `items`, `value` |
| State / flags   | Booleans describing condition    | `disabled`, `required`, `expanded`      |
| Behavior        | Actions, menus, commands         | `actions`, `commands`                   |
| Presentation    | Visual variants, dimensions      | `variant`, `align`, `width`             |
| Handlers        | `on*` / callbacks                | `onselect`, `onchange`                  |
| Timestamps      | Created / updated / deleted      | `createdAt`, `updatedAt`, `archivedAt`  |
| Slots / embeds  | Injected markup, composed traits | `icon`, `header`, `children`, `footer`  |

```go
type Book struct {
	ID int

	AuthorID   int
	CategoryID int

	Title string
	Price float64

	Active bool

	PublishedAt time.Time
	CreatedAt   time.Time

	sharedmodel.Auditable
}
```

- Only present groups appear.
- `AuthorID` (foreign key) before `Title` (content) because _hierarchy_ precedes _payload_ — order by role, not by name length.
- Within a group: most **meaningful** order (render order top→bottom, logical sequence). Length only as last resort, for genuinely interchangeable members.
- **Member fitting no group = smell.** It belongs to an existing role, or the unit does two things → split.

## Multi-line declaration = own paragraph

A one-liner shares a paragraph with same-shaped siblings. Once a value wraps (length or compound logic), blank it off from the compact lines above. The wrap already broke density.

```go
sameSize := item.Width == target.Width
sameColor := item.Color == target.Color

visible := item.OwnerID == 0 ||
	item.OwnerID == session.UserID
```

## Length & naming are diagnostics, not sort keys

- **Length.** A short→long staircase reads calmly but never order _by_ it — it fights role order, breaks on rename, and LLMs apply it inconsistently. It falls out for free once grouped by role. Uneven lengths in a group = signal the group is heterogeneous, split it.
- **Naming.** Name communicates role; clear role → grouping falls out. A name that lands in no group is the same warning as an ungroupable field.

## Imports

Groups by source, blank between, none within. Formatter owns order — never reorder by hand. Some languages also split type-only imports into their own group (see references).

```go
import (
	"context"
	"errors"

	"github.com/jmoiron/sqlx"

	"example.com/app/internal/book"
)
```

## Attributes in markup

Order by role or alphabetically per language convention. Bindings first, then directives, events, styling. Exact scheme and tooling → see references.

## Scope: layout only

These rules arrange what exists. Whether a prop _should_ exist is API design, not layout — out of scope. LLMs over-supply props by completing toward the "fully configurable component" pattern; correct that with a separate minimalism rule ("every prop earns its place"), not blank lines.

## Verify

Run the project formatter + build. Layout never changes behavior; a broken build means something else changed.

```bash
# Go
gofmt -w . && go build ./...
# TS / JS / Svelte
pnpm prettier --write . && pnpm eslint --fix . && pnpm tsc --noEmit
# Python
ruff format . && ruff check --fix .
```
