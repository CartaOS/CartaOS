import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import Page from '../+page.svelte';
import { invoke } from '@tauri-apps/api/core';
import type { Mock } from 'vitest';

const mockInvoke = invoke as unknown as Mock;

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

describe('Upload DnD to triage', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
	});

	function makeDataTransfer(files: File[]): any {
		const arr = files.slice();
		return {
			files: {
				length: arr.length,
				item: (i: number) => arr[i] ?? null
			}
		} as const;
	}

	it('invokes import_to_triage with dropped file paths and shows success status', async () => {
		render(Page);

		const dropzone = await screen.findByRole('region', { name: /drop files to import/i });

		const f1 = new File(['a'], 'a.pdf');
		const f2 = new File(['b'], 'b.pdf');
		(f1 as any).path = '/tmp/a.pdf';
		(f2 as any).path = '/tmp/b.pdf';

		const dt = makeDataTransfer([f1, f2]);

		await fireEvent.drop(dropzone, { dataTransfer: dt });

		await waitFor(() => {
			expect(mockInvoke).toHaveBeenCalledWith('import_to_triage', {
				paths: ['/tmp/a.pdf', '/tmp/b.pdf']
			});
			expect(screen.getByRole('status')).toHaveTextContent('Imported 2 file(s) to triage.');
		});
	});

	it('shows no-selection message when dropping empty items', async () => {
		render(Page);
		const dropzone = await screen.findByRole('region', { name: /drop files to import/i });

		const dt = { files: { length: 0, item: () => null } } as any;
		await fireEvent.drop(dropzone, { dataTransfer: dt });

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('No files selected.');
		});
	});

	it('shows error status when import_to_triage fails during drop', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'get_files_in_stage') return [];
			if (cmd === 'import_to_triage') throw new Error('copy failed');
			return undefined;
		});

		render(Page);
		const dropzone = await screen.findByRole('region', { name: /drop files to import/i });
		const f = new File(['x'], 'x.pdf') as any;
		f.path = '/tmp/x.pdf';
		const dt = makeDataTransfer([f]);
		await fireEvent.drop(dropzone, { dataTransfer: dt });

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('ERROR in Import to Triage:');
			expect(screen.getByRole('status')).toHaveTextContent('copy failed');
		});
	});

	it('falls back to file names when no path property is available', async () => {
		mockInvoke.mockImplementation(async (cmd: string, args?: any) => {
			if (cmd === 'get_files_in_stage') return [];
			if (cmd === 'import_to_triage') {
				expect(args).toEqual({ paths: ['y.pdf', 'z.pdf'] });
			}
			return undefined;
		});

		render(Page);
		const dropzone = await screen.findByRole('region', { name: /drop files to import/i });
		const f1 = new File(['y'], 'y.pdf');
		const f2 = new File(['z'], 'z.pdf');
		const dt = makeDataTransfer([f1, f2]);
		await fireEvent.drop(dropzone, { dataTransfer: dt });

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('Imported 2 file(s) to triage.');
		});
	});
});
