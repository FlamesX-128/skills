# HTML reference

Plain HTML markup. Core rules apply. Attribute order main lever.

## Attribute order

Default: group by role. Order from identity (what tag is) to behavior: identity, data, screen-reader info, presentation, events. Left-to-right puts essential facts first. Use table below. Escape hatch: pure a-z if project enforces — pick one, never mix.

| Order | Role           | Examples                         |
| ----- | -------------- | -------------------------------- |
| 1     | Identity       | `id`, `name`, `type`             |
| 2     | Data           | `data-*`, `value`, `href`, `src` |
| 3     | Accessibility  | `role`, `aria-*`, `alt`, `title` |
| 4     | Presentation   | `class`, `style`                 |
| 5     | Event handlers | `onclick`, `onsubmit`            |

```html
<input
    id="email"
    name="email"
    type="email"
    data-testid="email-field"
    aria-describedby="email-hint"
    class="field"
    required
/>
```

## Blank lines between siblings

Separate sibling elements with different roles; keep single visual unit dense. Blank means "different job". Icon + input it decorates = one dense unit. Search field + results list below = two units, blank between.

```html
<div class="search">
    <svg class="icon">…</svg>

    <input class="field" type="search" />
</div>
```

## Tooling — be honest

No standard formatter reorders HTML attributes. Prettier and `htmlhint` do not sort attributes. Options:

- Keep order as convention LLM/author applies (this skill).
- Frameworks: use their linter (`eslint-plugin-svelte` `svelte/sort-attributes`, `eslint-plugin-react` `react/jsx-sort-props`).
- Pure-HTML enforcement needs custom rule. Treat order as reviewed convention.

## Verify

```bash
pnpm prettier --write .   # horizontal only; won't reorder attributes
```
