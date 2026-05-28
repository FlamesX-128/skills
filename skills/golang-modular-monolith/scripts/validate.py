#!/usr/bin/env python3
"""Validate that cmd/ and internal/ follow the Golang Modular Monolith convention.

Usage:
    python3 scripts/validate.py [PROJECT_ROOT]

With no argument the current working directory is used. Exits non-zero when
any error is reported; warnings (empty structural slots, unknown but harmless
subdirectories) never fail the run.
"""

from __future__ import annotations

import re
import sys
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import IO, Literal

__all__ = [
    "HTTP_OPS",
    "SQL_OPS",
    "HTTP_ROOT_EXTRA_GO",
    "INTERNAL_RESERVED",
    "Issue",
    "Report",
    "main",
    "split_http",
    "split_sql",
    "validate_cmd",
    "validate_http_op_dir",
    "validate_http_protocol",
    "validate_infrastructure_layer",
    "validate_interface_layer",
    "validate_internal",
    "validate_model_dir",
    "validate_module",
    "validate_postgres_adapter",
    "validate_redis_adapter",
    "validate_service_layer",
    "validate_sql_op_dir",
    "validate_tool_dir",
]

HTTP_OPS: frozenset[str] = frozenset(
    {"get", "post", "put", "patch", "delete", "head", "options", "query"}
)
SQL_OPS: frozenset[str] = frozenset({"select", "insert", "update", "delete", "merge", "truncate"})

# Files allowed at the root of interface/http/ besides register.go.
HTTP_ROOT_EXTRA_GO: frozenset[str] = frozenset({"permissions.go"})

INTERNAL_RESERVED: frozenset[str] = frozenset({"platform", "shared"})

IDENT_RE = re.compile(r"^[a-z][a-z0-9]*(?:_[a-z0-9]+)*$")

Severity = Literal["error", "warning"]

FileCheck = Callable[[Path, str, "Report"], None]


@dataclass(frozen=True, slots=True)
class Issue:
    """A single violation or advisory emitted by the validator."""

    severity: Severity
    path: Path
    message: str


@dataclass
class Report:
    """Accumulator of issues collected during a validation pass.

    Attributes:
        root: Project root used to render relative paths in output.
        issues: Issues in emission order.
    """

    root: Path
    issues: list[Issue] = field(default_factory=list)

    def error(self, path: Path, msg: str) -> None:
        """Record an error that will cause the validator to exit non-zero."""
        self.issues.append(Issue("error", path, msg))

    def warn(self, path: Path, msg: str) -> None:
        """Record a non-failing advisory."""
        self.issues.append(Issue("warning", path, msg))

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity == "warning"]


# ---------------------------------------------------------------------------
# Filesystem and parsing helpers
# ---------------------------------------------------------------------------


def rel(path: Path, root: Path) -> str:
    """Return ``path`` relative to ``root`` or the absolute form when outside."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def visible_children(d: Path) -> list[Path]:
    """Direct children of ``d``, skipping dot-files (.gitkeep, .DS_Store, ...)."""
    return [p for p in sorted(d.iterdir()) if not p.name.startswith(".")]


def list_files(d: Path) -> list[Path]:
    return [p for p in visible_children(d) if p.is_file()]


def list_dirs(d: Path) -> list[Path]:
    return [p for p in visible_children(d) if p.is_dir()]


def is_empty_dir(d: Path) -> bool:
    """Return True when ``d`` is a directory with no visible children."""
    return d.is_dir() and not visible_children(d)


def split_http(name: str, ext: str) -> tuple[str, str] | None:
    """Parse ``<entity>_<method>.<ext>``.

    The HTTP method is the final token. The entity may contain underscores
    (``password_reset_post.go`` → ``password_reset``, ``post``).

    Returns:
        ``(entity, method)`` or ``None`` when the name does not match.
    """
    if not name.endswith(ext):
        return None
    base = name[: -len(ext)]
    parts = base.rsplit("_", 1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


def split_sql(name: str, ext: str) -> tuple[str, str, str] | None:
    """Parse ``<entity>_<sql_op>[_<modifier>].<ext>``.

    The first SQL op token found splits the name. Everything before it is the
    entity (may itself contain underscores), everything after is the optional
    modifier (``employee_select_by_id.sql`` → ``employee``, ``select``,
    ``by_id``).

    Returns:
        ``(entity, op, modifier)`` or ``None`` when no SQL op token appears.
    """
    if not name.endswith(ext):
        return None
    base = name[: -len(ext)]
    tokens = base.split("_")
    for i, tok in enumerate(tokens):
        if tok in SQL_OPS:
            if i == 0:
                return None
            entity = "_".join(tokens[:i])
            modifier = "_".join(tokens[i + 1 :])
            return entity, tok, modifier
    return None


# ---------------------------------------------------------------------------
# File-level validators
# ---------------------------------------------------------------------------


def _validate_sql_file(f: Path, label: str, ext: str, report: Report) -> None:
    """Validate a single ``<entity>_<sql_op>[_<modifier>].<ext>`` file."""
    if not f.name.endswith(ext):
        report.error(f, f"{label}/: unexpected extension (expected {ext})")
        return
    parsed = split_sql(f.name, ext)
    if parsed is None:
        ops = "/".join(sorted(SQL_OPS))
        report.error(
            f,
            f"{label}/: does not match <entity>_<sql_op>[_<modifier>]{ext} (valid ops: {ops})",
        )
        return
    entity, _op, modifier = parsed
    if not IDENT_RE.match(entity):
        report.error(f, f"{label}/: invalid entity prefix '{entity}'")
    if modifier and not IDENT_RE.match(modifier):
        report.error(f, f"{label}/: invalid modifier '{modifier}'")


def _validate_http_file(f: Path, label: str, report: Report) -> None:
    """Validate a single ``<entity>_<method>.go`` file."""
    if not f.name.endswith(".go"):
        report.error(f, f"{label}/: unexpected extension (expected .go)")
        return
    parsed = split_http(f.name, ".go")
    if parsed is None:
        report.error(f, f"{label}/: does not match <entity>_<method>.go")
        return
    entity, op = parsed
    if not IDENT_RE.match(entity):
        report.error(f, f"{label}/: invalid entity prefix '{entity}'")
    if op not in HTTP_OPS:
        ops = "/".join(sorted(HTTP_OPS))
        report.error(f, f"{label}/: '{op}' is not a valid HTTP method ({ops})")


def _validate_tool_file(f: Path, label: str, report: Report) -> None:
    """Validate a single helper file under a ``tool/`` slot."""
    if not f.name.endswith(".go"):
        report.error(f, f"{label}/tool/: unexpected extension (expected .go)")
        return
    base = f.name[:-3]
    if not IDENT_RE.match(base):
        report.error(f, f"{label}/tool/: invalid name '{base}' (snake_case)")


def _validate_model_file(f: Path, _label: str, report: Report) -> None:
    """Validate a single entity file under ``model/``."""
    if not f.name.endswith(".go"):
        report.error(f, "model/: unexpected extension (expected .go)")
        return
    base = f.name[:-3]
    if not IDENT_RE.match(base):
        report.error(f, f"model/: invalid name '{base}' (snake_case)")


def _validate_freeform_op_file(
    f: Path,
    label: str,
    report: Report,
) -> None:
    """Validate ``<entity>_<op>.go`` where ``op`` is free-form snake_case.

    Used by layers whose vocabulary is open (service, redis) - only structural
    requirements apply: ``.go`` extension and the entity-prefix shape.
    """
    if not f.name.endswith(".go"):
        report.error(f, f"{label}/: unexpected extension (expected .go)")
        return
    base = f.name[:-3]
    if "_" not in base:
        report.error(f, f"{label}/: missing entity prefix <entity>_<op>.go")
        return
    entity, _, op = base.partition("_")
    if not IDENT_RE.match(entity):
        report.error(f, f"{label}/: invalid entity prefix '{entity}'")
    if not IDENT_RE.match(op):
        report.error(f, f"{label}/: invalid operation '{op}'")


# ---------------------------------------------------------------------------
# Generic directory validators (composition: pluggable file_check)
# ---------------------------------------------------------------------------


def _validate_leaf_dir(
    d: Path,
    label: str,
    file_check: FileCheck,
    report: Report,
    *,
    empty_label: str | None = None,
) -> None:
    """Validate a leaf directory: no subdirs, each file checked individually.

    Args:
        d: Directory to inspect.
        label: Human-readable label for messages (e.g. ``"interface/http"``).
        file_check: Callable invoked per file. Receives ``(path, label, report)``.
        report: Accumulator to push errors/warnings into.
        empty_label: Optional label to use for the "empty slot" warning. When
            omitted, ``label`` is used. Useful when the label of the empty
            warning differs from the per-file message label
            (e.g. ``service/tool/`` vs ``service``).
    """
    if is_empty_dir(d):
        report.warn(d, f"{empty_label or label}/: empty slot")
        return
    for sub in list_dirs(d):
        report.error(sub, f"{label}/: unexpected subdirectory '{sub.name}'")
    for f in list_files(d):
        file_check(f, label, report)


def validate_http_op_dir(d: Path, label: str, report: Report) -> None:
    """Validate a directory whose files follow the HTTP-method vocabulary."""
    if not d.is_dir():
        return
    _validate_leaf_dir(d, label, _validate_http_file, report)


def validate_sql_op_dir(d: Path, label: str, ext: str, report: Report) -> None:
    """Validate a directory whose files follow the SQL-operation vocabulary."""
    if not d.is_dir():
        return

    def _check(f: Path, lbl: str, rep: Report) -> None:
        _validate_sql_file(f, lbl, ext, rep)

    _validate_leaf_dir(d, label, _check, report)


def validate_tool_dir(d: Path, label: str, report: Report) -> None:
    """Validate a ``tool/`` directory (helpers without entity prefix)."""
    _validate_leaf_dir(
        d,
        label,
        _validate_tool_file,
        report,
        empty_label=f"{label}/tool",
    )


def validate_model_dir(d: Path, report: Report) -> None:
    """Validate ``model/``: one ``<entity>.go`` per entity, no subdirs."""
    _validate_leaf_dir(d, "model", _validate_model_file, report)


def reject_nested_tool(d: Path, label: str, report: Report) -> None:
    """Emit an error if ``d/tool/`` exists.

    The ``tool/`` slot is only valid at the root of a major layer; helpers in
    sub-directories must be promoted to that parent ``tool/`` instead.
    """
    tool = d / "tool"
    if tool.exists():
        report.error(
            tool,
            f"{label}/: must not contain tool/ (helpers go in the parent tool/)",
        )


# ---------------------------------------------------------------------------
# Layer and adapter validators
# ---------------------------------------------------------------------------


def _validate_service_root_files(d: Path, report: Report) -> None:
    """Validate files directly under ``service/`` (free-form action vocabulary)."""
    for f in list_files(d):
        _validate_freeform_op_file(f, "service", report)


def validate_service_layer(d: Path, report: Report) -> None:
    """Validate the full ``service/`` layer: root files + mapper/ + tool/."""
    _validate_service_root_files(d, report)
    allowed = {"mapper", "tool"}
    for sub in list_dirs(d):
        if sub.name not in allowed:
            report.warn(sub, f"service/: unexpected subdirectory '{sub.name}'")

    mapper = d / "mapper"
    if mapper.is_dir():
        for f in list_files(mapper):
            report.error(f, "service/mapper/: must not contain direct files")
        for sub in list_dirs(mapper):
            if sub.name not in {"http", "postgres"}:
                report.warn(
                    sub,
                    f"service/mapper/: unexpected subdirectory '{sub.name}'",
                )

        mh = mapper / "http"
        if mh.is_dir():
            reject_nested_tool(mh, "service/mapper/http", report)
            validate_http_op_dir(mh, "service/mapper/http", report)

        mp = mapper / "postgres"
        if mp.is_dir():
            reject_nested_tool(mp, "service/mapper/postgres", report)
            validate_sql_op_dir(mp, "service/mapper/postgres", ".go", report)

    tool = d / "tool"
    if tool.is_dir():
        validate_tool_dir(tool, "service", report)


def validate_postgres_adapter(d: Path, report: Report) -> None:
    """Validate ``infrastructure/postgres/``: root .go files + dto/sql/tool slots."""
    for f in list_files(d):
        _validate_sql_file(f, "infrastructure/postgres", ".go", report)

    allowed = {"dto", "sql", "tool"}
    for sub in list_dirs(d):
        if sub.name not in allowed:
            report.warn(
                sub,
                f"infrastructure/postgres/: unexpected subdirectory '{sub.name}'",
            )

    dto = d / "dto"
    if dto.is_dir():
        reject_nested_tool(dto, "infrastructure/postgres/dto", report)
        validate_sql_op_dir(dto, "infrastructure/postgres/dto", ".go", report)

    sqld = d / "sql"
    if sqld.is_dir():
        reject_nested_tool(sqld, "infrastructure/postgres/sql", report)
        validate_sql_op_dir(sqld, "infrastructure/postgres/sql", ".sql", report)

    tool = d / "tool"
    if tool.is_dir():
        validate_tool_dir(tool, "infrastructure/postgres", report)


def validate_redis_adapter(d: Path, report: Report) -> None:
    """Validate ``infrastructure/redis/``: free-form op vocabulary + dto/tool slots."""
    for f in list_files(d):
        _validate_freeform_op_file(f, "infrastructure/redis", report)

    for sub in list_dirs(d):
        if sub.name not in {"dto", "tool"}:
            report.warn(
                sub,
                f"infrastructure/redis/: unexpected subdirectory '{sub.name}'",
            )

    dto = d / "dto"
    if dto.is_dir():
        reject_nested_tool(dto, "infrastructure/redis/dto", report)
        if is_empty_dir(dto):
            report.warn(dto, "infrastructure/redis/dto/: empty slot")

    tool = d / "tool"
    if tool.is_dir():
        validate_tool_dir(tool, "infrastructure/redis", report)


def validate_infrastructure_layer(d: Path, report: Report) -> None:
    """Validate ``infrastructure/``: only known adapters as direct children."""
    for f in list_files(d):
        report.error(f, "infrastructure/: must not contain direct files")
    if is_empty_dir(d):
        report.warn(d, "infrastructure/: empty slot")
        return
    for adapter in list_dirs(d):
        if adapter.name == "postgres":
            validate_postgres_adapter(adapter, report)
        elif adapter.name == "redis":
            validate_redis_adapter(adapter, report)
        else:
            report.warn(
                adapter,
                f"infrastructure/: unknown adapter '{adapter.name}'",
            )


def _validate_http_root_files(d: Path, report: Report) -> None:
    """Validate the files directly under ``interface/http/``."""
    allowed_root_go = {"register.go"} | set(HTTP_ROOT_EXTRA_GO)
    has_register = False
    for f in list_files(d):
        if f.name == "register.go":
            has_register = True
            continue
        if f.name in allowed_root_go:
            continue
        report.error(
            f,
            f"interface/http/: unexpected file '{f.name}' "
            f"(allowed at root: {', '.join(sorted(allowed_root_go))})",
        )
    if not has_register:
        report.error(d / "register.go", "interface/http/: missing register.go")


def validate_http_protocol(d: Path, report: Report) -> None:
    """Validate ``interface/http/``: register.go + dto/handler/middleware/tool slots."""
    _validate_http_root_files(d, report)

    for sub in list_dirs(d):
        if sub.name not in {"dto", "handler", "middleware", "tool"}:
            report.warn(
                sub,
                f"interface/http/: unexpected subdirectory '{sub.name}'",
            )

    dto = d / "dto"
    if dto.is_dir():
        reject_nested_tool(dto, "interface/http/dto", report)
        validate_http_op_dir(dto, "interface/http/dto", report)

    handler = d / "handler"
    if handler.is_dir():
        reject_nested_tool(handler, "interface/http/handler", report)
        validate_http_op_dir(handler, "interface/http/handler", report)

    middleware = d / "middleware"
    if middleware.is_dir():
        reject_nested_tool(middleware, "interface/http/middleware", report)
        if is_empty_dir(middleware):
            report.warn(middleware, "interface/http/middleware/: empty slot")

    tool = d / "tool"
    if tool.is_dir():
        validate_tool_dir(tool, "interface/http", report)


def validate_interface_layer(d: Path, report: Report) -> None:
    """Validate ``interface/``: only known protocols as direct children."""
    for f in list_files(d):
        report.error(f, "interface/: must not contain direct files")
    if is_empty_dir(d):
        report.warn(d, "interface/: empty slot")
        return
    for proto in list_dirs(d):
        if proto.name == "http":
            validate_http_protocol(proto, report)
        else:
            report.warn(proto, f"interface/: unknown protocol '{proto.name}'")


# ---------------------------------------------------------------------------
# Root validators (module, internal/, cmd/)
# ---------------------------------------------------------------------------


_LAYER_VALIDATORS: dict[str, Callable[[Path, Report], None]] = {
    "model": validate_model_dir,
    "service": validate_service_layer,
    "infrastructure": validate_infrastructure_layer,
    "interface": validate_interface_layer,
}


def validate_module(module: Path, report: Report) -> None:
    """Validate a single domain module inside ``internal/``."""
    name = module.name
    if not IDENT_RE.match(name):
        report.error(module, f"internal/: invalid module name '{name}'")

    for f in list_files(module):
        report.error(
            f,
            f"internal/{name}/: must not contain direct files",
        )

    for sub in list_dirs(module):
        if sub.name not in _LAYER_VALIDATORS:
            report.warn(
                sub,
                f"internal/{name}/: unexpected directory '{sub.name}'",
            )

    for layer, validator in _LAYER_VALIDATORS.items():
        d = module / layer
        if d.is_dir():
            validator(d, report)


def validate_internal(internal_dir: Path, report: Report) -> None:
    """Validate ``internal/``: modules + reserved (platform, shared) skipped."""
    if not internal_dir.is_dir():
        report.error(internal_dir, "missing internal/ directory")
        return
    for f in list_files(internal_dir):
        report.error(f, "internal/: must not contain direct files")
    for entry in list_dirs(internal_dir):
        if entry.name in INTERNAL_RESERVED:
            continue
        validate_module(entry, report)


def _validate_cmd_entry(entry: Path, report: Report) -> None:
    """Validate a single ``cmd/<name>/`` entry point."""
    if not IDENT_RE.match(entry.name):
        report.error(entry, f"cmd/: invalid name '{entry.name}'")

    main_go = entry / "main.go"
    if not main_go.exists():
        report.error(main_go, f"cmd/{entry.name}/: missing main.go")

    bootstrap_dir = entry / "bootstrap"
    if not bootstrap_dir.is_dir():
        return

    bootstrap_go = bootstrap_dir / "bootstrap.go"
    if not bootstrap_go.exists():
        report.error(
            bootstrap_go,
            f"cmd/{entry.name}/bootstrap/: missing bootstrap.go",
        )
    for f in list_files(bootstrap_dir):
        if f.name != "bootstrap.go":
            report.warn(
                f,
                f"cmd/{entry.name}/bootstrap/: unexpected file '{f.name}'",
            )


def validate_cmd(cmd_dir: Path, report: Report) -> None:
    """Validate ``cmd/``: each entry point has ``main.go`` and optional bootstrap/."""
    if not cmd_dir.is_dir():
        report.error(cmd_dir, "missing cmd/ directory")
        return
    for f in list_files(cmd_dir):
        report.error(f, "cmd/: must not contain direct files")
    if is_empty_dir(cmd_dir):
        report.warn(cmd_dir, "cmd/: no entry points")
        return
    for entry in list_dirs(cmd_dir):
        _validate_cmd_entry(entry, report)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def _print_section(title: str, issues: list[Issue], root: Path, out: IO[str]) -> None:
    """Print a labelled block of issues to ``out``."""
    print(f"{title} ({len(issues)}):", file=out)
    for issue in issues:
        print(f"  {rel(issue.path, root)}: {issue.message}", file=out)


def main(argv: list[str]) -> int:
    """CLI entry point.

    Returns:
        0 when there are no errors, 1 when at least one error was reported,
        2 when the supplied project root is not a directory.
    """
    root = Path(argv[1]).resolve() if len(argv) > 1 else Path.cwd().resolve()
    if not root.is_dir():
        print(f"error: {root} is not a directory", file=sys.stderr)
        return 2

    report = Report(root=root)
    validate_cmd(root / "cmd", report)
    validate_internal(root / "internal", report)

    out = sys.stderr
    if report.errors:
        _print_section("ERRORS", report.errors, root, out)
    if report.warnings:
        if report.errors:
            print("", file=out)
        _print_section("WARNINGS", report.warnings, root, out)
    if not report.issues:
        print("no violations", file=out)

    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
