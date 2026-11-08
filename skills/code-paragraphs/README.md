# Code Paragraphs

Group code into paragraphs by purpose. Separate roles with a blank line; keep related statements and members together.

The shared core supports language-specific profiles. This revision concentrates on TypeScript/JavaScript: explicit paragraph precedence, same-module value/type imports, role-based member ordering, declarative flow, optional properties, and comment policy. Go, Python, Svelte, and HTML references remain available; TS-only rules do not apply to those languages or markup.

## Install

```bash
skills add FlamesX-128/skills --skill=code-paragraphs
```

## Use

Start with [SKILL.md](SKILL.md), then read the applicable language profile. For TS/JS, read [typescript.md](references/typescript.md) before writing and run its final manual audit after formatting/linting. Passing lint alone does not establish paragraph or semantic ordering compliance.

For requested tooling setup, read [typescript-tooling.md](references/typescript-tooling.md). [assets/ts-style](assets/ts-style/) contains portable shared ESLint/Prettier templates and behavior tests, adapted from Doorknocker's shared tooling. Copy and merge them into the consuming repository's root tooling; installing this skill does not install npm dependencies or change project configuration. There is no per-skill formatter installation.

The templates cover syntax, control flow, measured complexity, and comment normalization. Paragraph meaning, member roles, import adjacency, and optional-property contracts still need manual review. They do not bundle project-specific alias migrations, framework plugins, or SQL formatting.

## References

| Context                             | Reference                                                 |
| ----------------------------------- | --------------------------------------------------------- |
| TS/JS writing and review            | [typescript.md](references/typescript.md)                 |
| TS/JS shared tooling and onboarding | [typescript-tooling.md](references/typescript-tooling.md) |
| Go                                  | [go.md](references/go.md)                                 |
| Python                              | [python.md](references/python.md)                         |
| Svelte                              | [svelte.md](references/svelte.md)                         |
| HTML                                | [html.md](references/html.md)                             |
| Background reading                  | [literature.md](references/literature.md)                 |

Existing Svelte examples illustrate framework structure; their required reactive mutation is outside the TS profile's declarative-flow restrictions. The shared core and explicit language rules take precedence over historical heuristics in the background reading.

## Maintenance

Repository-wide formatting is documented in the [root README](../../README.md#development). In a consuming project with the template dependencies installed, run `node --test scripts/style/*.test.mjs` after adapting the shared config; see the tooling reference for integration checks.

## License

MIT, © 2026 FlamesX-128. See [LICENSE](LICENSE).
