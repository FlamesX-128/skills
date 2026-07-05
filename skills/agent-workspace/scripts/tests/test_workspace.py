"""Tests for workspace.py — one git worktree per agent."""

import argparse
import subprocess
from pathlib import Path

import pytest

import workspace


def make_repo(path: Path) -> None:
    subprocess.run(["git", "init", "-q", str(path)], check=True)

    subprocess.run(
        [
            "git",
            "-C",
            str(path),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=t",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "--allow-empty",
            "-q",
            "-m",
            "init",
        ],
        check=True,
    )


@pytest.fixture()
def repo(tmp_path, monkeypatch):
    repo = tmp_path / "repo"
    make_repo(repo)
    monkeypatch.chdir(repo)
    monkeypatch.setenv("AGENT_WORKSPACE_ROOT", str(tmp_path / "ws"))
    return repo


def test_valid_name_rejects_uppercase():
    with pytest.raises(argparse.ArgumentTypeError):
        workspace.valid_name("Kimi")


def test_add_idempotent_list_remove(repo, capsys):
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_OK
    out = capsys.readouterr().out
    target = Path(out.splitlines()[0].removeprefix("workspace: "))
    assert target.is_dir()
    assert "branch: agents/kimi (new, base HEAD)" in out

    # Idempotent re-add converges on the same path.
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_OK
    assert f"workspace: {target}" in capsys.readouterr().out

    assert workspace.main(["list"]) == workspace.EXIT_OK
    assert "kimi" in capsys.readouterr().out

    assert workspace.main(["remove", "kimi"]) == workspace.EXIT_OK
    out = capsys.readouterr().out
    assert "kept" in out
    assert not target.exists()

    # Branch survives; re-add reattaches it.
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_OK
    assert "reattached" in capsys.readouterr().out


def test_add_with_base_seeds_from_another_agents_branch(repo, capsys):
    workspace.main(["add", "kimi"])
    kimi_ws = Path(capsys.readouterr().out.splitlines()[0].removeprefix("workspace: "))
    (kimi_ws / "partial.py").write_text("def add(a, b):\n    pass\n")
    subprocess.run(["git", "-C", str(kimi_ws), "add", "partial.py"], check=True)

    subprocess.run(
        [
            "git",
            "-C",
            str(kimi_ws),
            "-c",
            "user.email=t@t",
            "-c",
            "user.name=kimi",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "wip",
        ],
        check=True,
    )

    assert workspace.main(["add", "claude", "--base", "agents/kimi"]) == workspace.EXIT_OK
    out = capsys.readouterr().out
    claude_ws = Path(out.splitlines()[0].removeprefix("workspace: "))
    assert "base agents/kimi" in out
    assert claude_ws != kimi_ws
    assert (claude_ws / "partial.py").read_text() == "def add(a, b):\n    pass\n"


def test_add_after_dir_vanished(repo, capsys):
    workspace.main(["add", "kimi"])
    target = Path(capsys.readouterr().out.splitlines()[0].removeprefix("workspace: "))

    # Simulate a cleaner/reboot deleting the dir behind git's back.
    subprocess.run(["rm", "-rf", str(target)], check=True)
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_OK
    assert target.is_dir()


def test_remove_dirty_needs_force(repo, capsys):
    workspace.main(["add", "kimi"])
    target = Path(capsys.readouterr().out.splitlines()[0].removeprefix("workspace: "))
    (target / "untracked.txt").write_text("wip")

    assert workspace.main(["remove", "kimi"]) == workspace.EXIT_ENV
    assert "force" in capsys.readouterr().err
    assert workspace.main(["remove", "kimi", "--force"]) == workspace.EXIT_OK


def test_remove_refuses_own_cwd(repo, monkeypatch, capsys):
    workspace.main(["add", "kimi"])
    target = Path(capsys.readouterr().out.splitlines()[0].removeprefix("workspace: "))
    monkeypatch.chdir(target)

    assert workspace.main(["remove", "kimi"]) == workspace.EXIT_USAGE
    assert "cwd" in capsys.readouterr().err
    assert target.is_dir()


def test_add_same_name_twice_from_different_root_is_rejected(repo, monkeypatch, capsys):
    workspace.main(["add", "kimi"])
    capsys.readouterr()

    # A second attempt at the same name, even under a different root override,
    # must be refused rather than silently producing a second workspace.
    monkeypatch.setenv("AGENT_WORKSPACE_ROOT", str(Path.cwd().parent / "other-ws"))
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_USAGE
    assert "already has a workspace" in capsys.readouterr().err


def test_path_prints_existing_workspace(repo, capsys):
    assert workspace.main(["add", "kimi"]) == workspace.EXIT_OK
    target = Path(capsys.readouterr().out.splitlines()[0].removeprefix("workspace: "))

    assert workspace.main(["path", "kimi"]) == workspace.EXIT_OK
    assert capsys.readouterr().out.strip() == str(target)


def test_path_fails_when_workspace_missing(repo, capsys):
    assert workspace.main(["path", "kimi"]) == workspace.EXIT_USAGE
    assert "no workspace" in capsys.readouterr().err
