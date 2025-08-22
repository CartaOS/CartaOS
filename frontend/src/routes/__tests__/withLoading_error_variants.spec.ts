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
				if (stage === '05_ReadyForSummary') return [];
			}
			return undefined;
		})
	};
});

const mockInvoke = invoke as unknown as Mock;

describe('withLoading error variants', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
	});

	it('shows string error message for summarize batch', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'run_summarize_batch') throw 'oops';
			return undefined;
		});

		render(Page);
		const btn = await screen.findByRole('button', { name: /summarize batch/i });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('ERROR in Summarization Batch: oops');
		});
	});

	it('shows unknown error message for summarize batch when non-Error object thrown', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'run_summarize_batch') throw { foo: 'bar' };
			return undefined;
		});

		render(Page);
		const btn = await screen.findByRole('button', { name: /summarize batch/i });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent(
				'ERROR in Summarization Batch: An unknown error occurred during Summarization Batch.'
			);
		});
	});
});
