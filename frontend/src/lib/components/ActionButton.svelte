<script lang="ts">
	import type { Snippet } from 'svelte';

	type Color = 'blue' | 'green' | 'purple';

	type Props = {
		onclick: () => unknown; // unknown é um pouco mais seguro que any
		isLoading: boolean;
		color?: Color;
		loadingText?: string;
		children?: Snippet;
	};

	const {
		onclick,
		isLoading = false,
		color = 'blue',
		loadingText = 'Loading...',
		children
	} = $props<Props>();

	// Using Record for stricter typing, eliminating the need for 'as Color'
	const colorClasses: Record<Color, string> = { 
		blue: 'bg-blue-500 hover:enabled:bg-blue-700',
		green: 'bg-green-500 hover:enabled:bg-green-700',
		purple: 'bg-purple-500 hover:enabled:bg-purple-700'
	};
</script> 

<button
	{onclick}
	disabled={isLoading}
	class="text-white font-bold py-2 px-4 rounded transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed {colorClasses[color as Color]}"
>
	{#if isLoading}
		{loadingText}
	{:else}
		{#if children}
			{@render children()}
		{/if}
	{/if}
</button>