# Code Paragraphs

JavaScript/TypeScript style rules in one concise [SKILL.md](SKILL.md). Other languages are outside this skill's scope.

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Optional shared tooling

- Adapt [assets/ts-style](assets/ts-style/) into the consuming project's shared tooling directory.
- Keep dependencies at the project root: `prettier`, `eslint`, `@eslint/js`, `typescript`, `typescript-eslint`, `eslint-plugin-functional`, `eslint-plugin-sonarjs`, `eslint-config-prettier`.
- Re-export `prettier.mjs` from the root Prettier config; merge `createProjectEslintConfig` from `eslint.mjs` into the root ESLint config.
- Supply project file scopes, globals, ignores, and measured `thresholds`: `complexity`, `cognitiveComplexity`, `maxDepth`, `maxParams`, `maxLinesPerFunction`.
- Keep the bundled Prettier compatibility config last and `multiline-comment-style` off; `comments.mjs` owns comment fixes.
- Enable alias restrictions only after typecheck, tests, runtime, and build resolve the alias.
- Run `node --test scripts/style/*.test.mjs` after adaptation; use the actual tooling path.

Repository formatting: [root README](../../README.md#development). License: [MIT](LICENSE).
