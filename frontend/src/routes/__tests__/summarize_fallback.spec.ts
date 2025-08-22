import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import Page from '../+page.svelte';
import type { Mock } from 'vitest';

vi.mock('$lib/ipc', async () => ({
	summarizeJson: vi.fn(async () => {
		throw new Error('no-json');
	})
}));

vi.mock('@tauri-apps/api/core', async (importOriginal) => {
	const actual = (await importOriginal()) as typeof import('@tauri-apps/api/core');
	return {
		...actual,
		invoke: vi.fn(async (cmd: string, args?: Record<string, unknown>) => {
			if (cmd === 'get_files_in_stage') {
				const stage = args?.stage as string | undefined;
				if (stage === '02_Triage') return [];
				if (stage === '03_Lab') return [];
				if (stage === '04_ReadyForOCR') return [];
				if (stage === '05_ReadyForSummary') return ['doc.pdf'];
			}
			if (cmd === 'run_summarize_single') return 'ok';
			return 'ok';
		})
	};
});

import { invoke } from '@tauri-apps/api/core';
const mockInvoke = invoke as unknown as Mock;

describe('Summarize single fallback path', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
	});

	it('shows default completion message when JSON enrichment fails', async () => {
		render(Page);

		await waitFor(() => {
			expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
		});

		const btn = await screen.findByRole('button', { name: 'Summarize' });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent(
				'Summarizing doc.pdf completed successfully.'
			);
		});
	});
});
