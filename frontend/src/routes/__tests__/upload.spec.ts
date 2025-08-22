import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import Page from '../+page.svelte';
import type { Mock } from 'vitest';

vi.mock('$lib/dialog', async () => ({
	openFilesDialog: vi.fn(async () => ['/tmp/a.pdf', '/tmp/b.pdf'])
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
				if (stage === '05_ReadyForSummary') return [];
			}
			return 'ok';
		})
	};
});

import { invoke } from '@tauri-apps/api/core';
import { openFilesDialog } from '$lib/dialog';
const mockInvoke = invoke as unknown as Mock;
const mockOpen = openFilesDialog as unknown as Mock;

describe('Upload/import into 02_Triage', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
		mockOpen.mockClear();
	});

	it('clicking Import to Triage opens file dialog and invokes import_to_triage with selected paths', async () => {
		render(Page);

		await waitFor(() => {
			expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
		});

		const btn = screen.getByRole('button', { name: /import to triage/i });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(mockOpen).toHaveBeenCalled();
			expect(mockInvoke).toHaveBeenCalledWith('import_to_triage', {
				paths: ['/tmp/a.pdf', '/tmp/b.pdf']
			});
			expect(screen.getByRole('status')).toHaveTextContent('Imported 2 file(s) to triage.');
		});
	});

	it('disables Import button during loading', async () => {
		mockOpen.mockImplementationOnce(async () => {
			// Simulate a short delay to observe disabled state
			await new Promise((r) => setTimeout(r, 10));
			return ['/tmp/a.pdf'];
		});

		render(Page);
		const btn = await screen.findByRole('button', { name: /import to triage/i });

		const clickPromise = fireEvent.click(btn);
		expect(btn).toBeDisabled();
		await clickPromise;

		await waitFor(() => {
			expect(btn).not.toBeDisabled();
		});
	});

	it('shows status when no files are selected and does not invoke import', async () => {
		mockOpen.mockResolvedValueOnce(null);

		render(Page);

		const btn = await screen.findByRole('button', { name: /import to triage/i });
		await fireEvent.click(btn);

		await waitFor(() => {
			expect(mockInvoke).not.toHaveBeenCalledWith('import_to_triage', expect.anything());
			expect(screen.getByRole('status')).toHaveTextContent('No files selected.');
		});
	});
});
