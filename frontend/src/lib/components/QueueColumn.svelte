<script lang="ts">
	import type { Snippet } from 'svelte';

	// Uma interface limpa para as props.
	type Props = {
		title: string;
		files: string[];
		// Opcional: Snippet que recebe 'file' e define como renderizar o item.
		// Esta é a forma correta de tipar um "scoped slot".
		children?: Snippet<{ file: string }>;
	};

	const { title, files, children } = $props<Props>();
</script>

<div class="bg-white p-4 rounded-lg shadow-md flex flex-col">
	<h2 class="text-lg font-semibold text-gray-700 border-b pb-2 flex-shrink-0">{title}</h2>
	<ul class="mt-2 space-y-1 text-sm overflow-y-auto flex-grow min-h-[12rem] max-h-[24rem]">
		{#each files as file (file)}
			<li class="p-1 rounded hover:bg-gray-100 flex justify-between items-center">
				{#if children}
					{@render children({ file })}
				{:else}
					<span class="text-gray-800 break-all">{file}</span>
				{/if}
			</li>
		{:else}
			<li class="text-gray-400 italic p-1">Empty</li>
		{/each}
	</ul>
</div>