<script lang="ts">

	type Color = 'blue' | 'green' | 'purple';

	// Props (implicit via $props usage below):
	// - onclick: () => unknown
	// - isLoading: boolean
	// - color?: Color
	// - loadingText?: string
	// - label?: string
	// - children?: Snippet

	const {
		onclick,
		isLoading = false,
		color = 'blue',
		loadingText = 'Loading...',
		label,
		children
	} = $props();

	// Using Record for stricter typing, eliminating the need for 'as Color'
	// Colors adjusted for better contrast with white text (aim >= 4.5:1)
	const colorClasses: Record<Color, string> = { 
		blue: 'bg-blue-600 hover:enabled:bg-blue-700',
		green: 'bg-green-700 hover:enabled:bg-green-800',
		purple: 'bg-purple-700 hover:enabled:bg-purple-800'
	};

	function handleClick() {
		if (!isLoading) onclick();
	}
</script> 

<button
	onclick={handleClick}
	disabled={isLoading}
	aria-busy={isLoading}
	aria-label={isLoading ? loadingText : (label ?? undefined)}
	class="text-white font-bold py-2 px-4 rounded transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed {colorClasses[color as Color]}"
>
	{#if isLoading}
		{loadingText}
	{:else}
		{#if children}
			{@render children()}
		{:else if label}
			{label}
		{/if}
	{/if}
</button>