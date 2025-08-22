<script lang="ts">
	import QueueColumn from '../QueueColumn.svelte';
</script>

<QueueColumn title="Queue" files={['x.pdf', 'y.pdf']}>
	{#snippet children({ file }: { file: string })}
		<button>Open {file}</button>
	{/snippet}
</QueueColumn>
