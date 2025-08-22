<script lang="ts">
	import { onMount } from 'svelte';
	import { invoke } from '@tauri-apps/api/core';
	import ActionButton from './ActionButton.svelte';

	interface Summary {
		name: string;
		path: string;
		modified: string;
	}

	let summaries = $state<Summary[]>([]);
	let selectedSummary = $state<Summary | null>(null);
	let summaryContent = $state('');
	let vaultPath = $state('');
	let loading = $state(true);
	let error = $state('');

	onMount(async () => {
		try {
			const [summariesResult, vaultResult] = await Promise.all([
				invoke('list_summaries'),
				invoke('get_vault_path')
			]);
			summaries = summariesResult as Summary[];
			vaultPath = (vaultResult as string) || '';
		} catch {
			error = 'Error loading summaries';
		} finally {
			loading = false;
		}
	});

	async function selectSummary(summary: Summary) {
		selectedSummary = summary;
		try {
			summaryContent = await invoke('read_summary', { path: summary.path });
		} catch {
			summaryContent = 'Error loading summary content';
		}
	}

	async function openInVault() {
		if (selectedSummary) {
			await invoke('open_in_vault', { path: selectedSummary.path });
		}
	}
</script>

<div class="flex h-full">
	<div class="w-1/3 border-r border-gray-300 p-4">
		<h2 class="mb-4 text-xl font-bold">Summaries</h2>

		{#if loading}
			<p>Loading summaries...</p>
		{:else if error}
			<p class="text-red-600">{error}</p>
		{:else if summaries.length === 0}
			<p class="text-gray-600">No summaries found</p>
		{:else}
			<ul role="list" class="max-h-96 space-y-2 overflow-y-auto">
				{#each summaries as summary (summary.path)}
					<li>
						<button
							class="w-full rounded p-2 text-left hover:bg-gray-100 {selectedSummary?.path ===
							summary.path
								? 'bg-blue-100'
								: ''}"
							onclick={() => selectSummary(summary)}
						>
							{summary.name}
						</button>
					</li>
				{/each}
			</ul>
		{/if}
	</div>

	<div class="flex-1 p-4">
		{#if selectedSummary}
			<div class="mb-4 flex items-center justify-between">
				<h3 class="text-lg font-semibold">{selectedSummary.name}</h3>
				{#if vaultPath}
					<ActionButton onclick={openInVault} color="blue">Open in Vault</ActionButton>
				{/if}
			</div>
			<div class="prose max-w-none">
				<pre class="whitespace-pre-wrap">{summaryContent}</pre>
			</div>
		{:else}
			<p class="text-gray-600">Select a summary to view</p>
		{/if}
	</div>
</div>
