# Agent to Agent

Minimal FIFO mailbox for agents in a shared repo. Each agent owns an inbox; peers deliver messages as individual files.

See [`SKILL.md`](./SKILL.md) for usage.

## Layout

```text
<repo>/.agent-to-agent/
├── kimi/
│   ├── inbox/      # pending messages
│   └── processed/  # delivered messages
└── claude/
    ├── inbox/
    └── processed/
```

Agent names are arbitrary lowercase strings. `kimi` and `claude` are just examples.

- `send` writes a temp file and atomically renames it into `<to>/inbox/`.
- `wait` blocks until mail arrives, prints the oldest message, and moves it to `processed/`.
- `drain` does the same for all pending messages without blocking.

## Why files

- No infrastructure required.
- Atomic rename prevents lost or clobbered messages.
- Plain Markdown; easy to inspect.

## Install

```bash
skills add FlamesX-128/skills --skill=agent-to-agent
```

## Requirements

Python >= 3.10, stdlib only. Uses inotify on Linux, polling fallback elsewhere.

## Development

```bash
cd scripts
uv run --locked pytest
uv run --locked mypy inbox.py
```

Repository-wide formatting is documented in the [root README](../../README.md#development).
