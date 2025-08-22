import { render, screen, waitFor } from '@testing-library/svelte';
import Page from '../+page.svelte';
import { invoke } from '@tauri-apps/api/core';
import type { Mock } from 'vitest';

const mockInvoke = invoke as unknown as Mock;

describe('Pipeline refresh error handling', () => {
	beforeEach(() => {
		mockInvoke.mockReset();
	});

	it('shows error status when refreshAllQueues fails', async () => {
		// Make get_files_in_stage throw to exercise error branch
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'get_files_in_stage') {
				throw new Error('boom');
			}
			return undefined;
		});

		render(Page);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('ERROR refreshing queues:');
			expect(screen.getByRole('status')).toHaveTextContent('boom');
		});
	});

	it('shows error status when refreshAllQueues fails with string error', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'get_files_in_stage') {
				throw 'bad';
			}
			return undefined;
		});

		render(Page);

		await waitFor(() => {
			const status = screen.getByRole('status');
			expect(status).toHaveTextContent('ERROR refreshing queues:');
			expect(status).toHaveTextContent('bad');
		});
	});
});
