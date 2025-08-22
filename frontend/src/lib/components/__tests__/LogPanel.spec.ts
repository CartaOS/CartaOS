import { render, screen } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import LogPanel from '../LogPanel.svelte';

declare const globalThis: any;

describe('LogPanel', () => {
	it('renders and appends logs on tauri event', async () => {
		const { container } = render(LogPanel);

		// Initially no log entries
		expect(container.querySelectorAll('.log-entry').length).toBe(0);

		// Emit a fake event (provided by tests/setup.ts)
		globalThis.__emitTauri('log-message', {
			timestamp: '2025-01-01T00:00:00Z',
			message: 'Hello world'
		});

		// Should render one log entry
		expect(await screen.findByText('Hello world')).toBeInTheDocument();
		expect(screen.getByText('2025-01-01T00:00:00Z')).toBeInTheDocument();

		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});
});
