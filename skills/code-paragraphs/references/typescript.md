# TypeScript / JavaScript reference

Concrete recipes for TS/JS. Core rules apply. Idiomatic patterns and tools.

## Contents

- Imports — group order, type-only separation, tooling
- Interfaces & object types — role order, perfectionist config
- Statements — braces, ternaries, blank between functions

## Imports

Group by source, blank between groups, none within. Type-only imports get own group at end — vanish at compile time, signal "no runtime weight", stop reader hunting for value that isn't there.

```ts
import { readFile } from "node:fs/promises";

import { z } from "zod";

import { resolve } from "$app/paths";

import Badge from "$lib/components/Badge.svelte";
import Button from "$lib/components/Button.svelte";

import { toInput, toPatch } from "$lib/forms/item";

import type { Item, Requirement } from "$lib/types";
import type { PageData } from "./$types";
```

Group order:

| Order | Group                         | Example                       |
| ----- | ----------------------------- | ----------------------------- |
| 1     | Node builtins                 | `node:fs`, `node:path`        |
| 2     | External packages             | `zod`, `@tabler/icons-svelte` |
| 3     | Internal aliases (framework)  | `$app/*`                      |
| 4     | Internal aliases (components) | `$lib/components/*`           |
| 5     | Internal aliases (logic)      | `$lib/forms/*`, `$lib/utils`  |
| 6     | Relative                      | `./`, `../`                   |
| 7     | Type-only (`import type`)     | `import type { … }`           |

Related things share subgroup (all form helpers together). Split further with blank only when subgroup earns it.

### Never mix `type` into a value import

Inline `type` specifier hides type inside value import; type-only group above can't work. Reader can no longer trust everything outside it has runtime weight. Split it out.

```ts
// Avoid: inline type specifier buried in a value import.
import { toInput, type ItemInput } from "$lib/forms/item";

// Prefer: split.
import { toInput } from "$lib/forms/item";

import type { ItemInput } from "$lib/forms/item";
```

### Tooling — don't fight it

| Want                           | Rule / tool                                                                                                                                                  |
| ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Blank-line-separated groups    | `import/order` with `newlines-between: "always"` + `groups` / `pathGroups`; or `eslint-plugin-perfectionist` `sort-imports` with `newlinesBetween: "always"` |
| Force `import type` separation | `@typescript-eslint/consistent-type-imports`                                                                                                                 |
| No inline `type` specifiers    | `@typescript-eslint/no-import-type-side-effects` + `import/consistent-type-specifier-style: "prefer-top-level"`                                              |
| Simple deterministic sort      | `eslint-plugin-simple-import-sort`                                                                                                                           |

Caveat: `prettier-plugin-organize-imports` sorts and collapses blank lines between groups — fights semantic grouping above. Use ESLint (`perfectionist` or `import/order`) for grouping; let Prettier handle horizontal formatting only.

## Interfaces & object types

Order by role (core table). Blank per group. Slots / render props last.

```ts
interface Props extends HTMLButtonAttributes {
    href?: string;
    variant?: "primary" | "secondary" | "danger";

    children: Snippet;
}
```

Enforce group order + blank partitions with `eslint-plugin-perfectionist`:

```jsonc
"perfectionist/sort-interfaces": ["error", {
  "partitionByNewLine": true  // keep your role groups; sort only within them
}]
```

`partitionByNewLine: true` sorts within each blank-separated block, never merges them — paragraphs survive.

## Statements

- Always braces on `if`. Even one-line guards. Braceless guard invites classic bug: second line added later silently falls outside branch. Braces make body extent unambiguous.
    ```ts
    if (items.length === 0) {
        return;
    }
    ```
- No nested ternaries. Nested ternary hides branching inside expression where eye doesn't expect control flow. Convert to `if / else if / else` for readable branches.
- Blank between functions. Each top-level declaration = own paragraph — blank marks "new unit starts here".
- Multi-line assignment → blank before it (core rule): wrap broke visual density; blank matches conceptual break.

## Verify

```bash
pnpm eslint --fix .
pnpm prettier --write .
pnpm tsc --noEmit
```
