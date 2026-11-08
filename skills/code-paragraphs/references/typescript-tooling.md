# Shared TS/JS tooling

Read when onboarding a repository or changing style tooling. Ordinary code edits use existing commands and the manual audit in [typescript.md](typescript.md).

The templates in [assets/ts-style](../assets/ts-style/) adapt the shared style configuration supplied from Doorknocker. They are not installed automatically and do not contain that project's package names, framework plugins, filesystem paths, or SQL formatter. SQL has a separate owner.

## One owner per concern

Keep formatter dependencies and base configuration at the consuming repository root. Packages may have thin ESLint adapters for files, runtime globals, aliases, ignores, and measured thresholds. They should not each carry a formatter installation or independent style policy.

The templates provide:

- `prettier.mjs`: four spaces, width 80, semicolons, double quotes. Add framework plugins only where that project needs them.
- `eslint.mjs`: `createProjectEslintConfig`, combining JS/TS, selected Functional rules, Sonar, the comment rule, and Prettier compatibility.
- `rules.mjs`: style rules, alias overrides, and required per-package complexity measurements.
- `comments.mjs`: a local ESLint plugin that converts standalone prose blocks, recognizes tagged documentation, and preserves compiler/bundler/license annotations. Inline block comments and unsupported tags are reported without an unsafe fix.
- `comments.test.mjs` and `config.test.mjs`: behavior checks for the reusable configuration.

For a requested migration, copy this directory into the project's shared tooling location, for example `scripts/style/`. Merge into existing configs; preserve unrelated rules, globals, ignores, and parser settings. Use `.mjs` entrypoints so this works without changing the package's module type.

Declare compatible versions of `prettier`, `eslint`, `@eslint/js`, `typescript`, `typescript-eslint`, `eslint-plugin-functional`, `eslint-plugin-sonarjs`, and `eslint-config-prettier` in that root's dev dependencies and lockfile. Use the project's package manager. Do not install unpinned latest versions silently or overwrite a lockfile. The bundled tests must pass with the selected versions before adoption. The adapted templates were verified with Prettier 3.9.9, ESLint 10.9.1, `@eslint/js` 10.0.1, TypeScript 6.0.3, `typescript-eslint` 8.68.0, Functional 10.0.1, SonarJS 4.2.0, and `eslint-config-prettier` 10.1.8 from the supplied project; this records a tested combination, not a requirement to upgrade an existing project.

Root `prettier.config.mjs` can re-export the shared file:

```js
export { default } from "./scripts/style/prettier.mjs";
```

Use `createProjectEslintConfig` from the root `eslint.config.mjs` or a thin package adapter. Supply `files`, `globals`, `ignores`, `tsconfigRootDir`, and measured `thresholds` for that scope; `beforeBase`/`afterBase` accept existing flat-config entries. `createAliasConfigs` is opt-in because aliases depend on the consuming project. Do not invent threshold numbers to make the factory run.

## Integrate without formatter cycles

The compatibility config goes last. It preserves `curly` and `quotes` because these are explicit style rules, while disabling competing formatting rules. Keep `multiline-comment-style` off: the custom comment rule is the sole owner of comment conversion and protects annotations the generic fixer may rewrite.

Use TypeScript ESLint for unused bindings; avoid duplicate Sonar diagnostics. The template disables Sonar's redundant-optional fix because optionality and explicit `undefined` can be distinct contracts. Never enable a plugin's blanket `all` preset as a shortcut.

Run formatting, then ESLint fixes on touched files. Run both checks again without fixes. If they disagree or a second pass changes output, fix the configuration instead of alternating fixers indefinitely. Ensure the editor resolves the same workspace formatter and config.

## Aliases before import migration

Verify all four consumers of an alias before rewriting imports:

1. TypeScript source resolution (`paths`, relative to the correct config).
2. Test/bundler resolution, using the project's actual runner.
3. Runtime and emitted imports. For a `tsc` emit pipeline, use an appropriate rewrite step such as the project's `tsc-alias` setup; a different bundler/runtime may resolve aliases itself.
4. ESLint restrictions scoped to files where the alias is valid.

The template's `createAliasConfigs` supports source restrictions and a narrower test restriction for relative paths into the same project's `src`. Review the actual layout before using it. It does not handle every project alias or enforce re-export barrels: check those manually too. Keep test-to-test and script-to-config imports valid.

Do not copy an import migration that infers emit behavior from package names such as `server` or `web`. Use explicit project configuration. Import grouping must preserve runtime order, attached comments, and emitted initialization, including inline type specifiers. A generic alphabetic sorter is not equivalent to the module paragraphs in this profile.

## Measured complexity, not shared arbitrary limits

For each package measure complexity, cognitive complexity, maximum depth, parameter count, and function lines (excluding blanks/comments). Use a reporting pass without fixes and thresholds low enough to reveal the observed maxima. Record the measurements and date next to the package adapter. For a scope with no applicable functions, record that fact and choose the minimum valid positive limit.

Pass those values as `complexity`, `cognitiveComplexity`, `maxDepth`, `maxParams`, and `maxLinesPerFunction`. The template rejects missing or nonpositive values; it has no shared default thresholds. They are warnings checked with `--max-warnings 0`, so they still fail verification. Tighten later as code improves; do not raise limits or suppress a finding to complete a style cleanup.

## Generated output and verification

Configure generated, vendored, build-output, and private diagnostic ignores before the first write. Ensure source, tests, and scripts remain covered. Test ignores with representative paths from nested packages. Where a generator has a byte-identity check, regenerate with its command instead of hand-formatting its output. SQL migrations and fragments belong to their own workflow.

Run the project's equivalent of:

```bash
pnpm exec prettier --check .
pnpm exec eslint . --max-warnings 0
node --test scripts/style/*.test.mjs
pnpm run typecheck
pnpm run test
pnpm run build
```

These commands are examples for the consuming project, not scripts installed by this skill. Use its real package scope and script names. If generators or schemas changed, run the generator consistency check; if emitted packages changed, check their consumers too. Complete the manual audit in `typescript.md` after tools finish.
