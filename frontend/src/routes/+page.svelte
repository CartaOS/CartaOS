<script lang="ts">
	import { invoke } from '@tauri-apps/api/core';
	import { onMount } from 'svelte';

	// --- State ---
	let statusMessage: string = 'Waiting for action...';
	let triageFiles: string[] = [];
	let labFiles: string[] = [];
	let ocrFiles: string[] = [];
	let summaryFiles: string[] = [];

	// --- Funções ---

	// Função unificada para atualizar todas as filas
	async function refreshAllQueues(): Promise<void> {
		statusMessage = 'Refreshing file queues...';
		try {
			// Usamos Promise.all para buscar tudo em paralelo
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

			statusMessage = 'File queues updated successfully.';
		} catch (error) {
			const errorMessage = 'ERROR refreshing queues: ' + (error as Error).message;
			statusMessage = errorMessage;
			console.error(errorMessage);
		}
	}

	async function handleTriage(): Promise<void> {
		statusMessage = 'Running Triage...';
		try {
			const result: string | null = await invoke<string>('run_triage');
			statusMessage = result ?? 'Triage completed successfully.';
			await refreshAllQueues(); // Atualiza as filas após a ação
		} catch (error) {
			statusMessage = 'ERROR in Triage: ' + (error as Error).message;
			console.error('Triage Error:', error);
		}
	}

	async function handleOcr(): Promise<void> {
		statusMessage = 'Running OCR in batch...';
		try {
			const result: string | null = await invoke<string>('run_ocr_batch');
			statusMessage = result ?? 'OCR completed successfully.';
			await refreshAllQueues(); // Atualiza as filas após a ação
		} catch (error) {
			statusMessage = 'ERROR in OCR: ' + (error as Error).message;
			console.error('OCR Error:', error);
		}
	}

	// Carrega os arquivos assim que a página é montada
	onMount(refreshAllQueues);
</script>

<main class="p-8 max-w-7xl mx-auto space-y-6 bg-gray-100 min-h-screen">
	<div class="text-center">
		<h1 class="text-4xl font-bold text-gray-800">CartaOS</h1>
		<p class="text-gray-600 mt-1">Pipeline Control Panel</p>
	</div>

	<div class="bg-white p-4 rounded-lg shadow-md space-x-4 text-center">
		<button
			on:click={handleTriage}
			class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition-colors"
		>
			Run Triage
		</button>
		<button
			on:click={handleOcr}
			class="bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-700 transition-colors"
		>
			Run OCR Batch
		</button>
		<button
			on:click={refreshAllQueues}
			class="bg-purple-500 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition-colors"
		>
			Refresh Queues
		</button>
	</div>

	<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
		<div class="bg-white p-4 rounded-lg shadow-md">
			<h2 class="text-lg font-semibold text-gray-700 border-b pb-2">📂 02_Triage</h2>
			<ul class="list-disc list-inside mt-2 space-y-1 text-sm">
				{#each triageFiles as file (file)}
					<li class="text-gray-800">{file}</li>
				{:else}
					<li class="text-gray-400 italic">Empty</li>
				{/each}
			</ul>
		</div>

		<div class="bg-white p-4 rounded-lg shadow-md">
			<h2 class="text-lg font-semibold text-gray-700 border-b pb-2">🔧 03_Lab</h2>
			<ul class="list-disc list-inside mt-2 space-y-1 text-sm">
				{#each labFiles as file (file)}
					<li class="text-gray-800">{file}</li>
				{:else}
					<li class="text-gray-400 italic">Empty</li>
				{/each}
			</ul>
		</div>

		<div class="bg-white p-4 rounded-lg shadow-md">
			<h2 class="text-lg font-semibold text-gray-700 border-b pb-2">📄 04_ReadyForOCR</h2>
			<ul class="list-disc list-inside mt-2 space-y-1 text-sm">
				{#each ocrFiles as file (file)}
					<li class="text-gray-800">{file}</li>
				{:else}
					<li class="text-gray-400 italic">Empty</li>
				{/each}
			</ul>
		</div>

		<div class="bg-white p-4 rounded-lg shadow-md">
			<h2 class="text-lg font-semibold text-gray-700 border-b pb-2">📝 05_ReadyForSummary</h2>
			<ul class="list-disc list-inside mt-2 space-y-1 text-sm">
				{#each summaryFiles as file (file)}
					<li class="text-gray-800">{file}</li>
				{:else}
					<li class="text-gray-400 italic">Empty</li>
				{/each}
			</ul>
		</div>
	</div>

	<div class="bg-white p-4 rounded-lg shadow-md">
		<h2 class="text-lg font-semibold text-gray-700 border-b pb-2">Status / Log</h2>
		<pre
			class="bg-gray-800 text-white p-4 rounded mt-2 whitespace-pre-wrap text-sm min-h-[50px]"
		>{statusMessage}</pre>
	</div>
</main>