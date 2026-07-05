# Golang Modular Monolith

Strict file and directory convention for Go modular monoliths: deterministic file placement, closed vocabularies per layer, bundled validator.

## Install

```bash
skills add FlamesX-128/skills --skill=golang-modular-monolith
```

## Structure

```
examples/book/                worked book module demonstrating file placement
references/
├── http-layer.md             routes, sub-resources vs PATCH, forbidden names
├── postgres-layer.md         SQL ops, modifiers, CTEs, one-op-per-file
├── service-layer.md          function naming per layer, banned tokens
├── tool-slot.md              which layers get tool/, naming rules
├── multi-entity.md           sub-entity vs separate module decision
└── validator-development.md  extending the validator
scripts/validate.py           Python validator (74 tests, ruff, mypy strict)
SKILL.md                      cardinal rules + module layout tree
```

## Validate

```bash
python3 scripts/validate.py /path/to/your/project
```

Exit `0` = clean. Explore the example: `python3 scripts/validate.py examples/book`.

## Convention at a glance

- **Layers**: `model/`, `service/`, `infrastructure/`, `interface/`. Deps flow inward.
- **Closed vocabularies**:
    - SQL: `select / insert / update / delete / merge / truncate`
    - HTTP: `get / post / put / patch / delete / head / options / query`
    - Service: free-form domain verbs (`create`, `archive`, `login`, …)
- **File naming**: `<entity>_<operation>.<ext>`. Exceptions: `model/<entity>.go`, `interface/http/register.go`, `tool/` helpers.
- **Domain actions**: sub-resource only if it produces a new tracked entity. Field flips → `PATCH /<entity>/:id`.

Full spec in [`SKILL.md`](SKILL.md). Layer details in [`references/`](references/).

## Format

- **[`format.bash`](format.bash)** — `ruff format` + `mdformat`.
- **[`examples/book/format.bash`](examples/book/format.bash)** — `gofmt` + `sql-formatter`.

## License

MIT, © 2026 FlamesX-128. See [LICENSE](LICENSE).
