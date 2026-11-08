# Code Paragraphs

Style rules for hand-written JavaScript and TypeScript: paragraphs, module-grouped imports, member ordering, explicit control flow, and comments. The complete rules live in [SKILL.md](SKILL.md).

## Install

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Workflow

This workflow is based on the [blind-subagents](../blind-subagents/SKILL.md) approach.

- Process each file through specialists in this order: syntax/flow, imports, members, paragraphs, then comments.
- Wait for each specialist to finish; the next edits the updated version of the same file.
- Give each specialist fresh context, the current files, the skill, its assigned area, and permitted tools. Share code without previous analyses or responses.
- Split multiple files into disjoint batches for parallel work; keep passes sequential within each batch.
- Run the project's checks, then have a fresh final reviewer check the completed files against the full skill.
- If subagents are unavailable, perform the same passes locally and report the limitation.

## Optional shared tooling

- Prettier handles formatting; ESLint applies JS/TS, Functional, SonarJS, and comment rules. Paragraph meaning and member roles still require manual review.
- Adapt [assets/ts-style](assets/ts-style/) into the consuming project's shared tooling directory.
- Keep dependencies at the project root: `prettier`, `eslint`, `@eslint/js`, `typescript`, `typescript-eslint`, `eslint-plugin-functional`, `eslint-plugin-sonarjs`, `eslint-config-prettier`.
- Re-export `prettier.mjs` from the root Prettier config; merge `createProjectEslintConfig` from `eslint.mjs` into the root ESLint config.
- Supply project file scopes, globals, ignores, and measured `thresholds`: `complexity`, `cognitiveComplexity`, `maxDepth`, `maxParams`, `maxLinesPerFunction`.
- Keep the bundled Prettier compatibility config last and `multiline-comment-style` off; `comments.mjs` owns comment fixes.
- Enable alias restrictions only after typecheck, tests, runtime, and build resolve the alias.
- Run `node --test scripts/style/*.test.mjs` after adaptation; use the actual tooling path.

Repository formatting: [root README](../../README.md#development). License: [MIT](LICENSE).
