import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import Page from '../+page.svelte';

const mockInvoke = invoke as unknown as Mock;

function deferred<T>() {
	let resolve!: (v: T | PromiseLike<T>) => void;
	let reject!: (r?: unknown) => void;
	const promise = new Promise<T>((res, rej) => {
		resolve = res;
		reject = rej;
	});
	return { promise, resolve, reject };
}

describe('Pipeline view loading/robustness', () => {
	beforeEach(() => {
		mockInvoke.mockReset();
	});

	it('disables action buttons while an operation is running and re-enables after', async () => {
		const d = deferred<string>();
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'run_ocr_batch') return d.promise; // pending until we resolve
			if (cmd === 'run_ocr_json') {
				return JSON.stringify({ status: 'success', data: { counts: { queued: 0 } } });
			}
			if (cmd === 'get_files_in_stage') return [];
			return undefined;
		});

		render(Page);

		await waitFor(() => {
			expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
		});

		const triageBtn = screen.getByRole('button', { name: 'Triage' });
		const ocrBtn = screen.getByRole('button', { name: 'OCR Batch' });
		const summarizeBtn = screen.getByRole('button', { name: 'Summarize Batch' });

		await fireEvent.click(ocrBtn);

		// While pending, all buttons should be disabled
		expect(triageBtn).toBeDisabled();
		expect(ocrBtn).toBeDisabled();
		expect(summarizeBtn).toBeDisabled();

		// Resolve operation
		d.resolve('ok');

		await waitFor(() => {
			expect(triageBtn).not.toBeDisabled();
			expect(ocrBtn).not.toBeDisabled();
			expect(summarizeBtn).not.toBeDisabled();
		});
	});

	it('allows retry after OCR error and shows success on second attempt', async () => {
		let call = 0;
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'run_ocr_batch') {
				call += 1;
				if (call === 1) throw new Error('first-fail');
				return 'ok';
			}
			if (cmd === 'run_ocr_json') {
				return JSON.stringify({ status: 'success', data: { counts: { queued: 2 } } });
			}
			if (cmd === 'get_files_in_stage') return [];
			return undefined;
		});

		render(Page);

		await waitFor(() => {
			expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
		});

		const ocrBtn = screen.getByRole('button', { name: 'OCR Batch' });

		// First attempt fails
		await fireEvent.click(ocrBtn);
		await waitFor(() => {
			const status = screen.getByRole('status');
			expect(status).toHaveTextContent(/ERROR in OCR Batch:/);
			expect(status).toHaveTextContent('first-fail');
		});

		// Second attempt succeeds and shows enriched message
		await fireEvent.click(ocrBtn);
		await waitFor(() => {
			expect(screen.getByText('OCR Batch: 2 files queued')).toBeInTheDocument();
		});
	});
});
