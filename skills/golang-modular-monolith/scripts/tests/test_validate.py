"""Tests for validate.py.

Strategy: each test builds a minimal structure under ``tmp_path`` and inspects
what the validator emits. Filesystem isolation keeps the tests deterministic
and parallel-safe, and lets us cover each layer's rules independently.

Naming follows ``test_<unit>_<scenario>_<expected>`` so failures read as
behavioural assertions, not implementation trivia.
"""

from __future__ import annotations

from pathlib import Path

import pytest

import validate
from validate import Report


def touch(p: Path) -> None:
    """Create an empty file, making parent directories on the way."""
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def valid_module(tmp_path: Path) -> Path:
    """Build a minimal but conformant ``employee`` module under ``internal/``."""
    m = tmp_path / "internal" / "employee"
    touch(m / "model" / "employee.go")
    touch(m / "service" / "employee_create.go")
    touch(m / "service" / "employee_get.go")
    touch(m / "service" / "mapper" / "http" / "employee_get.go")
    touch(m / "service" / "mapper" / "postgres" / "employee_select.go")
    touch(m / "infrastructure" / "postgres" / "employee_select.go")
    touch(m / "infrastructure" / "postgres" / "dto" / "employee_select.go")
    touch(m / "interface" / "http" / "register.go")
    touch(m / "interface" / "http" / "handler" / "employee_get.go")
    touch(m / "interface" / "http" / "dto" / "employee_get.go")
    return m


@pytest.fixture
def valid_cmd(tmp_path: Path) -> Path:
    """Build a ``cmd/server`` entry point with main.go and bootstrap.go."""
    touch(tmp_path / "cmd" / "server" / "main.go")
    touch(tmp_path / "cmd" / "server" / "bootstrap" / "bootstrap.go")
    return tmp_path / "cmd"


# ---------------------------------------------------------------------------
# Full project: golden path + CLI exit codes
# ---------------------------------------------------------------------------


def test_main_returns_zero_on_valid_project(
    tmp_path: Path, valid_cmd: Path, valid_module: Path
) -> None:
    assert validate.main(["validate.py", str(tmp_path)]) == 0


def test_main_returns_two_on_missing_root() -> None:
    assert validate.main(["validate.py", "/no/such/path/anywhere"]) == 2


def test_main_returns_one_when_any_error_is_reported(tmp_path: Path, valid_cmd: Path) -> None:
    """Errors anywhere (here: empty internal/) must surface as exit 1."""
    (tmp_path / "internal").mkdir()
    touch(tmp_path / "internal" / "stray.go")
    assert validate.main(["validate.py", str(tmp_path)]) == 1


# ---------------------------------------------------------------------------
# cmd/
# ---------------------------------------------------------------------------


def test_cmd_without_main_go_emits_error(tmp_path: Path) -> None:
    (tmp_path / "cmd" / "server").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert any("main.go" in i.message for i in report.errors)


def test_cmd_bootstrap_dir_without_bootstrap_go_is_error(tmp_path: Path) -> None:
    touch(tmp_path / "cmd" / "server" / "main.go")
    (tmp_path / "cmd" / "server" / "bootstrap").mkdir()
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert any("bootstrap.go" in i.message for i in report.errors)


def test_cmd_with_extra_bootstrap_file_emits_warning_not_error(
    tmp_path: Path,
) -> None:
    touch(tmp_path / "cmd" / "server" / "main.go")
    touch(tmp_path / "cmd" / "server" / "bootstrap" / "bootstrap.go")
    touch(tmp_path / "cmd" / "server" / "bootstrap" / "extras.go")
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert report.errors == []
    assert any("extras.go" in i.message for i in report.warnings)


def test_cmd_missing_directory_emits_error(tmp_path: Path) -> None:
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert any("missing cmd/" in i.message for i in report.errors)


def test_cmd_with_direct_file_is_error(tmp_path: Path) -> None:
    (tmp_path / "cmd").mkdir()
    touch(tmp_path / "cmd" / "stray.go")
    touch(tmp_path / "cmd" / "server" / "main.go")
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert any("direct files" in i.message for i in report.errors)


def test_cmd_entry_with_invalid_name_is_error(tmp_path: Path) -> None:
    touch(tmp_path / "cmd" / "BadName" / "main.go")
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert any("BadName" in i.message for i in report.errors)


def test_cmd_allows_freeform_extra_files_alongside_main(tmp_path: Path) -> None:
    """cmd/<name>/ may carry arbitrary helper files; only main.go is required."""
    touch(tmp_path / "cmd" / "setup" / "main.go")
    touch(tmp_path / "cmd" / "setup" / "sql" / "init.sql")
    report = Report(root=tmp_path)
    validate.validate_cmd(tmp_path / "cmd", report)
    assert report.errors == []


# ---------------------------------------------------------------------------
# HTTP vocabulary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    [
        "employee_get.go",
        "employee_post.go",
        "employee_query.go",
        "password_reset_post.go",
    ],
)
def test_http_handler_accepts_valid_method_suffix(tmp_path: Path, filename: str) -> None:
    handler = tmp_path / "handler"
    touch(handler / filename)
    report = Report(root=tmp_path)
    validate.validate_http_op_dir(handler, "test/handler", report)
    assert report.errors == []


@pytest.mark.parametrize(
    "filename,reason",
    [
        ("employee_login.go", "login is not an HTTP method"),
        ("post.go", "missing entity prefix"),
        ("employee.go", "missing method suffix"),
        ("employee_get.txt", "wrong extension"),
    ],
)
def test_http_handler_rejects_invalid_filename(tmp_path: Path, filename: str, reason: str) -> None:
    handler = tmp_path / "handler"
    touch(handler / filename)
    report = Report(root=tmp_path)
    validate.validate_http_op_dir(handler, "test/handler", report)
    assert report.errors, f"expected error because {reason}"


# ---------------------------------------------------------------------------
# SQL vocabulary
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    [
        "employee_select.go",
        "employee_select_by_id.go",
        "user_role_insert.go",
        "employee_update_archived.go",
        "session_delete.go",
    ],
)
def test_postgres_accepts_valid_sql_filename(tmp_path: Path, filename: str) -> None:
    d = tmp_path / "infrastructure" / "postgres"
    touch(d / filename)
    report = Report(root=tmp_path)
    validate.validate_postgres_adapter(d, report)
    assert report.errors == []


@pytest.mark.parametrize(
    "filename,reason",
    [
        ("employee_archive.go", "archive is not a SQL op"),
        ("select.go", "missing entity prefix"),
        ("employee.go", "missing SQL op"),
    ],
)
def test_postgres_rejects_invalid_sql_filename(tmp_path: Path, filename: str, reason: str) -> None:
    d = tmp_path / "infrastructure" / "postgres"
    touch(d / filename)
    report = Report(root=tmp_path)
    validate.validate_postgres_adapter(d, report)
    assert report.errors, f"expected error because {reason}"


def test_postgres_sql_dir_validates_dot_sql_extension(tmp_path: Path) -> None:
    sqld = tmp_path / "infrastructure" / "postgres" / "sql"
    touch(sqld / "employee_select_by_id.sql")
    report = Report(root=tmp_path)
    validate.validate_sql_op_dir(sqld, "infrastructure/postgres/sql", ".sql", report)
    assert report.errors == []


def test_postgres_sql_dir_rejects_go_file_in_sql_slot(tmp_path: Path) -> None:
    sqld = tmp_path / "infrastructure" / "postgres" / "sql"
    touch(sqld / "employee_select.go")  # wrong ext for sql/
    report = Report(root=tmp_path)
    validate.validate_sql_op_dir(sqld, "infrastructure/postgres/sql", ".sql", report)
    assert any("unexpected extension" in i.message for i in report.errors)


# ---------------------------------------------------------------------------
# Redis adapter (free-form op vocabulary)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    ["session_set.go", "session_get.go", "user_role_invalidate.go"],
)
def test_redis_accepts_valid_freeform_op(tmp_path: Path, filename: str) -> None:
    d = tmp_path / "infrastructure" / "redis"
    touch(d / filename)
    report = Report(root=tmp_path)
    validate.validate_redis_adapter(d, report)
    assert report.errors == []


@pytest.mark.parametrize(
    "filename,reason",
    [
        ("session.go", "missing entity prefix (no underscore)"),
        ("set.txt", "wrong extension"),
        ("Session_Get.go", "not snake_case"),
    ],
)
def test_redis_rejects_invalid_filename(tmp_path: Path, filename: str, reason: str) -> None:
    d = tmp_path / "infrastructure" / "redis"
    touch(d / filename)
    report = Report(root=tmp_path)
    validate.validate_redis_adapter(d, report)
    assert report.errors, f"expected error because {reason}"


def test_redis_empty_dto_slot_emits_warning(tmp_path: Path) -> None:
    d = tmp_path / "infrastructure" / "redis"
    (d / "dto").mkdir(parents=True)
    touch(d / "session_set.go")
    report = Report(root=tmp_path)
    validate.validate_redis_adapter(d, report)
    assert any("empty slot" in i.message for i in report.warnings)


def test_redis_rejects_tool_inside_dto(tmp_path: Path) -> None:
    d = tmp_path / "infrastructure" / "redis"
    (d / "dto" / "tool").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_redis_adapter(d, report)
    assert any("tool/" in i.message for i in report.errors)


def test_infrastructure_with_unknown_adapter_warns(tmp_path: Path) -> None:
    d = tmp_path / "infrastructure"
    (d / "mongo").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_infrastructure_layer(d, report)
    assert any("unknown adapter" in i.message for i in report.warnings)


# ---------------------------------------------------------------------------
# Service layer (free-form action vocabulary + mapper subdirs)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "filename",
    [
        "employee_create.go",
        "employee_archive.go",
        "user_login.go",
        "user_reset_password.go",
    ],
)
def test_service_accepts_freeform_action(tmp_path: Path, filename: str) -> None:
    s = tmp_path / "service"
    touch(s / filename)
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert report.errors == []


def test_service_rejects_file_without_entity_prefix(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "create.go")
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert any("missing entity prefix" in i.message for i in report.errors)


def test_service_mapper_postgres_enforces_sql_vocab(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "mapper" / "postgres" / "employee_login.go")  # not a SQL op
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert report.errors


def test_service_mapper_http_enforces_http_vocab(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "mapper" / "http" / "employee_login.go")  # login is not HTTP method
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert report.errors


def test_service_mapper_direct_file_is_error(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "mapper" / "stray.go")
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert any("direct files" in i.message for i in report.errors)


def test_service_unexpected_subdirectory_warns(tmp_path: Path) -> None:
    s = tmp_path / "service"
    (s / "domain").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert any("unexpected subdirectory" in i.message for i in report.warnings)


# ---------------------------------------------------------------------------
# tool/ slot rules
# ---------------------------------------------------------------------------


def test_tool_inside_http_handler_is_error(tmp_path: Path) -> None:
    iface = tmp_path / "interface" / "http"
    touch(iface / "register.go")
    touch(iface / "handler" / "employee_get.go")
    (iface / "handler" / "tool").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_http_protocol(iface, report)
    assert any("tool/" in i.message for i in report.errors)


def test_tool_inside_postgres_dto_is_error(tmp_path: Path) -> None:
    d = tmp_path / "infrastructure" / "postgres"
    touch(d / "dto" / "employee_select.go")
    (d / "dto" / "tool").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_postgres_adapter(d, report)
    assert any("tool/" in i.message for i in report.errors)


def test_service_tool_accepts_unprefixed_helper(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "tool" / "parse.go")
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert report.errors == []


def test_service_tool_rejects_invalid_filename(tmp_path: Path) -> None:
    s = tmp_path / "service"
    touch(s / "tool" / "BadName.go")
    report = Report(root=tmp_path)
    validate.validate_service_layer(s, report)
    assert any("snake_case" in i.message for i in report.errors)


# ---------------------------------------------------------------------------
# interface/http root file rules
# ---------------------------------------------------------------------------


def test_http_root_allows_register_go(tmp_path: Path) -> None:
    iface = tmp_path / "interface" / "http"
    touch(iface / "register.go")
    report = Report(root=tmp_path)
    validate.validate_http_protocol(iface, report)
    assert report.errors == []


def test_http_root_allows_permissions_go(tmp_path: Path) -> None:
    iface = tmp_path / "interface" / "http"
    touch(iface / "register.go")
    touch(iface / "permissions.go")
    report = Report(root=tmp_path)
    validate.validate_http_protocol(iface, report)
    assert report.errors == []


def test_http_root_rejects_arbitrary_go_file(tmp_path: Path) -> None:
    iface = tmp_path / "interface" / "http"
    touch(iface / "register.go")
    touch(iface / "routes.go")
    report = Report(root=tmp_path)
    validate.validate_http_protocol(iface, report)
    assert any("routes.go" in i.message for i in report.errors)


def test_http_root_missing_register_is_error(tmp_path: Path) -> None:
    iface = tmp_path / "interface" / "http"
    iface.mkdir(parents=True)
    touch(iface / "handler" / "employee_get.go")
    report = Report(root=tmp_path)
    validate.validate_http_protocol(iface, report)
    assert any("register.go" in i.message for i in report.errors)


def test_model_filename_is_entity_without_prefix(tmp_path: Path) -> None:
    m = tmp_path / "model"
    touch(m / "employee.go")
    touch(m / "user_role.go")
    report = Report(root=tmp_path)
    validate.validate_model_dir(m, report)
    assert report.errors == []


# ---------------------------------------------------------------------------
# Empty slots → warnings, not errors
# ---------------------------------------------------------------------------


def test_empty_sql_slot_emits_warning_not_error(tmp_path: Path) -> None:
    d = tmp_path / "infrastructure" / "postgres" / "sql"
    d.mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_sql_op_dir(d, "infrastructure/postgres/sql", ".sql", report)
    assert report.errors == []
    assert any(i.severity == "warning" for i in report.warnings)


def test_empty_tool_slot_emits_warning_not_error(tmp_path: Path) -> None:
    d = tmp_path / "service" / "tool"
    d.mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_tool_dir(d, "service", report)
    assert report.errors == []
    assert any("empty slot" in i.message for i in report.warnings)


def test_dotfiles_do_not_count_as_dir_content(tmp_path: Path) -> None:
    d = tmp_path / "service" / "tool"
    d.mkdir(parents=True)
    (d / ".gitkeep").touch()
    report = Report(root=tmp_path)
    validate.validate_tool_dir(d, "service", report)
    assert any("empty slot" in i.message for i in report.warnings)


# ---------------------------------------------------------------------------
# internal/ reserved names and module shape
# ---------------------------------------------------------------------------


def test_internal_platform_and_shared_are_skipped(tmp_path: Path) -> None:
    """platform/ and shared/ are free-form; module rules do not apply."""
    touch(tmp_path / "internal" / "shared" / "model" / "auditable.go")
    touch(tmp_path / "internal" / "platform" / "oauth" / "client.go")
    report = Report(root=tmp_path)
    validate.validate_internal(tmp_path / "internal", report)
    assert report.errors == []


def test_internal_with_direct_file_is_error(tmp_path: Path) -> None:
    touch(tmp_path / "internal" / "rogue.go")
    report = Report(root=tmp_path)
    validate.validate_internal(tmp_path / "internal", report)
    assert any("direct files" in i.message for i in report.errors)


def test_internal_missing_directory_is_error(tmp_path: Path) -> None:
    report = Report(root=tmp_path)
    validate.validate_internal(tmp_path / "internal", report)
    assert any("missing internal/" in i.message for i in report.errors)


def test_module_with_direct_file_is_error(tmp_path: Path) -> None:
    m = tmp_path / "internal" / "employee"
    touch(m / "stray.go")
    report = Report(root=tmp_path)
    validate.validate_module(m, report)
    assert any("direct files" in i.message for i in report.errors)


def test_module_with_invalid_name_is_error(tmp_path: Path) -> None:
    m = tmp_path / "internal" / "BadModule"
    m.mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_module(m, report)
    assert any("BadModule" in i.message for i in report.errors)


def test_module_unknown_layer_warns(tmp_path: Path) -> None:
    m = tmp_path / "internal" / "employee"
    (m / "domain").mkdir(parents=True)
    report = Report(root=tmp_path)
    validate.validate_module(m, report)
    assert any("unexpected directory" in i.message for i in report.warnings)


# ---------------------------------------------------------------------------
# Helper-level unit tests (parsing primitives)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "name,expected",
    [
        ("employee_get.go", ("employee", "get")),
        ("password_reset_post.go", ("password_reset", "post")),
        ("post.go", None),
        ("employee.txt", None),
    ],
)
def test_split_http_parses_method_at_end(name: str, expected: tuple[str, str] | None) -> None:
    assert validate.split_http(name, ".go") == expected


@pytest.mark.parametrize(
    "name,expected",
    [
        ("employee_select.go", ("employee", "select", "")),
        ("employee_select_by_id.go", ("employee", "select", "by_id")),
        ("user_role_insert.go", ("user_role", "insert", "")),
        ("employee_update_archived.go", ("employee", "update", "archived")),
        ("select.go", None),
        ("employee_archive.go", None),
    ],
)
def test_split_sql_finds_first_op_token(name: str, expected: tuple[str, str, str] | None) -> None:
    assert validate.split_sql(name, ".go") == expected
