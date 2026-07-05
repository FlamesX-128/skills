# FlamesX-128 Skills

Agent skills I build and maintain — my own conventions and tooling, packaged as reusable [Agent Skills](https://agentskills.io/home). Compatible w/ the [`skills`](https://github.com/vercel-labs/skills) CLI (Claude, Codex, other agent runtimes). Each skill lives at `skills/<name>/`.

## Skills

| Skill                                                          | Description                                                                                                                                                                                                      |
| -------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **[agent-to-agent](skills/agent-to-agent/)**                   | Minimal FIFO mailbox for LLM agents. `send`, `wait`, `drain`; peer-to-peer, no built-in hierarchy.                                                                                                               |
| **[agent-workspace](skills/agent-workspace/)**                 | Isolated git worktree per agent for parallel, race-free edits.                                                                                                                                                   |
| **[code-paragraphs](skills/code-paragraphs/)**                 | Vertical-layout conventions for readable code across Go, TypeScript/JS, Svelte, and HTML: blank lines as paragraph breaks, role-based ordering of struct fields, props, and tag attributes, and import grouping. |
| **[golang-modular-monolith](skills/golang-modular-monolith/)** | Strict file-layout convention for Go modular monoliths.                                                                                                                                                          |

## Layout

Each skill bundles its own `SKILL.md`, `README.md`, `LICENSE`, and tooling (validators, formatters, examples). Installs independently w/ the `skills` CLI:

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Validating skills

Every skill follows the [Agent Skills specification](https://agentskills.io/specification). Validate w/ [`skills-ref`](https://github.com/agentskills/agentskills/tree/main/skills-ref), the reference validator from the spec authors.

Ephemeral run (no install, recommended):

```bash
uvx --from 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref' \
    skills-ref validate skills/code-paragraphs
```

Or install once, reuse:

```bash
uv tool install 'git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref'
skills-ref validate skills/code-paragraphs
```

## License

Each skill carries its own `LICENSE` file. See the skill directory for terms.
