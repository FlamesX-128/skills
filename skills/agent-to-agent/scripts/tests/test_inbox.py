"""Tests for inbox.py — the agent-to-agent protocol CLI."""

import argparse
import threading
import time

import pytest

import inbox


@pytest.fixture()
def root(tmp_path, monkeypatch):
    mailbox = tmp_path / "mail" / ".agent-to-agent"
    monkeypatch.setenv("AGENT_MAIL_ROOT", str(mailbox))
    return mailbox


# -- names --------------------------------------------------------------------


def test_valid_name_accepts_lowercase():
    assert inbox.valid_name("kimi") == "kimi"
    assert inbox.valid_name("agent-2_x") == "agent-2_x"


@pytest.mark.parametrize("bad", ["CLAUDE", "CLAUDE.md", "Kimi", "", "-x", "a" * 33, "a.b"])
def test_valid_name_rejects(bad):
    with pytest.raises(argparse.ArgumentTypeError):
        inbox.valid_name(bad)


def test_message_name_sorts_numerically():
    name = inbox.message_name("kimi")
    stamp, _, rest = name.partition("-")
    assert len(stamp) == 19 and stamp.isdigit()
    assert rest == "kimi.md"


# -- delivery -----------------------------------------------------------------


def test_deliver_is_atomic_and_clean(root):
    path = inbox.deliver(root, "kimi", "claude", "hello")
    assert path.parent == inbox.inbox_dir(root, "claude")
    assert path.read_text() == "hello\n"
    assert not list(path.parent.glob(".tmp-*"))


def test_pending_skips_dotfiles_and_sorts(root):
    box = inbox.inbox_dir(root, "claude")
    box.mkdir(parents=True)
    (box / "0000000000000000002-a.md").write_text("2")
    (box / "0000000000000000001-b.md").write_text("1")
    (box / ".tmp-0000000000000000003-c.md").write_text("staging")
    names = [p.name for p in inbox.pending(box)]
    assert names == ["0000000000000000001-b.md", "0000000000000000002-a.md"]


def test_rename_noreplace_refuses_existing(tmp_path):
    src = tmp_path / "src"
    dst = tmp_path / "dst"
    src.write_text("new")
    dst.write_text("old")
    assert inbox.rename_noreplace(src, dst) is False
    assert dst.read_text() == "old"


# -- wait ---------------------------------------------------------------------


def test_wait_delivers_one_message_at_a_time(root, capsys):
    inbox.deliver(root, "kimi", "claude", "first")
    inbox.deliver(root, "kimi", "claude", "second")

    assert inbox.wait_for_mail(root, "claude", timeout=5) == inbox.EXIT_OK
    out = capsys.readouterr().out
    assert "first" in out
    assert "second" not in out
    assert len(inbox.pending(inbox.inbox_dir(root, "claude"))) == 1

    assert inbox.wait_for_mail(root, "claude", timeout=5) == inbox.EXIT_OK
    out = capsys.readouterr().out
    assert "second" in out
    assert not inbox.pending(inbox.inbox_dir(root, "claude"))


def test_wait_timeout(root):
    inbox.inbox_dir(root, "claude").mkdir(parents=True)
    assert inbox.wait_for_mail(root, "claude", timeout=0.2) == inbox.EXIT_TIMEOUT


def test_wait_wakes_on_delivery(root, capsys):
    inbox.inbox_dir(root, "claude").mkdir(parents=True)
    threading.Timer(0.15, inbox.deliver, (root, "kimi", "claude", "ping")).start()
    start = time.monotonic()
    assert inbox.wait_for_mail(root, "claude", timeout=5) == inbox.EXIT_OK
    assert time.monotonic() - start < 2
    assert "ping" in capsys.readouterr().out


# -- drain --------------------------------------------------------------------


def test_drain_order_archive_idempotent(root, capsys):
    for body in ("first", "second", "third"):
        inbox.deliver(root, "kimi", "claude", body)

    assert inbox.drain_mail(root, "claude") == inbox.EXIT_OK
    out = capsys.readouterr().out
    assert out.index("first") < out.index("second") < out.index("third")
    assert "drained: 3" in out
    assert not inbox.pending(inbox.inbox_dir(root, "claude"))
    assert len(list(inbox.processed_dir(root, "claude").iterdir())) == 3

    assert inbox.drain_mail(root, "claude") == inbox.EXIT_OK
    assert "drained: 0" in capsys.readouterr().out


# -- CLI ----------------------------------------------------------------------


def test_send_requires_explicit_self(root, capsys):
    assert inbox.main(["send", "kimi", "claude", "-m", "hi"]) == inbox.EXIT_OK
    assert "delivered:" in capsys.readouterr().out


def test_send_refuses_empty_message(root):
    assert inbox.main(["send", "kimi", "claude", "-m", "  "]) == inbox.EXIT_USAGE


def test_resolve_root_env_override(root):
    resolved, via = inbox.resolve_root()
    assert resolved == root
    assert "AGENT_MAIL_ROOT" in via


def test_ensure_gitignore_appends_once(tmp_path):
    repo = tmp_path / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / ".gitignore").write_text("node_modules/")  # no trailing newline

    root = repo / ".agent-to-agent"
    inbox.ensure_gitignore(root)
    inbox.ensure_gitignore(root)

    lines = (repo / ".gitignore").read_text().splitlines()
    assert lines[0] == "node_modules/"
    assert lines.count(inbox.IGNORE_LINE) == 1
