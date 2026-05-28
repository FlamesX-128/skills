---
name: code-paragraphs
description: Vertical layout signals logical structure. Blank lines as paragraph breaks between groups of related fields, imports, statements, function steps. Use when adding struct fields, ordering imports, reviewing handler error paths, judging when blank line earns place vs signals missing extraction, or enforcing layout consistency.
license: MIT
compatibility: Language-agnostic principles. Per-language recipes in `references/`.
allowed-tools: Read Edit Write Glob Grep Bash(gofmt:*) Bash(goimports:*) Bash(go:*) Bash(prettier:*) Bash(black:*) Bash(rustfmt:*) Bash(git:*)
metadata:
  author: FlamesX-128
  version: 1.0.0
  user-invocable: true
---

# Code Paragraphs

Vertical layout shows logical structure. Group related lines into paragraphs separated by blank lines; formatter handles horizontal whitespace.

> "Good visual layout shows the logical structure of a program." - Steve McConnell

References:

- Go (structs, imports, multi-line calls, sqlx scan, slog, error paths) -> [Go reference](./references/go.md)
- Authors, quotes, empty-line debate, empirical evidence -> [Literature](./references/literature.md)

## Core principles

1. **Vertical openness between concepts.** Blank line separates groups playing different roles - validation vs compute vs response; identity vs content vs timestamps. _(Martin, Clean Code Ch. 5; McConnell, Code Complete Ch. 31.)_
2. **Vertical density within concept.** No blanks inside group - gap weakens implied bond. _(Martin, "Vertical Density.")_
3. **Vertical ordering: high to low.** Public API above private helpers, caller above callee, exports above internals - Newspaper Metaphor / Stepdown Rule. _(Martin; Kent Beck, Smalltalk Best Practice Patterns.)_
4. **Co-locate declaration with first use.** Variable on line above use; no hoist locals to top. _(Martin, "Vertical Distance.")_
5. **Formatter owns horizontal layout.** Never align `=` columns or struct tags by hand - `gofmt` / Prettier / Black / rustfmt own that. _(Rob Pike: "Gofmt's style is no one's favorite, yet gofmt is everyone's favorite.")_
6. **Blank line earns place.** Third blank inside one function -> extract method. Blanks mark sub-steps; not substitute for naming. _(PEP 8 "sparingly"; Bugayenko's "empty line is code smell" - see [literature §3](./references/literature.md#3-the-counterargument-an-empty-line-is-a-code-smell).)_

## When to use blank line

| Situation                                                                 | Blank?          |
| ------------------------------------------------------------------------- | --------------- |
| Between top-level decls (functions, types)                                | Yes             |
| Between import groups (stdlib / third-party / local)                      | Yes             |
| Between field groups in struct (identity / content / timestamps)          | Yes             |
| Inside same field group                                                   | No              |
| Between function sub-steps (validation -> compute -> respond)             | Yes (sparingly) |
| Before early-return on error (`if err != nil { return err }`)             | No              |
| Before terminal success return                                            | Yes             |
| Between observability call (e.g. `slog.ErrorContext`) and response/return | Yes             |
| Around single statement                                                   | No              |

## When NOT

- Between variable and first use.
- Between error check and early return it guards.
- Inside same semantic group (sibling struct fields, related imports, switch case members).
- "For breathing room" without logical reason. Function long -> extract, not whitespace.

## Newspaper Metaphor applied

Top-to-bottom: abstraction decreases.

```
1. package doc / file header
2. imports (stdlib, third-party, local)
3. constants & vars
4. exported types
5. constructors & primary methods
6. private helpers
```

A calls B, A above B.

## Semantic grouping in structures

Struct, DTO, JSON literal - same rule. Group by role, one blank per group:

- **Identity** (`ID`)
- **Hierarchy / foreign keys** (`UserID`, `ClientID`, `OrgID`)
- **Content** (entity payload)
- **Domain timestamps** (`StartDate`, `ExpiresAt`, `RevokedAt`)
- **Registry timestamps** (`CreatedAt`, `UpdatedAt`)
- **Soft delete** (`ArchivedAt`)
- **Embeds** (composed traits last)

Field with no obvious group = smell. Either belongs in existing group, or struct does two things.

## Horizontal whitespace

Run formatter. No argue. No disable rules locally.

| Language        | Formatter                          |
| --------------- | ---------------------------------- |
| Go              | `gofmt` + `goimports`              |
| Python          | `black` + `isort`                  |
| TypeScript / JS | `prettier` + ESLint `import/order` |
| Rust            | `rustfmt`                          |
| Java            | `google-java-format`               |

Manual `=` align -> next longer name undoes it.

## Imports

Group by source, blank between groups, no blanks within:

```
stdlib
[ blank ]
third-party (github.com/..., npm, PyPI)
[ blank ]
internal cross-module
[ blank ]
internal same-module
```

Formatter owns import order (`goimports`, `isort`, ESLint `import/order` with `newlines-between: "always"`) -> let it. No manual reorder.

## Errors: specific -> generic

Multiple branches (typed -> generic 500) -> specific first, blank before generic tail:

```go
if errors.Is(err, ErrNotFound) {
    return NotFound(...)
}

logErrorWithContext(...)

return InternalError(...)
```

Blank marks boundary between "handled specifically" and "logging-then-failing." Without it, log fuses to previous branch.

## When genuinely don't know

- Section needs comment to explain -> extract named function. Name replaces comment + blank.
- Struct has 10+ fields no obvious groups -> struct does too much; split.
- Formatter and rule disagree -> trust formatter. No fight locally.

## Empirical note

Buse & Weimer (IEEE TSE, 2010): 120 annotators x 100 Java snippets. Blank-line count = strong positive predictor of readability, _more_ important than comment count. Model descriptive, not prescriptive - no sprinkle mechanically. Group by meaning, not line count.

Full provenance - Knuth, Martin, McConnell, Beck, Fowler, Pike, Torvalds, Bugayenko counterargument, empirical record - in [`references/literature.md`](./references/literature.md).

## Verification

Run project formatter + build after applying:

```bash
# Go
gofmt -w .
go build ./...

# TypeScript / JS
pnpm prettier --write .
pnpm tsc --noEmit

# Python
black .
isort .
```

Layout changes never alter behavior. Build breaks -> something else changed.
