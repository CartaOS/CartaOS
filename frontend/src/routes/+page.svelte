<script lang="ts">
	import { invoke } from '@tauri-apps/api/core';
	import { onMount } from 'svelte';
	import { listen } from '@tauri-apps/api/event';
	import SettingsView from '$lib/components/SettingsView.svelte';
	import LabView from '$lib/components/LabView.svelte';
	import ActionButton from '$lib/components/ActionButton.svelte';
	import QueueColumn from '$lib/components/QueueColumn.svelte';
	import LogPanel from '$lib/components/LogPanel.svelte';

	// --- State ---
	let currentView: 'pipeline' | 'lab' | 'settings' = $state('pipeline');
	let statusMessage = $state('Waiting for action...');
	let isLoading = $state(false);
	let triageFiles = $state<string[]>([]);
	let labFiles = $state<string[]>([]);
	let ocrFiles = $state<string[]>([]);
	let summaryFiles = $state<string[]>([]);

	// --- Lógica de Ações ---
	async function withLoading<T>(action: () => Promise<T>, baseMessage: string): Promise<void> {
		statusMessage = `Running ${baseMessage}...`;
		isLoading = true;
		try {
			const result = await action();
			if (typeof result === 'string' && result.trim()) {
				statusMessage = result.trim();
			} else {
				statusMessage = `${baseMessage} completed successfully.`;
			}
			await refreshAllQueues();
		} catch (error) {
			console.error("Caught error in withLoading:", error);
			const errorMessage = typeof error === 'string' ? error : (error instanceof Error ? error.message : `An unknown error occurred during ${baseMessage}.`);
			statusMessage = `ERROR in ${baseMessage}: ${errorMessage}`;
			console.error(statusMessage, error);
		} finally {
			isLoading = false;
		}
	}

	const handleTriage = () => withLoading(() => invoke('run_triage'), 'Triage');
	const handleOcr = () => withLoading(() => invoke('run_ocr_batch'), 'OCR Batch');
	const handleSummarizeBatch = () => withLoading(() => invoke('run_summarize_batch'), 'Summarization Batch');
	const handleSummarizeSingle = (fileName: string) =>
		withLoading(
			() => invoke('run_summarize_single', { fileName, dryRun: false, debug: false, forceOcr: false }),
			`Summarizing ${fileName}`
		);
	const handleCorrect = (fileName: string) =>
		withLoading(
			() => invoke('open_scantailor', { fileName }),
			`Opening ScanTailor for ${fileName}`
		);
	const handleFinalize = (fileName: string) =>
		withLoading(() => invoke('finalize_lab_file', { fileName }), `Finalizing ${fileName}`);

	// Função de refresh
	async function refreshAllQueues(): Promise<void> {
		statusMessage = 'Refreshing all file queues...';
		isLoading = true;
		try {
			const [triage, lab, ocr, summary] = await Promise.all([
				invoke<string[]>('get_files_in_stage', { stage: '02_Triage' }),
				invoke<string[]>('get_files_in_stage', { stage: '03_Lab' }),
				invoke<string[]>('get_files_in_stage', { stage: '04_ReadyForOCR' }),
				invoke<string[]>('get_files_in_stage', { stage: '05_ReadyForSummary' })
			]);

			triageFiles = triage;
			labFiles = lab;
			ocrFiles = ocr;
			summaryFiles = summary;

			statusMessage = 'File queues refreshed successfully.';
		} catch (error) {
			console.error("Caught error in refreshAllQueues:", error);
			const errorMessage = typeof error === 'string' ? error : (error instanceof Error ? error.message : 'An unknown error occurred while refreshing queues.');
			statusMessage = `ERROR refreshing queues: ${errorMessage}`;
			console.error(statusMessage, error);
		} finally {
			isLoading = false;
		}
	}

	onMount(() => {
		let unlisten: (() => void) | undefined;
		// initial load
		refreshAllQueues();
		// subscribe to backend FS changes
		listen('queues-changed', () => {
			// debounce via microtask; cheap and keeps UI responsive
			queueMicrotask(() => { refreshAllQueues(); });
		}).then((fn) => { unlisten = fn; });

		return () => {
			if (unlisten) {
				unlisten();
			}
		};
	});
</script>

<main class="p-4 md:p-8 max-w-7xl mx-auto space-y-6 bg-gray-100 min-h-screen">
	<div class="text-center">
		<h1 class="text-3xl md:text-4xl font-bold text-gray-800">CartaOS</h1>
		<p class="text-lg text-gray-600">Your Document Processing Pipeline</p>
	</div>

	<div class="flex flex-wrap justify-center gap-4 mb-6 border-b pb-2">
		<button onclick={() => currentView = 'pipeline'} class:font-bold={currentView === 'pipeline'}>Pipeline</button>
		<button onclick={() => currentView = 'lab'} class:font-bold={currentView === 'lab'}>Lab</button>
		<button onclick={() => currentView = 'settings'} class:font-bold={currentView === 'settings'}>Settings</button>
	</div>

	{#if currentView === 'pipeline'}
		<div class="bg-white p-4 rounded-lg shadow-md flex flex-wrap justify-center gap-4 text-center">
			<ActionButton onclick={handleTriage} {isLoading} color="blue" class="w-full sm:w-auto">
				Triage
			</ActionButton>
			<ActionButton onclick={handleOcr} {isLoading} color="green" class="w-full sm:w-auto">
				OCR Batch
			</ActionButton>
			<ActionButton onclick={handleSummarizeBatch} {isLoading} color="amber" class="w-full sm:w-auto">
				Summarization Batch
			</ActionButton>
		</div>

		<div class="bg-white p-4 rounded-lg shadow-md">
			<p class="text-sm text-gray-700 font-mono">{statusMessage}</p>
		</div>

		<LogPanel />

		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
			<QueueColumn title="📂 Triage" files={triageFiles} />
			<QueueColumn title="🔧 Correction Lab" files={labFiles}>
				{#snippet children({ file })}
					<span class="text-gray-800 break-all pr-2">{file}</span>
					<div class="flex-shrink-0 space-x-1">
						<button
							onclick={() => handleCorrect(file)}
							class="px-2 py-1 text-xs font-semibold text-white bg-blue-500 rounded hover:bg-blue-600"
							title="Correct in ScanTailor"
						>
							Correct
						</button>
						<button
							onclick={() => handleFinalize(file)}
							class="px-2 py-1 text-xs font-semibold text-white bg-green-500 rounded hover:bg-green-600"
							title="Mark as done and move to OCR"
						>
							Finalized
						</button>
					</div>
				{/snippet}
			</QueueColumn>
			<QueueColumn title="📄 Ready for OCR" files={ocrFiles} />
			<QueueColumn title="📝 Summarize" files={summaryFiles}>
				{#snippet children({ file })}
					<span class="text-gray-800 break-all pr-2">{file}</span>
					<div class="flex-shrink-0 space-x-1">
						<button
							onclick={() => handleSummarizeSingle(file)}
							class="px-2 py-1 text-xs font-semibold text-white bg-amber-500 rounded hover:bg-amber-600"
							title="Summarize this file"
						>
							Summarize
						</button>
					</div>
				{/snippet}
			</QueueColumn>
		</div>
	{:else if currentView === 'lab'}
		<LabView />
	{:else if currentView === 'settings'}
		<SettingsView />
	{/if}
</main>
