<script lang="ts">
	import ActionButton from '../ActionButton.svelte';
	let submits = $state(0);
	function onSubmit(e: SubmitEvent) {
		e.preventDefault();
		submits += 1;
	}
</script>

<form onsubmit={onSubmit} aria-label="test-form">
	<ActionButton
		onclick={() => {
			/* no-op */
		}}
		label="Click Me"
	/>
</form>

<p data-testid="submit-count">{submits}</p>
