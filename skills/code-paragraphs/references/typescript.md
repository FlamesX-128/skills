# TypeScript / JavaScript

Apply to hand-written TS/JS source, tests, scripts, examples, and fixtures in the requested scope. Generated output stays generator-owned. JSX, Svelte templates, and other markup use their own profile; framework-required mutation is not a reason to rewrite framework semantics.

Read this entire profile before editing TS/JS. For config changes, also read [typescript-tooling.md](typescript-tooling.md). The rules below resolve the general core's ambiguous cases.

## Enforcement map

| Rule                                             | Tool coverage                      | Writer/reviewer responsibility                                    |
| ------------------------------------------------ | ---------------------------------- | ----------------------------------------------------------------- |
| Braces for control flow and arrow bodies         | ESLint `curly`, `arrow-body-style` | Keep empty swallow callbacks as `{}`; never invent a return value |
| Paragraph after a closed block                   | ESLint padding rule                | Apply the paragraph exceptions below                              |
| Paragraphs within blocks                         | Manual                             | Read every touched block, including nested callbacks              |
| Four spaces, semicolons, double quotes, width 80 | Shared Prettier config             | Use the effective project config; do not hand-align columns       |
| No ternaries                                     | ESLint `no-ternary`                | Name the decision; preserve evaluation behavior                   |
| Declarative flow, no loops or `let`              | Functional plugin                  | Review legitimate sequential/streaming exemptions                 |
| Source aliases                                   | Import restrictions                | Verify typecheck, runtime, test, and build resolution first       |
| Unused bindings                                  | TypeScript ESLint                  | Keep rest-destructuring omissions and intentional `_` parameters  |
| Complexity limits                                | ESLint and Sonar                   | Measure per package, restructure rather than suppress             |
| Member groups and ordering                       | Manual                             | Group by role, then order within each group                       |
| Imports and re-exports                           | Manual or a compatible AST helper  | Same-module value/type adjacency; preserve initialization order   |
| Backticks for interpolation or multiline strings | ESLint quotes rule                 | Avoid replacing interpolation with string concatenation           |
| Optional property shape                          | Manual plus typecheck              | Check object producers before removing explicit `undefined`       |
| Line comments and tagged JSDoc                   | Bundled comment rule               | Keep reasons short and preserve protected annotations             |

Tool coverage depends on the effective configuration. Do not claim enforcement because a plugin is installed. A clean lint result does not check the manual rows.

## Paragraphs: one purpose per group

Use exactly one blank line between logical steps: acquire, validate, transform, respond. Keep related compact declarations dense. Apply this inside callbacks, nested blocks, constructors, and at module level.

```ts
function normalizeHeaders(headers: Headers, names: readonly string[]) {
    const entries = names
        .map((name) => {
            return [name, headers.get(name)] as const;
        })
        .filter((entry): entry is readonly [string, string] => {
            return entry[1] !== null;
        });

    return Object.fromEntries(entries);
}
```

Apply paragraph boundaries in this priority order:

1. A multiline declaration closes its paragraph. Put a blank line after it even when the next statement consumes its result. Separate it from compact declarations above, too.
2. A closed block takes a blank line before the next statement. Do not detach `else`, `catch`, `finally`, or the `while` of `do…while` from their construct.
3. A terminal success return starts its own paragraph after acquisition/computation. A function containing only a return needs no leading blank.
4. A compact acquisition and its immediate guard stay together; the guard's early return stays inside its braces. Put a blank line after the guard block.
5. Compact dependent declarations feeding the same next step may stay together. A compact destructuring directly feeding a returned object may also stay attached.
6. A different operation/context or a change from calling to constructing starts a new paragraph, even if data is derived.

Rule 1 wins over rules 4–5. An early-exit return is part of its guard; it is not the terminal success-return case.

```ts
const response = await fetch(url);
responseGuard(response);

const payload = await response.json();

return payload;
```

```ts
const result = await invoke(client, operation, options);

if (result.status === 204) {
    return undefined;
}

return result.data;
```

Do not add blanks inside a single semantic step for breathing room. Do not extract functions based on a blank-line count; extract when a name clarifies a separate responsibility.

## Members: role first, order second

Group interface/type/class fields, declared objects, returned objects, schema definitions, and large fixtures by semantic role. Typical roles: identity, content, transport, helper functions, main operation, timestamps. A single identity field can form a paragraph; do not manufacture groups just to make every paragraph the same size.

```ts
interface InvocationOptions {
    readonly workspaceId?: string;

    readonly headers?: Readonly<Record<string, string>>;
    readonly signal?: AbortSignal;
}
```

Inside a group, order by actual usage flow (`path`, `query`, `headers`, `body`). When members are interchangeable, use alphabetic order. Keep an already intentional short-to-long staircase only when usage and dependency order do not decide the order; do not reshuffle unrelated members by length. Alphabetize independent import specifiers and destructuring targets.

Small inline flow literals such as `{ ...result, data: undefined }`, one or two closely related fields, case-table rows, parameters, and union variants stay dense. Do not reorder public parameters. For argument objects with at least three members spanning different roles, separate spread/defaults, data, callback implementations, and flags into paragraphs.

Constructor assignments mirror the declaration groups. Keep base boilerplate such as `this.name` with `super`. Do not move pre-`super` computation or side-effectful initializers to satisfy visual order. Keep helpers together and the main operation in its own paragraph in a returned service object.

Never reorder spreads, computed keys, duplicate keys, getters, decorators, or expressions with side effects mechanically. Preserve behavior before applying an ordering tiebreak.

## Imports: the module is the paragraph

Value import first, then whole-clause `import type` from the same module, with no blank between them. Separate different source modules with one blank line. Do not collect all types at the bottom. Prefer separate whole-clause type imports over inline `type` specifiers.

```ts
import { z } from "zod";
import type { ZodType } from "zod";

import type { Client } from "@/client.js";

import { modelArguments } from "@/contracts.js";
import type { OperationContract } from "@/contracts.js";

import { ApiError } from "@/errors.js";
```

Group external packages first, own modules alphabetically second, generated modules last. Imports from the same generated directory can share a paragraph. Apply module adjacency to re-export barrels too.

Runtime import order takes precedence over sorting: preserve side-effect imports and existing initialization order. An AST helper must report unsafe reorderings for review. Changing an inline `type` import into a whole-clause type import can change emitted initialization; inspect the emit settings and module effects before converting existing code. Keep attached comments and directives with their statement.

Use the project's established source alias. For onboarding, `@/` is the default, but never rewrite specifiers until all resolvers support it. Keep relatives where the alias does not reach, including scripts and test helpers outside the source tree. Generated modules keep generator-owned imports.

## Decisions and declarative flow

- Always use braces on control statements and block bodies with explicit returns on arrows. An intentionally empty `.catch(() => {})` remains an empty block.
- No ternaries, including single ones. Extract a named decision function with guards. Case tables and code-generation string assembly are the only ternary exemptions.
- Prefer `map`, `filter`, `find`, `some`, and `Object.fromEntries` to loops and mutable `let` accumulators. Do not replace a sequential asynchronous loop with concurrent promises merely to satisfy style.
- Loop exemptions: externally constrained sequencing (cursor pagination, transaction-bound operations, retries, sequential model rounds), pull streams yielding events as they arrive, and assembling case tables or generated strings. A loop is not exempt merely because it predates this skill.
- Use conditional object spread only when it preserves the original condition and value evaluation. Extract a named builder for a real decision.

An exemption has a short English reason and an exact next-line rule directive. No intervening line, no directory-wide disable. Keep a needed mutable binding exemption as narrow as the loop exemption.

```ts
// ! Each event must be yielded immediately; buffering would break streaming.
// eslint-disable-next-line functional/no-loop-statements
while (stream.hasNext()) {
    yield await stream.next();
}
```

If no listed exemption fits, restructure the code or report the specific unresolved conflict. Do not add a suppression just to pass lint.

## Optional properties and comments

Prefer `foo?: T` for optional hand-written properties. Keep `foo: T | undefined` or `foo?: T | undefined` when producers explicitly assign `undefined` and the contract requires it. Check callers and spread producers under `exactOptionalPropertyTypes`; do not apply a redundant-optional autofix blindly.

Write explanatory comments as consecutive `//` lines in English. Code expresses what; comments explain a short reason. Do not wrap one-line comments merely to fill the print width. Use `// !` for a constraint/exemption, `// ?` for an open question, `// *` for an essential design decision, and `// TODO` for known pending work.

Reserve `/** */` for real tags: `@param`, `@returns`, `@deprecated`, `@example`, `@internal`, `@throws`, `@see`, `@defaultValue`, and `@type` for JavaScript typing. A bare description becomes `//`; do not duplicate the signature in prose. Preserve licenses, lint/compiler directives, pure annotations, source-map directives, and bundler annotations. Inline block comments require review because converting them can change parsing.

## Final manual audit

Before claiming completion, inspect the final touched diff:

- Each block has paragraphs by purpose; multiline declarations close their paragraph; compact acquisition/guard pairs stay together.
- Members are grouped by role, including constructor assignments and nontrivial argument objects. No evaluation order or public parameter order changed.
- Same-module value/type imports are adjacent; no global type-only section remains. Runtime initialization and directive attachment are intact.
- No ternaries, loops, mutable bindings, or lint suppressions remain without their specific allowed reason.
- Optional fields match actual object producers. Comments add a reason, tagged JSDoc adds information, protected annotations are intact.
- Existing formatter/lint checks pass after fixes, with zero warnings; relevant typecheck, tests, build, and generator checks pass. State any check that could not run.
