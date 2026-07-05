# Validator development

Bundled scripts directory = self-contained `uv` project.

## Setup

```bash
cd ${SKILL_DIR}/scripts
uv sync                       # install pytest, ruff, mypy into .venv
uv run pytest -q              # validator's own tests (must stay green)
uv run ruff check .           # lint
uv run mypy validate.py       # strict type check
```

## Extending

Add test in `tests/test_validate.py` covering accept and reject cases before changing `validate.py`. Existing tests = contract — keep green.
