# FlamesX-128 Skills

Personal collection of [Agent Skills](https://agentskills.io/home), compat w/ [`skills`](https://github.com/vercel-labs/skills) CLI (Claude, Codex, other agent runtimes). Each skill self-contained at `skills/<name>/`.

## Skills

| Skill                                      | Description                                             |
| ------------------------------------------ | ------------------------------------------------------- |
| **[golang-modular-monolith](skills/golang-modular-monolith/)** | Strict file-layout convention for Go modular monoliths. |

## Layout

Each skill fully self-contained — bundles own `SKILL.md`, `README.md`, `LICENSE`, any tooling (validators, formatters, examples) — install independently w/ `skills` CLI:

```bash
pnpm dlx skills add FlamesX-128/skills --skill=golang-modular-monolith
```

Add `-g` for global install, or `--skill='*'` to install all skills in repo.

External skills mirrored from other repos pinned in [`skills-lock.json`](skills-lock.json).

## Validating skills

Every skill follows [Agent Skills specification](https://agentskills.io/specification). Validate w/ [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref) — reference validator from spec authors.

Ephemeral run (no install, recommended):

```bash
uvx --from 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref' \
    skills-ref validate skills/golang-modular-monolith
```

Or install once, reuse:

```bash
uv tool install 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref'
skills-ref validate skills/golang-modular-monolith
```

## License

Each skill carries own `LICENSE` file. See skill directory for terms.
