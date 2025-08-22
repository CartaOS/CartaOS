import { render, screen, fireEvent, waitFor, within } from '@testing-library/svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import LabView from '../LabView.svelte';

const mockInvoke = invoke as unknown as Mock;

describe('LabView interactions', () => {
	beforeEach(() => {
		mockInvoke.mockReset();
	});

	it('loads lab files on mount and refresh updates list', async () => {
		let toggle = 0;
		mockInvoke.mockImplementation(async (cmd: string, args?: { stage?: string }) => {
			if (cmd === 'get_files_in_stage') {
				const stage = args?.stage as string;
				if (stage === '03_Lab') return toggle === 0 ? ['a.tif'] : ['a.tif', 'b.tif'];
			}
			return undefined;
		});

		render(LabView);

		// Trigger explicit refresh to avoid onMount timing flakiness
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh Lab Files' }));

		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		const list = screen.getByRole('list');
		expect(within(list).getByText('a.tif')).toBeInTheDocument();

		toggle = 1;
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh Lab Files' }));

		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		expect(within(list).getByText('b.tif')).toBeInTheDocument();
	});

	it('Correct opens ScanTailor and refreshes', async () => {
		mockInvoke.mockImplementation(
			async (cmd: string, args?: { stage?: string; fileName?: string }) => {
				if (cmd === 'get_files_in_stage') {
					if (args?.stage === '03_Lab') return ['docX.tif'];
				}
				if (cmd === 'open_scantailor') {
					expect(args?.fileName).toBe('docX.tif');
					return 'Opened';
				}
				return undefined;
			}
		);

		render(LabView);

		// Trigger explicit refresh to ensure initial data is loaded
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh Lab Files' }));
		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		const correctBtn = screen.getByRole('button', { name: 'Correct' });
		await fireEvent.click(correctBtn);

		// Expect final state to be refresh success
		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		// Ensure command was invoked
		expect(mockInvoke).toHaveBeenCalledWith('open_scantailor', { fileName: 'docX.tif' });
	});

	it('Finalized moves file out of lab (refresh shows empty)', async () => {
		let lab: string[] = ['done1.tif'];
		mockInvoke.mockImplementation(
			async (cmd: string, args?: { stage?: string; fileName?: string }) => {
				if (cmd === 'get_files_in_stage') {
					if (args?.stage === '03_Lab') return lab;
				}
				if (cmd === 'finalize_lab_file') {
					lab = lab.filter((f) => f !== (args?.fileName as string));
					return 'Finalized';
				}
				return undefined;
			}
		);

		render(LabView);

		// Trigger explicit refresh to ensure initial data is loaded
		await fireEvent.click(screen.getByRole('button', { name: 'Refresh Lab Files' }));
		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		const finalizeBtn = screen.getByRole('button', { name: 'Finalized' });
		await fireEvent.click(finalizeBtn);

		await waitFor(() => {
			expect(screen.getByText('Lab files refreshed successfully.')).toBeInTheDocument();
		});

		const list = screen.getByRole('list');
		expect(within(list).getByText('Empty')).toBeInTheDocument();
		expect(mockInvoke).toHaveBeenCalledWith('finalize_lab_file', { fileName: 'done1.tif' });
	});
});
