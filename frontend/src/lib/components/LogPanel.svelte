<script lang="ts">
	import { onMount, onDestroy } from 'svelte';
	import { listen, type Event } from '@tauri-apps/api/event';

	interface LogEntry {
		timestamp: string;
		message: string;
	}

	let logs = $state<LogEntry[]>([]);

	let unlisten: (() => void) | undefined;

	onMount(async () => {
		const un = await listen('log-message', (event: Event<LogEntry>) => {
			logs.push(event.payload);
		});
		unlisten = un;
	});

	onDestroy(() => {
		if (unlisten) unlisten();
	});
</script>

<div class="log-panel">
	<h2>Real-Time Logs</h2>
	<div class="logs-container">
		{#each logs as log, i (i)}
			<div class="log-entry">
				<span class="timestamp">{log.timestamp}</span>
				<span class="message">{log.message}</span>
			</div>
		{/each}
	</div>
</div>

<style>
	.log-panel {
		display: flex;
		flex-direction: column;
		height: 100%;
		border: 1px solid #ccc;
		border-radius: 4px;
	}

	h2 {
		margin: 0;
		padding: 0.5rem;
		border-bottom: 1px solid #ccc;
		background-color: #f7f7f7;
	}

	.logs-container {
		flex-grow: 1;
		overflow-y: auto;
		padding: 0.5rem;
	}

	.log-entry {
		display: flex;
		margin-bottom: 0.25rem;
	}

	.timestamp {
		font-family: monospace;
		margin-right: 1rem;
		color: #888;
	}

	.message {
		font-family: monospace;
	}
</style>
