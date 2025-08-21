<script lang="ts">
  import { onMount } from 'svelte';
  import { invoke } from '@tauri-apps/api/core';

  let statusMessage = $state('Waiting for action...');
  let isLoading = $state(false);
  let labFiles = $state<string[]>([]);

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
      await refresh();
    } catch (error) {
      const msg = typeof error === 'string' ? error : (error instanceof Error ? error.message : `unknown error in ${baseMessage}`);
      statusMessage = `ERROR in ${baseMessage}: ${msg}`;
      console.error(statusMessage, error);
    } finally {
      isLoading = false;
    }
  }

  async function refresh() {
    statusMessage = 'Refreshing lab files...';
    isLoading = true;
    try {
      const result = await invoke<string[] | undefined>('get_files_in_stage', { stage: '03_Lab' });
      labFiles = Array.isArray(result) ? result : [];
      statusMessage = 'Lab files refreshed successfully.';
    } catch (error) {
      const msg = typeof error === 'string' ? error : (error instanceof Error ? error.message : 'unknown error refreshing lab');
      statusMessage = `ERROR refreshing lab files: ${msg}`;
      console.error(statusMessage, error);
    } finally {
      isLoading = false;
    }
  }

  const handleCorrect = (fileName: string) => withLoading(() => invoke('open_scantailor', { fileName }), `Opening ScanTailor for ${fileName}`);
  const handleFinalize = (fileName: string) => withLoading(() => invoke('finalize_lab_file', { fileName }), `Finalizing ${fileName}`);

  onMount(refresh);
</script>

<div class="lab-view">
  <h2>Laboratório (03_Lab)</h2>
  <p>Aqui você verá os arquivos que precisam de correção manual no ScanTailor.</p>

  <div class="controls">
    <button onclick={refresh} aria-busy={isLoading} class="refresh">Refresh Lab Files</button>
  </div>

  <div class="status">
    <p class="mono">{statusMessage}</p>
  </div>

  <ul class="files">
    {#if labFiles.length === 0}
      <li class="empty">Empty</li>
    {:else}
      {#each labFiles as file (file)}
        <li class="row">
          <span class="name">{file}</span>
          <div class="actions">
            <button onclick={() => handleCorrect(file)} title="Correct in ScanTailor">Correct</button>
            <button onclick={() => handleFinalize(file)} title="Mark as done and move to OCR">Finalized</button>
          </div>
        </li>
      {/each}
    {/if}
  </ul>
</div>

<style>
  .lab-view {
    padding: 1rem;
    background-color: #f0f0f0;
    border-radius: 8px;
  }
  .controls { margin: 0.5rem 0; }
  .mono { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
  .files { margin-top: 0.5rem; }
  .row { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.25rem 0; }
  .name { word-break: break-all; }
  .actions button { margin-left: 0.25rem; }
</style>
