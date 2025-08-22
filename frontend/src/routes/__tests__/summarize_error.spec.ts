import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import Page from '../+page.svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';

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
			if (cmd === 'run_summarize_batch') throw new Error('batch-fail');
			if (cmd === 'run_summarize_single') throw new Error('single-fail');
			return undefined;
		})
	};
});

const mockInvoke = invoke as unknown as Mock;

describe('Summarization error paths', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
	});

	it('shows error message when summarize batch fails', async () => {
		render(Page);

		const batchBtn = await screen.findByRole('button', { name: /summarize batch/i });
		await fireEvent.click(batchBtn);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent(
				'ERROR in Summarization Batch: batch-fail'
			);
		});
	});

	it('shows error message when summarize single fails', async () => {
		render(Page);

		// Wait for queues to populate
		await waitFor(() => {
			expect(screen.getByText('doc.pdf')).toBeInTheDocument();
		});

		const btn = await screen.findByRole('button', { name: 'Summarize' });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent(
				'ERROR in Summarizing doc.pdf: single-fail'
			);
		});
	});
});
