---
name: code-paragraphs
description: Apply code style when writing, editing, reviewing, or cleaning source code. Group statements and members into blank-line paragraphs by role. Includes a TypeScript/JavaScript profile with explicit import, control-flow, comment, and verification rules, plus language-specific references for Go, Python, Svelte, and HTML.
license: MIT
metadata:
    author: FlamesX-128
    version: 3.0.0
    user-invocable: true
---

# Code Paragraphs

**One rule:** blank line = change of role. No blank = same role. Formatter owns horizontal space; you own vertical.

## Apply the relevant profile first

For TS/JS, read [typescript.md](./references/typescript.md) before editing. Its concrete rules and exceptions take precedence over the general tables below. For tooling setup or migration, also read [typescript-tooling.md](./references/typescript-tooling.md); reusable configuration lives in [assets/ts-style](./assets/ts-style/).

For other languages, read only the corresponding reference. TS-specific bans on loops, ternaries, and mutable bindings do not extend to other languages or framework markup. Explicit user and repository instructions take precedence over this skill.

1. Identify the touched files, effective formatter/linter config, and generator-owned paths.
2. Apply paragraph and member rules while writing. A formatter cannot infer semantic roles.
3. Run the existing project formatting, lint, and validation commands for the affected scope.
4. Inspect the final diff against the applicable profile's manual checks. Lint passing alone does not establish compliance.

Keep changes within the requested scope. Installing the skill does not request a repository-wide migration. Preserve evaluation order, side effects, public signatures, directive attachment, and generated output. Report an unresolved style conflict instead of suppressing it or silently claiming success.

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
6. **Blank earns its place.** Consider extraction when a paragraph needs an independent name or responsibilities diverge. Do not extract merely because a function has three blank lines. _(PEP 8 "sparingly"; Bugayenko "empty line is a code smell".)_

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

- **Length.** Preserve semantic role and usage order first. Apply a language profile’s explicit tiebreak within interchangeable members; do not split a coherent group merely because names differ in length.
- **Naming.** Name communicates role; clear role → grouping falls out. A name that lands in no group is the same warning as an ungroupable field.

## Imports

Use the language profile’s group definition. In TS/JS the source module is the group: its value and type-only imports stay adjacent. Other languages may use broader source categories. Preserve runtime initialization order; alphabetization never justifies changing side effects.

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

## Scope and verification

The shared core concerns layout. The TS/JS profile also specifies control flow, optional properties, and comments; those edits require behavior and type checks, not just formatting. Do not introduce API options, rewrite framework constructs, or change exported parameter order to satisfy layout.

Use the project's existing commands on the affected files or packages. Run formatting and lint fixes, inspect their diff, then run checks without fixes to detect formatter/linter cycles. Run the relevant typecheck, tests, and build when code or configuration changes. State checks that could not run. For documentation-only changes, validate links and formatting instead.
