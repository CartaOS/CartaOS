import { render, screen, waitFor } from '@testing-library/svelte';
import Page from '../+page.svelte';
import { invoke } from '@tauri-apps/api/core';
import type { Mock } from 'vitest';
import { makeInvokeMock, withQueues } from '../../test/utils/tauriMock';

const mockInvoke = invoke as unknown as Mock;

describe('Testing utils: makeInvokeMock + withQueues', () => {
	beforeEach(() => {
		mockInvoke.mockReset?.();
	});

	it('populates queues via withQueues fixture and shows refresh status', async () => {
		makeInvokeMock({
			get_files_in_stage: withQueues({ triage: ['a.pdf'], lab: ['b.pdf'], ocr: [], summary: [] })
		});

		render(Page);

		await waitFor(() => {
			expect(screen.getByRole('status')).toHaveTextContent('File queues refreshed successfully.');
		});

		expect(screen.getByText('a.pdf')).toBeInTheDocument();
		expect(screen.getByText('b.pdf')).toBeInTheDocument();
	});
});
