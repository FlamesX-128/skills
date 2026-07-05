# Svelte reference

Svelte = TypeScript in `<script>` + HTML markup + runes/snippets. Inherits [typescript.md](./typescript.md) (imports, interfaces, statements) and [html.md](./html.md) (attribute order). This file adds Svelte-specific layer.

## Contents

- `<script>` block order — runes paragraph order
- `Props` interface — Svelte delta
- Snippets — top-level spacing, `{@const}`
- Attribute order — Svelte delta over HTML

## `<script>` block order

Runes run top→bottom in dependency order. Cannot derive from undeclared state, cannot affect unbound ref. Layout mirrors flow — one paragraph per role, blank between — reader sees data path (props → state → derived → effects → behavior) at glance.

```svelte
<script lang="ts">
	import Button from '$lib/components/Button.svelte';

	import type { Snippet } from 'svelte';

	interface Props {
		label: string;

		children: Snippet;
	}

	let { label, children }: Props = $props();

	let open = $state(false);

	let trigger = $state<HTMLButtonElement>();

	let panelId = $derived(`panel-${label}`);

	$effect(() => {
		if (open) trigger?.focus();
	});

	function toggle() {
		open = !open;
	}

	function onkeydown(event: KeyboardEvent) {
		if (event.key === 'Escape') open = false;
	}
</script>
```

| Order | Role                          | Marker              |
| ----- | ----------------------------- | ------------------- |
| 1     | imports                       | `import`            |
| 2     | types / `Props`               | `interface Props`   |
| 3     | props                         | `$props()`          |
| 4     | state                         | `$state`            |
| 5     | DOM refs (`bind:this` target) | `$state<HTMLxxx>()` |
| 6     | derived                       | `$derived`          |
| 7     | effects                       | `$effect`           |
| 8     | helpers                       | `function`          |
| 9     | event handlers                | `function on*`      |

## `Props` interface

Inherits role order from [typescript.md](./typescript.md). Svelte delta: `Snippet` is injected markup, not value — goes last. Multiple snippets stay dense (same role); single blank separates from value groups.

```svelte
interface Props {
	options: Option[];
	value?: string;

	searchable?: boolean;
	disabled?: boolean;

	variant?: 'field' | 'ghost';

	onselect?: (value: string) => void;

	icon?: Snippet;
	children: Snippet;
}
```

## Snippets

- Top-level `{#snippet}` blocks = declarations like functions → blank around them; each reads as own paragraph, not fused to adjacent markup.
- `{@const}` before markup that uses it → blank between const and markup; const = setup, markup = payload — different roles.

```svelte
{#snippet row(option: Option)}
	{@const selected = option.value === value}

	<li class:selected>
		{option.label}
	</li>
{/snippet}
```

## Attribute order

Inherits HTML role scheme ([html.md](./html.md)). Svelte delta: bindings lead. `bind:this`/`bind:*` = element wiring, most structural fact. Order: `bind:this` first → other `bind:*` (a-z) → inherited HTML order (`class:*`, `on*`, `role`, `type`, …).

```svelte
<button
	bind:this={trigger}
	bind:value
	class="field"
	class:open
	onclick={toggle}
	type="button"
>
```

- Blank line between sibling elements of different roles (icon vs input; trigger vs menu) — blank marks role boundary, same as everywhere.
- Expression-only tag → three lines; dynamic content reads as own unit, not hidden inside tag.
    ```svelte
    <span class="truncate">
    	{option.label}
    </span>
    ```

Enforce with `eslint-plugin-svelte`. `svelte/sort-attributes` sorts; `prettier-plugin-svelte` does horizontal only (never reorders attributes):

```jsonc
"svelte/sort-attributes": "error"
```

## Verify

```bash
pnpm eslint --fix .
pnpm prettier --write .
pnpm svelte-check
```
