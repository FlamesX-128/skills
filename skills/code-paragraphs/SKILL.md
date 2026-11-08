---
name: code-paragraphs
description: Apply when writing, editing, or reviewing JavaScript or TypeScript. Use blank-line paragraphs, module-grouped imports, role-based member ordering, and explicit control flow.
license: MIT
metadata:
    author: FlamesX-128
    version: 4.1.0
    user-invocable: true
---

# Code Paragraphs

## Scope

- Apply to hand-written JavaScript and TypeScript. Leave generated files unchanged.

## Subagents

- Assign one specialist per applicable area: syntax/flow, imports, members, paragraphs, then comments.
- Run specialists sequentially on the same file. Wait for each to finish before starting the next on that file's updated contents.
- For multiple files, use disjoint batches. Run batches in parallel; never let agents edit the same file concurrently.
- Start each specialist with fresh context. Provide only the current target files, this skill, the assigned area, and permitted tools.
- Share updated code, not proposed fixes, prior analyses, or other agents' responses. Limit access to the provided files and authorized tools.
- Keep each specialist within its assigned area. The coordinator starts the next specialist; specialists do not delegate further.
- Run the project's checks and give a fresh final reviewer the completed files and this skill before declaring completion.
- If subagents are unavailable, perform separate passes for the same areas and report the limitation.

## Paragraphs

- Use exactly one blank line between logical steps; keep each step dense.
- Keep a compact declaration with its immediate setup or validation of the same value.
- Separate validation phases by concern; shared validation does not make them one paragraph.
- Isolate statements containing block-bodied callbacks with blank lines, including callback-bearing declarations. Keep the complete call or chain together.
- Separate multiline declarations from surrounding statements.
- Keep a direct guard attached to a compact declaration or wrapped literal. This overrides multiline spacing, not callback spacing.
- Give each object/resource its own setup paragraph; separate callback registration and composition.
- Put a blank line after a closed block; keep `else`, `catch`, `finally`, and `do…while` continuations attached.
- Put a blank line before a final success return; keep compact destructuring attached to its returned object.
- Separate top-level functions, classes, and types.
- Do not extract functions just to reduce blank-line counts.

## Imports

- Group imports and re-exports by source module, with one blank line between modules.
- Put value imports before whole-clause `import type` from the same module, without a blank line between them.
- Do not collect type imports at the bottom or use inline `type` specifiers.
- Order groups: external packages, own modules, generated modules. Sort own modules by module path, regardless of import length or wrapping.
- Alphabetize independent specifiers and destructuring bindings.
- Preserve side-effect order and attached directives; do not reorder effectful imports blindly.
- Use the existing source alias; keep relative imports where the alias does not resolve.

## Members

- Group fields, properties, and schema/object members by role; separate roles with one blank line.
- Order within a role by usage, then alphabetically; preserve an intentional length staircase only among interchangeable members.
- Keep small related objects, case-table rows, parameters, and union variants dense. Preserve public parameter order.
- Separate spreads/defaults, data, callbacks, and flags in nontrivial argument objects.
- Mirror field groups in constructor assignments; keep base setup with `super`.
- Do not reorder spreads, computed keys, or initializers when evaluation order matters.

## Syntax and flow

- Use braces for control statements and block bodies for arrows; return explicitly when the arrow produces a value.
- Keep intentionally empty callbacks empty.
- Replace ternaries with named decisions. Allow ternaries only in case tables and code-generation strings.
- Use `const` and collection transforms instead of `let` and loops.
- Preserve required sequential I/O, retries, streaming, and table/code-generation loops. Explain exemptions with `// !` directly above the exact next-line lint directive.
- Use four spaces, semicolons, double quotes, and width 80 unless the project specifies otherwise.
- Use backticks for interpolation or multiline strings, not plain single-line strings.
- Use `?:` for optional properties; retain explicit `undefined` when object producers require it.

## Comments and checks

- Write short English reasons as `//` comments; do not restate the code.
- Use `// !` for constraints, `// ?` for questions, `// *` for essential decisions, and `// TODO` for pending work.
- Reserve JSDoc for real documentation tags or JavaScript `@type`. Preserve licenses and compiler/lint/bundler annotations.
- Run the project's formatter and lint checks; run relevant typecheck, tests, and build after code changes.
- Review paragraph boundaries, member roles, and import order manually after formatting.
- Do not add unlisted lint exemptions or raise complexity limits to pass checks.
- For requested tooling setup, adapt [assets/ts-style](assets/ts-style/); keep shared dependencies and configuration at the project root.
