# Agent Workspace

Tiny CLI: each agent gets its own isolated git worktree on branch `agents/<name>`, so agents can edit the same repo in parallel without racing. No locks: git refuses to check out one branch in two worktrees.

See [`SKILL.md`](./SKILL.md) for the full command reference.

## Why

Two agents editing the same working tree race: whoever writes last wins silently. Fix: don't share the working tree. Each agent gets an independent checkout and can edit, run, and commit in parallel.

An agent can also continue a peer's work with `--base agents/<peer>`, in its own copy, without touching the peer's.

## Quickstart

```bash
T=scripts/workspace.py

python3 $T add claude
python3 $T add kimi --base agents/claude
python3 $T add codex --base agents/claude
python3 $T list
python3 $T remove claude
```

## Requirements

Python >= 3.10, git >= 2.31. No external deps.

## Development

```bash
cd scripts
uv run --locked pytest
uv run --locked mypy workspace.py
```

Repository-wide formatting is documented in the [root README](../../README.md#development).

## Files

| File                     | Purpose            |
| ------------------------ | ------------------ |
| [`SKILL.md`](./SKILL.md) | Command reference. |
| `scripts/workspace.py`   | CLI.               |
| `scripts/tests/`         | Pytest suite.      |
| `LICENSE`                | MIT.               |
