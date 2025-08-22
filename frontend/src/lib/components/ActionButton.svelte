<script lang="ts">
	import type { Snippet } from 'svelte';

	type Color = 'blue' | 'green' | 'purple' | 'amber';

	type Props = {
		onclick: () => unknown;
		isLoading?: boolean;
		color?: Color;
		loadingText?: string;
		label?: string;
		children?: Snippet;
	};

	const {
		onclick,
		isLoading = false,
		color = 'blue',
		loadingText = 'Loading...',
		label,
		children
	}: Props = $props();

	const colorClasses: Record<Color, string> = {
		blue: 'bg-blue-600 hover:enabled:bg-blue-700',
		green: 'bg-green-700 hover:enabled:bg-green-800',
		purple: 'bg-purple-700 hover:enabled:bg-purple-800',
		amber: 'bg-amber-600 hover:enabled:bg-amber-700'
	};

	function handleClick() {
		if (!isLoading) onclick();
	}
</script>

<button
	type="button"
	onclick={handleClick}
	disabled={isLoading}
	aria-busy={isLoading}
	aria-label={isLoading ? loadingText : (label ?? undefined)}
	class="rounded px-4 py-2 font-bold text-white transition-colors disabled:cursor-not-allowed disabled:bg-gray-400 {colorClasses[
		color as Color
	]}"
>
	{#if isLoading}
		{loadingText}
	{:else if children}
		{@render children()}
	{:else if label}
		{label}
	{/if}
</button>
