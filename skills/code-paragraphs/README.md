# Code Paragraphs

Vertical layout as readability primitive: blank lines as paragraph breaks between groups of related fields, imports, statements, function steps. Language-agnostic principles + per-language reference.

## Install

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Structure

```
references/
├── go.md           operational recipes for Go (structs, DTOs, postgres infra, handlers)
└── literature.md   authors, quotes, empty-line debate, empirical evidence
LICENSE
README.md
SKILL.md            core principles + when-to-blank table
```

## Principles at a glance

- **Vertical openness between concepts** - blanks separate groups playing different roles.
- **Vertical density within concept** - no blanks inside group.
- **Vertical ordering: high -> low** - public API above private helpers; caller above callee (Newspaper Metaphor).
- **Co-locate declaration with first use.**
- **Formatter owns horizontal layout** - never align columns by hand.
- **Blank line earns place** - third blank in one function -> extract.

Full rules in [`SKILL.md`](SKILL.md). Go recipes in [`references/go.md`](references/go.md). Provenance + disagreements in [`references/literature.md`](references/literature.md).

## Format

- **[`format.bash`](format.bash)** - `mdformat` over Markdown. Maintenance only; not part of skill spec.

## License

MIT, © 2026 FlamesX-128. See [LICENSE](LICENSE).
