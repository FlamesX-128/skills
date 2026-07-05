#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""One isolated git worktree per agent. Git refuses to check the same branch
out twice, so concurrent edits cannot race.

Usage: python3 workspace.py <command> --help
"""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import sys
from pathlib import Path

NAME_RE = re.compile(r"^[a-z][a-z0-9_-]{0,31}$")

EXIT_OK = 0
EXIT_USAGE = 2
EXIT_ENV = 3


class GitError(RuntimeError):
    pass


def cmd_add(args: argparse.Namespace) -> int:
    main = require_main_worktree()
    branch = f"agents/{args.name}"
    ref = f"refs/heads/{branch}"
    target = workspace_path(main, args.name)
    git(main, "worktree", "prune")

    stanza = existing_workspace(main, ref)
    if stanza is not None:
        existing = Path(stanza["worktree"])
        if existing != target or not target.is_dir():
            print(
                f"error: agent '{args.name}' already has a workspace at {existing}",
                file=sys.stderr,
            )
            return EXIT_USAGE

        print(f"workspace: {target}")
        print(f"branch: {branch} (already attached)")
        return EXIT_OK

    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        print(f"error: {target} exists and is not an empty directory", file=sys.stderr)
        return EXIT_USAGE

    target.parent.mkdir(parents=True, exist_ok=True)
    detail = add_or_reattach(main, target, branch, ref, args.base or "HEAD")
    print(f"workspace: {target}")
    print(f"branch: {branch} ({detail})")

    return EXIT_OK


def cmd_remove(args: argparse.Namespace) -> int:
    main = require_main_worktree()
    branch = f"agents/{args.name}"
    ref = f"refs/heads/{branch}"
    stanza = existing_workspace(main, ref)
    if stanza is None:
        print(f"note: no workspace for '{args.name}' (nothing to do)")
        return EXIT_OK

    target = Path(stanza["worktree"])
    # git can remove the worktree your own cwd is inside; guard against it.
    if Path(os.path.realpath(Path.cwd())).is_relative_to(Path(os.path.realpath(target))):
        print("error: refusing to remove the workspace your cwd is inside", file=sys.stderr)
        return EXIT_USAGE

    remove = ["worktree", "remove", "--force"] if args.force else ["worktree", "remove"]
    git(main, *remove, str(target))
    if args.delete_branch:
        git(main, "branch", "-D" if args.force else "-d", branch)
    git(main, "worktree", "prune")

    kept = "deleted" if args.delete_branch else "kept (committed work survives)"
    print(f"removed: {target}")
    print(f"branch: {branch} {kept}")

    return EXIT_OK


def cmd_list(args: argparse.Namespace) -> int:
    main = require_main_worktree()
    prefix = "refs/heads/agents/"
    rows = [s for s in worktree_stanzas(main) if s.get("branch", "").startswith(prefix)]
    if not rows:
        print("no agent workspaces; create one: workspace.py add <name>")
        return EXIT_OK

    for stanza in rows:
        name = stanza["branch"].removeprefix(prefix)
        line = f"{name}  {stanza['worktree']}  [agents/{name} @ {stanza.get('HEAD', '?')[:12]}]"
        if "prunable" in stanza:
            line += "  PRUNABLE: dir vanished; re-run add (uncommitted work is gone)"
        print(line)

    return EXIT_OK


def cmd_path(args: argparse.Namespace) -> int:
    main = require_main_worktree()
    branch = f"agents/{args.name}"
    ref = f"refs/heads/{branch}"
    stanza = existing_workspace(main, ref)
    if stanza is None:
        print(f"error: no workspace for '{args.name}'", file=sys.stderr)
        return EXIT_USAGE

    target = Path(stanza["worktree"])
    if "prunable" in stanza or not target.is_dir():
        print(f"error: workspace dir for '{args.name}' is missing", file=sys.stderr)
        return EXIT_USAGE

    print(target)

    return EXIT_OK


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="workspace.py",
        description="One isolated git worktree per agent, on branch agents/<name>.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="create (or reattach) a worktree on branch agents/<name>")
    p.add_argument("name", type=valid_name, help="lowercase agent name")
    p.add_argument("--base", help="ref a NEW branch starts from (default: HEAD)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("remove", help="remove a worktree (branch kept unless --delete-branch)")
    p.add_argument("name", type=valid_name, help="lowercase agent name")
    p.add_argument("--force", action="store_true", help="discard dirty/untracked files too")
    p.add_argument("--delete-branch", action="store_true", help="also delete branch agents/<name>")
    p.set_defaults(func=cmd_remove)

    p = sub.add_parser("list", help="list agent workspaces (flags vanished dirs)")
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("path", help="print the absolute path of an existing workspace")
    p.add_argument("name", type=valid_name, help="lowercase agent name")
    p.set_defaults(func=cmd_path)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result: int = args.func(args)

        return result
    except KeyboardInterrupt:
        return 130
    except (GitError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_ENV


def git(cwd: Path, *args: str) -> str:
    run = subprocess.run(
        ["git", "-C", str(cwd), *args], capture_output=True, text=True, check=False
    )
    if run.returncode != 0:
        raise GitError(run.stderr.strip() or f"git {' '.join(args)} failed")

    return run.stdout


def worktree_stanzas(repo: Path) -> list[dict[str, str]]:
    """Parse `git worktree list --porcelain` (newline stanzas)."""
    stanzas: list[dict[str, str]] = []
    current: dict[str, str] = {}
    for line in git(repo, "worktree", "list", "--porcelain").splitlines():
        if not line:
            if current:
                stanzas.append(current)
                current = {}
            continue

        key, _, value = line.partition(" ")
        current[key] = value

    if current:
        stanzas.append(current)

    return stanzas


def main_worktree_toplevel() -> Path | None:
    """Top-level of the MAIN worktree, identical for every linked worktree."""
    try:
        run = subprocess.run(
            ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
            capture_output=True,
            text=True,
            check=False,
        )
        if run.returncode != 0:
            run = subprocess.run(
                ["git", "rev-parse", "--git-common-dir"],
                capture_output=True,
                text=True,
                check=False,
            )
    except FileNotFoundError:
        return None

    if run.returncode != 0:
        return None

    common = (Path.cwd() / run.stdout.strip()).resolve()

    try:
        stanzas = worktree_stanzas(common)
    except GitError:
        return common.parent if common.name == ".git" else common

    if stanzas and "worktree" in stanzas[0]:
        return Path(stanzas[0]["worktree"])

    return common.parent if common.name == ".git" else common


def require_main_worktree() -> Path:
    main = main_worktree_toplevel()
    if main is None:
        raise GitError("agent-workspace needs a git repository")

    return main


def valid_name(value: str) -> str:
    if not NAME_RE.match(value):
        raise argparse.ArgumentTypeError(
            f"invalid agent name {value!r}: want lowercase matching ^[a-z][a-z0-9_-]{{0,31}}$"
        )

    return value


def repo_slug_hash(main: Path) -> str:
    real = os.path.realpath(main)
    digest = hashlib.sha256(real.encode()).hexdigest()[:8]
    slug = re.sub(r"[^a-zA-Z0-9._-]+", "-", Path(real).name).strip("-").lower() or "repo"

    return f"{slug}-{digest}"


def workspace_path(main: Path, agent: str) -> Path:
    env = os.environ.get("AGENT_WORKSPACE_ROOT")
    if env:
        base = Path(env).expanduser().resolve()
    else:
        state = os.environ.get("XDG_STATE_HOME")
        home_state = Path(state).expanduser() if state else Path.home() / ".local" / "state"
        # Use XDG state, not /tmp (wiped at boot) or /run/user (gone at logout).
        base = home_state / "agent-workspace" / "worktrees"

    # Always append repo identity so an override cannot reintroduce cross-repo collisions.
    return base / repo_slug_hash(main) / agent


def existing_workspace(main: Path, ref: str) -> dict[str, str] | None:
    for stanza in worktree_stanzas(main):
        if stanza.get("branch") == ref:
            return stanza

    return None


def branch_exists(main: Path, ref: str) -> bool:
    run = subprocess.run(
        ["git", "-C", str(main), "show-ref", "--verify", "--quiet", ref], check=False
    )

    return run.returncode == 0


def add_or_reattach(main: Path, target: Path, branch: str, ref: str, base: str) -> str:
    """Run `git worktree add`, converging on a concurrent winner."""
    reattach = branch_exists(main, ref)
    try:
        if reattach:
            git(main, "worktree", "add", str(target), branch)
        else:
            git(main, "worktree", "add", str(target), "-b", branch, base)
    except GitError as exc:
        if "cannot lock ref" not in str(exc):
            raise

        winner = existing_workspace(main, ref)
        if winner is None or Path(winner["worktree"]) != target:
            raise

        return "created by a concurrent add"

    return "reattached, keeps prior commits" if reattach else f"new, base {base}"


if __name__ == "__main__":
    sys.exit(main())
