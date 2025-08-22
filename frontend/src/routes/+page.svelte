<script lang="ts">
	import { invoke } from '@tauri-apps/api/core';
	import { openFilesDialog } from '$lib/dialog';
	import { onMount } from 'svelte';
	import SettingsView from '$lib/components/SettingsView.svelte';
	import LabView from '$lib/components/LabView.svelte';
	import SummariesView from '$lib/components/SummariesView.svelte';
	import ActionButton from '$lib/components/ActionButton.svelte';
	import QueueColumn from '$lib/components/QueueColumn.svelte';
	import LogPanel from '$lib/components/LogPanel.svelte';
	import { triageJson, ocrJson, type TriageJson, type OcrJson } from '$lib/ipc';

	// --- State ---
	let currentView: 'pipeline' | 'lab' | 'settings' | 'summaries' = $state('pipeline');
	let statusMessage = $state('Waiting for action...');
	let isLoading = $state(false);
	let triageFiles = $state<string[]>([]);
	let labFiles = $state<string[]>([]);
	let ocrFiles = $state<string[]>([]);
	let summaryFiles = $state<string[]>([]);

	// --- Action Logic ---
	async function withLoading<T>(action: () => Promise<T>, baseMessage: string): Promise<void> {
		statusMessage = `Running ${baseMessage}...`;
		isLoading = true;
		try {
			let finalMessage: string | undefined;
			const result = await action();
			if (typeof result === 'string' && result.trim()) {
				finalMessage = result.trim();
				statusMessage = finalMessage;
			} else {
				finalMessage = `${baseMessage} completed successfully.`;
				statusMessage = finalMessage;
			}
			await refreshAllQueues();
			// Preserve enriched message after refresh
			if (finalMessage) statusMessage = finalMessage;
		} catch (error) {
			console.error('Caught error in withLoading:', error);
			const errorMessage =
				typeof error === 'string'
					? error
					: error instanceof Error
						? error.message
						: `An unknown error occurred during ${baseMessage}.`;
			statusMessage = `ERROR in ${baseMessage}: ${errorMessage}`;
			console.error(statusMessage, error);
		} finally {
			isLoading = false;
		}
	}

	const handleTriage = () =>
		withLoading(async () => {
			// Keep legacy command for compatibility/tests
			await invoke('run_triage');
			// Then fetch JSON summary for a richer status
			try {
				const t: TriageJson = await triageJson();
				if (t.status === 'success' && t.data?.counts) {
					return `Triage: ${t.data.counts.triage} files in triage`;
				}
			} catch {
				// Best-effort enrichment only; ignore when not available (e.g., unit tests)
				void 0;
			}
			return 'Triage completed successfully.';
		}, 'Triage');

	const handleOcr = () =>
		withLoading(async () => {
			await invoke('run_ocr_batch');
			try {
				const o: OcrJson = await ocrJson();
				if (o.status === 'success') {
					const q = o.data?.counts?.queued ?? o.data?.queued_for_ocr?.length ?? 0;
					return `OCR Batch: ${q} files queued`;
				}
			} catch {
				// Best-effort enrichment only
				void 0;
			}
			return 'OCR Batch completed successfully.';
		}, 'OCR Batch');

	const handleImportToTriage = () =>
		withLoading(async () => {
			const selection = await openFilesDialog({ multiple: true, title: 'Select files to import' });
			let paths: string[] = [];
			if (Array.isArray(selection)) paths = selection as string[];
			else if (typeof selection === 'string') paths = [selection];
			return await importToTriageWithPaths(paths);
		}, 'Import to Triage');

	async function importToTriageWithPaths(paths: string[]): Promise<string> {
		if (!paths || paths.length === 0) {
			return 'No files selected.';
		}
		await invoke('import_to_triage', { paths });
		return `Imported ${paths.length} file(s) to triage.`;
	}

	function extractPathsFromDataTransfer(dt: DataTransfer | null): string[] {
		if (!dt) return [];
		const files: string[] = [];
		for (let i = 0; i < dt.files.length; i++) {
			const f = dt.files.item(i) as File & { path?: string };
			if (!f) continue;
			const p = (f as unknown as { path?: string }).path ?? f.name;
			if (p) files.push(p);
		}
		return files;
	}

	const handleDropToTriage = (event: DragEvent) => {
		event.preventDefault();
		const paths = extractPathsFromDataTransfer(event.dataTransfer);
		void withLoading(() => importToTriageWithPaths(paths), 'Import to Triage');
	};
	const handleSummarizeBatch = () =>
		withLoading(async () => {
			await invoke('run_summarize_batch');
			try {
				const files: string[] = await invoke('get_files_in_stage', { stage: '05_ReadyForSummary' });
				return `Summarization Batch: ${files.length} files ready`;
			} catch {
				// Best-effort enrichment only
				void 0;
			}
			return 'Summarization Batch completed successfully.';
		}, 'Summarization Batch');
	const handleSummarizeSingle = (fileName: string) =>
		withLoading(async () => {
			await invoke('run_summarize_single', {
				fileName,
				dryRun: false,
				debug: false,
				forceOcr: false
			});
			try {
				// Best-effort enrichment via JSON endpoint
				const res = await import('$lib/ipc').then((m) =>
					m.summarizeJson(fileName, { dry_run: false, debug: false, force_ocr: false })
				);
				if (res.status === 'success' && res.data?.target_file) {
					return `Summarize: ${res.data.target_file} acknowledged`;
				}
			} catch {
				void 0;
			}
			return `Summarizing ${fileName} completed successfully.`;
		}, `Summarizing ${fileName}`);

	const handleOcrSingle = (fileName: string) =>
		withLoading(async () => {
			await invoke('run_ocr_single', { fileName });
			try {
				const o: OcrJson = await ocrJson();
				if (o.status === 'success') {
					const q = o.data?.counts?.queued ?? o.data?.queued_for_ocr?.length ?? 0;
					return `OCR Batch: ${q} files queued`;
				}
			} catch {
				void 0;
			}
			return `OCR for ${fileName} completed successfully.`;
		}, `OCR for ${fileName}`);
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
			console.error('Caught error in refreshAllQueues:', error);
			const errorMessage =
				typeof error === 'string'
					? error
					: error instanceof Error
						? error.message
						: 'An unknown error occurred while refreshing queues.';
			statusMessage = `ERROR refreshing queues: ${errorMessage}`;
			console.error(statusMessage, error);
		} finally {
			isLoading = false;
		}
	}

	// Initial load + auto-refresh polling
	onMount(() => {
		// initial refresh
		void refreshAllQueues();
		// simple polling every 2s; can be replaced with Tauri FS watcher later
		const id = window.setInterval(() => {
			// avoid overlapping runs
			if (!isLoading) void refreshAllQueues();
		}, 2000);
		return () => {
			clearInterval(id);
		};
	});
</script>

<main class="mx-auto min-h-screen max-w-7xl space-y-6 bg-gray-100 p-8">
	<div class="text-center">
		<h1 class="text-4xl font-bold text-gray-800">CartaOS</h1>
		<p class="text-lg text-gray-600">Your Document Processing Pipeline</p>
	</div>

	<div class="mb-6 flex justify-center space-x-4 border-b pb-2">
		<button onclick={() => (currentView = 'pipeline')} class:font-bold={currentView === 'pipeline'}
			>Pipeline</button
		>
		<button onclick={() => (currentView = 'lab')} class:font-bold={currentView === 'lab'}
			>Lab</button
		>
		<button
			onclick={() => (currentView = 'summaries')}
			class:font-bold={currentView === 'summaries'}>Summaries</button
		>
		<button onclick={() => (currentView = 'settings')} class:font-bold={currentView === 'settings'}
			>Settings</button
		>
	</div>

	{#if currentView === 'pipeline'}
		<div class="space-x-4 rounded-lg bg-white p-4 text-center shadow-md">
			<ActionButton onclick={handleTriage} {isLoading} color="blue">Triage</ActionButton>
			<ActionButton onclick={handleOcr} {isLoading} color="green">OCR Batch</ActionButton>
			<ActionButton onclick={handleSummarizeBatch} {isLoading} color="amber">
				Summarize Batch
			</ActionButton>
			<ActionButton onclick={handleImportToTriage} {isLoading} color="purple">
				Import to Triage
			</ActionButton>
		</div>

		<div
			role="region"
			aria-label="Drop files to import"
			ondragover={(e) => e.preventDefault()}
			ondrop={handleDropToTriage}
			class="rounded-lg border-2 border-dashed border-gray-300 bg-white p-6 text-center text-gray-700 shadow-sm"
		>
			Drop files to import
		</div>

		<div class="rounded-lg bg-white p-4 shadow-md">
			<p
				role="status"
				aria-live="polite"
				aria-atomic="true"
				class="font-mono text-sm text-gray-700"
			>
				{statusMessage}
			</p>
		</div>

		<LogPanel />

		<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-4">
			<QueueColumn title="📂 Triage" files={triageFiles} />
			<QueueColumn title="🔧 Correction Lab" files={labFiles}>
				{#snippet children({ file }: { file: string })}
					<span class="break-all pr-2 text-gray-800">{file}</span>
					<div class="flex-shrink-0 space-x-1">
						<button
							onclick={() => handleCorrect(file)}
							class="rounded bg-blue-500 px-2 py-1 text-xs font-semibold text-white hover:bg-blue-600"
							title="Correct in ScanTailor"
						>
							Correct
						</button>
						<button
							onclick={() => handleFinalize(file)}
							class="rounded bg-green-500 px-2 py-1 text-xs font-semibold text-white hover:bg-green-600"
							title="Mark as done and move to OCR"
						>
							Finalized
						</button>
					</div>
				{/snippet}
			</QueueColumn>
			<QueueColumn title="📄 Ready for OCR" files={ocrFiles}>
				{#snippet children({ file }: { file: string })}
					<span class="break-all pr-2 text-gray-800">{file}</span>
					<div class="flex-shrink-0 space-x-1">
						<button
							onclick={() => handleOcrSingle(file)}
							class="rounded bg-green-500 px-2 py-1 text-xs font-semibold text-white hover:bg-green-600 disabled:opacity-50"
							disabled={isLoading}
							title="OCR this file"
							aria-label={`OCR ${file}`}
						>
							OCR {file}
						</button>
					</div>
				{/snippet}
			</QueueColumn>
			<QueueColumn title="📝 Summarization" files={summaryFiles}>
				{#snippet children({ file }: { file: string })}
					<span class="break-all pr-2 text-gray-800">{file}</span>
					<div class="flex-shrink-0 space-x-1">
						<button
							onclick={() => handleSummarizeSingle(file)}
							class="rounded bg-amber-500 px-2 py-1 text-xs font-semibold text-white hover:bg-amber-600"
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
	{:else if currentView === 'summaries'}
		<SummariesView />
	{:else if currentView === 'settings'}
		<SettingsView />
	{/if}
</main>
