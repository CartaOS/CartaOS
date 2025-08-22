<script lang="ts">
	import type { Snippet } from 'svelte';
	// Properly type children as a Snippet that accepts one arg: { file: string }
	const {
		title,
		files,
		children
	}: { title: string; files: string[]; children?: Snippet<[{ file: string }]> } = $props();
</script>

<div class="flex flex-col rounded-lg bg-white p-4 shadow-md">
	<h2 class="flex-shrink-0 border-b pb-2 text-lg font-semibold text-gray-700">{title}</h2>
	<ul class="mt-2 max-h-[24rem] min-h-[12rem] flex-grow space-y-1 overflow-y-auto text-sm">
		{#each files as file (file)}
			<li class="flex items-center justify-between rounded p-1 hover:bg-gray-100">
				{#if children}
					{@render children({ file })}
				{:else}
					<span class="break-all text-gray-800">{file}</span>
				{/if}
			</li>
		{:else}
			<li class="text-gray-700 italic p-1">Empty</li>
		{/each}
	</ul>
</div>
