# Python reference

Core rules apply; this is the Python recipe layer, anchored to PEP 8. Tooling default: **Ruff** (formatter + linter; subsumes black + isort). Examples use a generic `book` domain.

## Contents

- Module layout — newspaper order for a `.py` file
- Imports — PEP 8 groups, `__future__`, `TYPE_CHECKING`
- Blank lines — the PEP 8 numbers (2 / 1 / sparingly) and why
- Dataclass & model fields — role order + the defaults-last constraint
- Statements — guard clauses, decorators
- Verify

## Module layout

Top→bottom, abstraction decreasing (Newspaper Metaphor). Blank line between each band; two blanks before top-level `def`/`class`.

```
1. module docstring
2. from __future__ import annotations
3. imports (stdlib / third-party / local)
4. module constants (UPPER_CASE)
5. public classes & functions
6. private helpers (_leading_underscore)
```

Public above private, caller above callee — a reader meets the API before the machinery.

## Imports

PEP 8 groups, blank between, none within: stdlib → third-party → local. Let Ruff/isort own the order; never reorder by hand.

```python
from __future__ import annotations

import json
from datetime import datetime

import httpx
from pydantic import BaseModel

from app.books import repository
```

`from __future__ import annotations` sits alone at the very top — it changes how the whole file is parsed, so it earns its own line before anything else.

### Type-only imports → `TYPE_CHECKING`

Python's equivalent of a type-only import. Symbols used **only** in annotations go in an `if TYPE_CHECKING:` block at the end of the import section: they never run at import time, so they carry no runtime weight and can break import cycles.

```python
from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.books.models import Book
```

Keeping them apart tells the reader "these cost nothing at runtime" — same signal as a separated `import type` group in TypeScript.

### Tooling

| Want                        | Tool / config                                                         |
| --------------------------- | --------------------------------------------------------------------- |
| Group + order imports       | `ruff check --select I --fix` (isort built in), or standalone `isort` |
| Blank line between sections | isort `force_sort_within_sections = false` (keeps a blank per group)  |
| First-party detection       | `known-first-party = ["app"]` under `[tool.ruff.lint.isort]`          |
| Horizontal formatting       | `ruff format` (black-compatible)                                      |

## Blank lines

PEP 8 is specific here, and Ruff/pycodestyle enforce it — don't guess:

| Situation                                 | Blanks | Rule |
| ----------------------------------------- | ------ | ---- |
| Between top-level `def` / `class`         | 2      | E302 |
| Between methods inside a class            | 1      | E301 |
| Too many consecutive blanks               | ≤2     | E303 |
| After the last top-level def (before EOF) | ≤2     | E305 |

Inside a function, use blanks **sparingly** to separate logical steps (validate → compute → respond). Two blank lines inside one function is the signal to extract, not to keep spacing (core rule).

```python
def price_after_discount(book: Book, rate: float) -> float:
    if rate < 0 or rate > 1:
        raise ValueError("rate must be in [0, 1]")

    discount = book.price * rate

    return book.price - discount
```

Blank before the terminal `return`; no blank between the guard and the `raise` it guards.

## Dataclass & model fields

Role order (core table), blank per group. Same for `@dataclass`, Pydantic `BaseModel`, `TypedDict`, `NamedTuple`.

```python
@dataclass
class Book:
    id: int

    author_id: int
    category_id: int

    title: str
    price: float

    active: bool

    published_at: datetime
    created_at: datetime
```

**Language constraint that can override role order:** in a plain `@dataclass`, fields _without_ defaults must precede fields _with_ defaults, or Python raises `TypeError`. When role order and this rule collide, the language wins (same as "formatter and rule disagree → trust the formatter"). Escape hatches that let role order stand: `@dataclass(kw_only=True)`, or use Pydantic, which has no positional constraint.

```python
@dataclass(kw_only=True)  # role order survives; all fields keyword-only
class Book:
    id: int

    title: str
    price: float = 0.0

    active: bool = True
```

## Statements

**A guard clause is its own paragraph.** The condition and its `return`/`raise` are one dense unit (no blank between them), but the guard is separated from surrounding code of a different role: blank _after_ it before the next step, and blank _before_ it when it follows other work. A guard is a complete thought — "if this, bail" — and the compute after it is the next thought; fusing them makes the reader hunt for where the check ends and the real work begins.

```python
# Cramped: guards fused to the compute around them.
if not name.endswith(ext):
    return None
base = name[: -len(ext)]
parts = base.rsplit("_", 1)
if len(parts) != 2:
    return None

return parts[0], parts[1]
```

```python
# Paragraphed: guard / compute / guard / return, each its own concept.
if not name.endswith(ext):
    return None

base = name[: -len(ext)]
parts = base.rsplit("_", 1)

if len(parts) != 2:
    return None

return parts[0], parts[1]
```

Consecutive guards are separate paragraphs — blank between them. Each checks a different condition and does different work, so each is its own thought. Keep them dense **only** in the narrow case of a parallel wall of identical one-line checks with no bodies (`if a is None: return` / `if b is None: return` in a row); the moment a branch has a body or a distinct action, it earns its blank.

**`continue` and `break` terminate a branch too.** The guard rule applies inside loops: an `if` block ending in `continue`/`break` is a paragraph — blank after it before the next step. And a setup block (accumulators, locals) is separated from the loop that consumes it: setup is one concept, the loop is another.

```python
# Paragraphed: setup / loop; inside the loop, flush-branch / parse.
stanzas: list[dict[str, str]] = []
current: dict[str, str] = {}

for line in output.splitlines():
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
```

The blank after `continue` is correct — the flush-on-blank-line branch is a complete thought, and parsing a real line is the next. No blank between `for` and the first `if`: that statement uses `line` immediately (declaration beside first use).

**Block statements are paragraphs.** A `for`, `while`, `if`/`elif`/`else`, `with`, or `try` is a unit. Two adjacent blocks get a blank between them — each iterates or branches on a different thing. This is the most common miss: an LLM stacks loops and checks with no separation.

```python
# Cramped: three blocks fused into a wall.
for f in list_files(d):
    report.error(f, "layer/: must not contain direct files")
if is_empty_dir(d):
    report.warn(d, "layer/: empty slot")
    return
for adapter in list_dirs(d):
    validate(adapter, report)
```

```python
# Paragraphed: each block stands alone.
for f in list_files(d):
    report.error(f, "layer/: must not contain direct files")

if is_empty_dir(d):
    report.warn(d, "layer/: empty slot")
    return

for adapter in list_dirs(d):
    validate(adapter, report)
```

Dense only when adjacent blocks are one tight group doing a single job — rare. When in doubt, separate: the common failure mode here is cramming, not over-spacing.

Other rules:

- **No blank between decorator and `def`.** The decorator is part of the definition — a gap wrongly implies they are separate concepts.
    ```python
    @app.get("/books/{book_id}")
    def get_book(book_id: int) -> Book:
        ...
    ```
- **Multi-line assignment → blank before it** (core rule): the wrap already broke visual density.

## Verify

```bash
ruff format .
ruff check --fix .
```

Layout changes never alter behavior; a failing run means something else changed.
