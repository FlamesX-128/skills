# Code Paragraphs

Vertical layout as readability primitive: blank lines as paragraph breaks between groups of related fields, members, imports, statements, and function steps — plus role-based ordering of struct fields, props, and tag attributes. Language-agnostic core + per-language references (Go, TypeScript, Svelte, and more).

## Install

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Structure

```
code-paragraphs/
├── SKILL.md              core principles + when-to-blank tables + member ordering
├── README.md
├── LICENSE
└── references/
    ├── go.md             recipes for Go (structs, DTOs, sqlx, slog handlers)
    ├── typescript.md     imports, type-import separation, interfaces, tooling
    ├── python.md          PEP 8 layout, TYPE_CHECKING imports, dataclass fields
    ├── svelte.md         runes order, snippets, attribute order (inherits ts + html)
    ├── html.md           attribute order by role
    └── literature.md     authors, quotes, empty-line debate, empirical evidence
```

## Principles at a glance

- **Vertical openness between concepts** — blanks separate groups playing different roles.
- **Vertical density within concept** — no blanks inside a group.
- **Vertical ordering: high → low** — public above private, caller above callee, essential above incidental (Newspaper Metaphor / Stepdown Rule).
- **Order members by role** — struct fields, props, DTO fields: data → state → behavior → presentation → handlers → slots, blank per group.
- **Order attributes by role** — markup tags: bindings → directives → events → styling (per-language scheme).
- **Co-locate declaration with first use.**
- **Formatter owns horizontal layout** — never align columns by hand.
- **Blank line earns its place** — third blank in one function → extract.

Full rules in [`SKILL.md`](SKILL.md). Per-language recipes in [`references/`](references/). Provenance + disagreements in [`references/literature.md`](references/literature.md).

## Language coverage

| Language                | Reference                                 | Key tooling                                                   |
| ----------------------- | ----------------------------------------- | ------------------------------------------------------------- |
| Go                      | [go.md](references/go.md)                 | `gofmt`, `goimports`                                          |
| TypeScript / JavaScript | [typescript.md](references/typescript.md) | `eslint-plugin-perfectionist`, `@typescript-eslint`, Prettier |
| Python                  | [python.md](references/python.md)         | `ruff` (format + isort), PEP 8                                |
| Svelte                  | [svelte.md](references/svelte.md)         | `eslint-plugin-svelte`, `svelte-check`                        |
| HTML                    | [html.md](references/html.md)             | convention (no formatter reorders attributes)                 |

Svelte inherits TypeScript (`<script>`) and HTML (markup); its reference carries only the Svelte-specific delta.

## Format

Repository-wide formatting is documented in the [root README](../../README.md#development).

## License

MIT, © 2026 FlamesX-128. See [LICENSE](LICENSE).
