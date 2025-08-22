import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import Page from '../+page.svelte';

const mockInvoke = invoke as unknown as Mock;

describe('Pipeline view (+page.svelte) - single-file OCR', () => {
	beforeEach(() => {
		mockInvoke.mockReset();
	});

	it('renders OCR button for items in Ready for OCR and runs run_ocr_single on click', async () => {
		mockInvoke.mockImplementation(async (cmd: string, args?: any) => {
			if (cmd === 'get_files_in_stage') {
				const stage = args?.stage;
				if (stage === '02_Triage') return [];
				if (stage === '03_Lab') return [];
				if (stage === '04_ReadyForOCR') return ['doc1.pdf'];
				if (stage === '05_ReadyForSummary') return [];
			}
			if (cmd === 'run_ocr_single') return 'ok';
			if (cmd === 'run_ocr_json') {
				return JSON.stringify({
					status: 'success',
					data: { counts: { queued: 1 }, queued_for_ocr: ['doc1.pdf'] }
				});
			}
			return undefined;
		});

		render(Page);

		// Wait for initial refresh
		await waitFor(() => {
			expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
		});

		// Find the OCR button for doc1.pdf
		const ocrBtn = screen.getByRole('button', { name: /OCR doc1.pdf/ });
		expect(ocrBtn).toBeInTheDocument();

		// Click to trigger single-file OCR
		const clickPromise = fireEvent.click(ocrBtn);
		// Button should be disabled during loading
		expect(ocrBtn).toBeDisabled();
		await clickPromise;

		// Command should be invoked with fileName
		await waitFor(() => {
			expect(mockInvoke).toHaveBeenCalledWith('run_ocr_single', { fileName: 'doc1.pdf' });
		});

		// Ensure enriched status after refresh
		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent(/OCR Batch:/);
			expect(ocrBtn).not.toBeDisabled();
		});
	});
});
