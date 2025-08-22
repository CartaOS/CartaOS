import { render } from '@testing-library/svelte';
import { tick } from 'svelte';
import LogPanel from '../LogPanel.svelte';

declare const globalThis: any;

describe('LogPanel clean up', () => {
	it('unlistens on destroy to avoid leaks', async () => {
		const { unmount } = render(LogPanel);
		// Ensure onMount async work (listen) has run
		await tick();

		// Unmount to trigger onDestroy clean up
		unmount();

		const stats = globalThis.__getTauriEventStats();
		expect(stats.unlistenCount['log-message']).toBeGreaterThanOrEqual(1);
	});
});
