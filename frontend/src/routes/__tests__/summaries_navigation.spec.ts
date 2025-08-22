import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import Page from '../+page.svelte';
import { invoke } from '@tauri-apps/api/core';
import type { Mock } from 'vitest';

const mockInvoke = invoke as unknown as Mock;

vi.mock('@tauri-apps/api/core', async (importOriginal) => {
	const actual = (await importOriginal()) as typeof import('@tauri-apps/api/core');
	return {
		...actual,
		invoke: vi.fn()
	};
});

describe('Summaries Navigation', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'get_files_in_stage') return [];
			if (cmd === 'list_summaries')
				return [{ name: 'doc1.md', path: '/summaries/doc1.md', modified: '2024-01-01' }];
			if (cmd === 'get_vault_path') return null;
			return undefined;
		});
	});

	it('shows summaries tab and can navigate to summaries view', async () => {
		render(Page);

		// Should have a Summaries navigation button
		const summariesTab = screen.getByRole('button', { name: /summaries/i });
		expect(summariesTab).toBeInTheDocument();

		// Click to navigate to summaries view
		await fireEvent.click(summariesTab);

		// Should show the summaries view content
		await waitFor(() => {
			expect(screen.getByRole('heading', { name: /summaries/i })).toBeInTheDocument();
			expect(screen.getByText('doc1.md')).toBeInTheDocument();
		});
	});

	it('highlights active summaries tab when selected', async () => {
		render(Page);

		const summariesTab = screen.getByRole('button', { name: /summaries/i });
		await fireEvent.click(summariesTab);

		// Tab should be highlighted/active
		expect(summariesTab).toHaveClass('font-bold');
	});

	it('can navigate back to pipeline from summaries view', async () => {
		render(Page);

		// Navigate to summaries
		const summariesTab = screen.getByRole('button', { name: /summaries/i });
		await fireEvent.click(summariesTab);

		// Navigate back to pipeline
		const pipelineTab = screen.getByRole('button', { name: /pipeline/i });
		await fireEvent.click(pipelineTab);

		// Should show pipeline content again
		await waitFor(() => {
			expect(screen.getByText(/Import to Triage/i)).toBeInTheDocument();
			expect(screen.getByText(/📂 Triage/i)).toBeInTheDocument();
		});
	});
});
