<script lang="ts">
    import { invoke } from '@tauri-apps/api/core';

    // Status message and list of files in the '03_Lab' directory
    let statusMessage: string = 'Waiting for action...';
    let labFiles: string[] = [];

    // Function to call the 'run_triage' command
    async function handleTriage(): Promise<void> {
        statusMessage = 'Running Triage...';
        labFiles = []; // Clear list of files from previous executions
        try {
            const result: string | null = await invoke<string>('run_triage');
            statusMessage = result ?? 'Triage completed successfully (no console output).';
            console.log('Triage Success:', result);
        } catch (error) {
            statusMessage = 'ERROR in Triage: ' + (error as Error).message;
            console.error('Triage Error:', error);
        }
    }

    // Function to call the 'run_ocr_batch' command
    async function handleOcr(): Promise<void> {
        statusMessage = 'Running OCR in batch...';
        labFiles = [];
        try {
            const result: string | null = await invoke<string>('run_ocr_batch');
            statusMessage = result ?? 'OCR completed successfully (no console output).';
            console.log('OCR Success:', result);
        } catch (error) {
            statusMessage = 'ERROR in OCR: ' + (error as Error).message;
            console.error('OCR Error:', error);
        }
    }

    // Function to call the 'get_files_in_stage' command
    async function listLabFiles(): Promise<void> {
        statusMessage = 'Searching for files in Lab...';
        labFiles = [];
        try {
            // Pass the folder name as an argument to the Rust function
            const files: string[] = await invoke<string[]>('get_files_in_stage', { stage: '03_Lab' });
            labFiles = files;
            statusMessage = `Found ${files.length} files in the "03_Lab" directory.`;
            console.log('Lab Files:', files);
        } catch (error) {
            statusMessage = 'ERROR while listing Lab files: ' + (error as Error).message;
            console.error('List Files Error:', error);
        }
    }
</script>

<main class="p-8 max-w-4xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-800">Control Panel - CartaOS</h1>
        <p class="text-gray-600">Test interface to validate Backend ↔ Frontend communication</p>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-md space-x-4 text-center">
        <button on:click={handleTriage} class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition-colors">
            Run Triage
        </button>
        <button on:click={handleOcr} class="bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-700 transition-colors">
            Run OCR
        </button>
        <button on:click={listLabFiles} class="bg-purple-500 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition-colors">
            List Files in Lab
        </button>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-md">
        <h2 class="text-lg font-semibold text-gray-700 border-b pb-2">Status / Log</h2>
        <pre class="bg-gray-800 text-white p-4 rounded mt-2 whitespace-pre-wrap text-sm">{statusMessage}</pre>
    </div>

    {#if labFiles.length > 0}
        <div class="bg-white p-4 rounded-lg shadow-md">
            <h2 class="text-lg font-semibold text-gray-700 border-b pb-2">Files in "03_Lab"</h2>
            <ul class="list-disc list-inside mt-2 space-y-1">
                {#each labFiles as file (file)}
                    <li class="text-gray-800">{file}</li>
                {/each}
            </ul>
        </div>
    {/if}
</main>

