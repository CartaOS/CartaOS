<script lang="ts">

	type Color = 'blue' | 'green' | 'purple' | 'amber';

    // Props via Svelte 5 $props() (no generics)
    const {
        onclick,
        isLoading = false,
        color = 'blue',
        loadingText = 'Loading...',
        children,
        class: className = ''
    } = $props();

    // Ensure typed key for colorClasses access
    const colorKey: Color = color as Color;

	// Using Record for stricter typing, eliminating the need for 'as Color'
    const colorClasses: Record<Color, string> = {
        blue: 'bg-blue-500 hover:enabled:bg-blue-700',
        green: 'bg-green-500 hover:enabled:bg-green-700',
        purple: 'bg-purple-500 hover:enabled:bg-purple-700',
        amber: 'bg-amber-500 hover:enabled:bg-amber-600'
    };
</script>

<button
	{onclick}
	disabled={isLoading}
    class="{className} text-white font-bold py-2 px-4 rounded transition-colors disabled:bg-gray-300 disabled:text-gray-800 disabled:border disabled:border-gray-400 disabled:cursor-not-allowed focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 focus-visible:ring-gray-700 {colorClasses[colorKey]}"
>
	{#if isLoading}
		{loadingText}
	{:else}
		{#if children}
			{@render children()}
		{/if}
	{/if}
</button>
