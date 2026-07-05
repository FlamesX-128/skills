---
name: agent-workspace
description: Isolated git worktree per agent for parallel, race-free edits.
license: MIT
compatibility: Python >=3.10, git >= 2.31. No external deps.
allowed-tools: Read Edit Write Glob Grep Bash(python3:*) Bash(git:*)
metadata:
    user-invocable: false
---

# Agent Workspace

CLI: [`scripts/workspace.py`](./scripts/workspace.py). Stdlib Python. Each agent gets its own worktree on branch `agents/<name>`. Git refuses to check out the same branch in two worktrees, so edits cannot race.

Examples use model names (`claude`, `kimi`, `codex`, ...), but any name works. This skill only answers "where do I safely edit".

## Get workspace

```bash
python3 $SKILL_DIR/scripts/workspace.py add claude
```

Prints the absolute path. Idempotent: re-running reprints the same path. Workspaces live under `~/.local/state/agent-workspace/worktrees/<repo>-<hash>/<name>`; override with `AGENT_WORKSPACE_ROOT`.

## Continue peer work

```bash
python3 $SKILL_DIR/scripts/workspace.py add kimi --base agents/claude
```

Creates `agents/kimi` from the tip of `agents/claude`. Each agent works in its own copy; reconcile later with normal git.

## List / remove

```bash
python3 $SKILL_DIR/scripts/workspace.py list
python3 $SKILL_DIR/scripts/workspace.py remove claude
python3 $SKILL_DIR/scripts/workspace.py remove claude --delete-branch
```

`remove` keeps the branch by default; the directory is disposable.

## Path only

For scripts:

```bash
python3 $SKILL_DIR/scripts/workspace.py path claude
```

Prints only the absolute path; exits 0 if it exists, non-zero otherwise.

## Notes

- `add` reattaches if the workspace already exists and recreates the directory if it vanished.
- `remove` refuses to delete the workspace your cwd is inside.
- Merge and rebase stay in git; this skill only creates the workspace.
