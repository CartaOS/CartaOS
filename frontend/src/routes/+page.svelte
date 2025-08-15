<script>
    import { invoke } from '@tauri-apps/api/core';

    let statusMessage = 'Aguardando uma ação...';
    let labFiles = [];

    // Função para chamar o comando 'run_triage'
    async function handleTriage() {
        statusMessage = 'Executando Triage...';
        labFiles = []; // Limpa a lista de arquivos de outras execuções
        try {
            const result = await invoke('run_triage');
            statusMessage = result || 'Triage concluído com sucesso (sem saída no console).';
            console.log('Triage Success:', result);
        } catch (error) {
            statusMessage = 'ERRO no Triage: ' + error;
            console.error('Triage Error:', error);
        }
    }

    // Função para chamar o comando 'run_ocr_batch'
    async function handleOcr() {
        statusMessage = 'Executando OCR em lote...';
        labFiles = [];
        try {
            const result = await invoke('run_ocr_batch');
            statusMessage = result || 'OCR concluído com sucesso (sem saída no console).';
            console.log('OCR Success:', result);
        } catch (error) {
            statusMessage = 'ERRO no OCR: ' + error;
            console.error('OCR Error:', error);
        }
    }

    // Função para chamar o comando 'get_files_in_stage'
    async function listLabFiles() {
        statusMessage = 'Buscando arquivos no Lab...';
        labFiles = [];
        try {
            // Passamos o nome da pasta como um argumento para a função Rust
            const files = await invoke('get_files_in_stage', { stage: '03_Lab' });
            labFiles = files;
            statusMessage = `Encontrados ${files.length} arquivos no diretório 03_Lab.`;
            console.log('Lab Files:', files);
        } catch (error) {
            statusMessage = 'ERRO ao listar arquivos do Lab: ' + error;
            console.error('List Files Error:', error);
        }
    }
</script>

<main class="p-8 max-w-4xl mx-auto space-y-6 bg-gray-50 min-h-screen">
    <div class="text-center">
        <h1 class="text-3xl font-bold text-gray-800">Painel de Controle - CartaOS</h1>
        <p class="text-gray-600">Interface de teste para validar a comunicação Backend ↔ Frontend</p>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-md space-x-4 text-center">
        <button on:click={handleTriage} class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700 transition-colors">
            Executar Triage
        </button>
        <button on:click={handleOcr} class="bg-green-500 text-white font-bold py-2 px-4 rounded hover:bg-green-700 transition-colors">
            Executar OCR
        </button>
        <button on:click={listLabFiles} class="bg-purple-500 text-white font-bold py-2 px-4 rounded hover:bg-purple-700 transition-colors">
            Listar Arquivos no Lab
        </button>
    </div>

    <div class="bg-white p-4 rounded-lg shadow-md">
        <h2 class="text-lg font-semibold text-gray-700 border-b pb-2">Status / Log</h2>
        <pre class="bg-gray-800 text-white p-4 rounded mt-2 whitespace-pre-wrap text-sm">{statusMessage}</pre>
    </div>

    {#if labFiles.length > 0}
        <div class="bg-white p-4 rounded-lg shadow-md">
            <h2 class="text-lg font-semibold text-gray-700 border-b pb-2">Arquivos no "03_Lab"</h2>
            <ul class="list-disc list-inside mt-2 space-y-1">
                {#each labFiles as file}
                    <li class="text-gray-800">{file}</li>
                {/each}
            </ul>
        </div>
    {/if}
</main>