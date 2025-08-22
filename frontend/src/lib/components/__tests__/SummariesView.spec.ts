import { render, screen, waitFor, fireEvent } from '@testing-library/svelte';
import SummariesView from '../SummariesView.svelte';
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

describe('SummariesView', () => {
	beforeEach(() => {
		mockInvoke.mockClear();
	});

	it('renders heading and loads summaries on mount', async () => {
		const mockSummaries = [
			{ name: 'doc1.md', path: '/summaries/doc1.md', modified: '2024-01-01' },
			{ name: 'doc2.md', path: '/summaries/doc2.md', modified: '2024-01-02' }
		];

		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'list_summaries') return mockSummaries;
			if (cmd === 'get_vault_path') return null;
			return undefined;
		});

		render(SummariesView);

		expect(screen.getByRole('heading', { name: /summaries/i })).toBeInTheDocument();

		await waitFor(() => {
			expect(screen.getByText('doc1.md')).toBeInTheDocument();
			expect(screen.getByText('doc2.md')).toBeInTheDocument();
		});
	});

	it('shows empty state when no summaries exist', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'list_summaries') return [];
			if (cmd === 'get_vault_path') return null;
			return undefined;
		});

		render(SummariesView);

		await waitFor(() => {
			expect(screen.getByText(/no summaries found/i)).toBeInTheDocument();
		});
	});

	it('shows error state when loading fails', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'list_summaries') throw new Error('Failed to load');
			if (cmd === 'get_vault_path') return null;
			return undefined;
		});

		render(SummariesView);

		await waitFor(() => {
			expect(screen.getByText(/error loading summaries/i)).toBeInTheDocument();
		});
	});

	it('loads and displays summary content when clicked', async () => {
		const mockSummaries = [{ name: 'doc1.md', path: '/summaries/doc1.md', modified: '2024-01-01' }];
		const mockContent = '# Summary\n\nThis is a test summary.';

		mockInvoke.mockImplementation(async (cmd: string, args?: any) => {
			if (cmd === 'list_summaries') return mockSummaries;
			if (cmd === 'get_vault_path') return null;
			if (cmd === 'read_summary' && args?.path === '/summaries/doc1.md') return mockContent;
			return undefined;
		});

		render(SummariesView);

		await waitFor(() => {
			expect(screen.getByText('doc1.md')).toBeInTheDocument();
		});

		await fireEvent.click(screen.getByText('doc1.md'));

		await waitFor(() => {
			expect(mockInvoke).toHaveBeenCalledWith('read_summary', { path: '/summaries/doc1.md' });
			expect(screen.getByText(/This is a test summary/)).toBeInTheDocument();
		});
	});

	it('shows open in vault button when vault path is configured', async () => {
		const mockSummaries = [
			{ name: 'doc1.md', path: '/vault/summaries/doc1.md', modified: '2024-01-01' }
		];

		mockInvoke.mockImplementation(async (cmd: string, _args?: any) => {
			if (cmd === 'list_summaries') return mockSummaries;
			if (cmd === 'get_vault_path') return '/vault';
			if (cmd === 'read_summary') return '# Test';
			return undefined;
		});

		render(SummariesView);

		await waitFor(() => {
			expect(screen.getByText('doc1.md')).toBeInTheDocument();
		});

		await fireEvent.click(screen.getByText('doc1.md'));

		await waitFor(() => {
			expect(screen.getByRole('button', { name: /open in vault/i })).toBeInTheDocument();
		});
	});

	it('invokes open_in_vault when button is clicked', async () => {
		const mockSummaries = [
			{ name: 'doc1.md', path: '/vault/summaries/doc1.md', modified: '2024-01-01' }
		];

		mockInvoke.mockImplementation(async (cmd: string, _args?: any) => {
			if (cmd === 'list_summaries') return mockSummaries;
			if (cmd === 'get_vault_path') return '/vault';
			if (cmd === 'read_summary') return '# Test';
			if (cmd === 'open_in_vault') return undefined;
			return undefined;
		});

		render(SummariesView);

		await waitFor(() => {
			expect(screen.getByText('doc1.md')).toBeInTheDocument();
		});

		await fireEvent.click(screen.getByText('doc1.md'));

		const openButton = await screen.findByRole('button', { name: /open in vault/i });
		await fireEvent.click(openButton);

		expect(mockInvoke).toHaveBeenCalledWith('open_in_vault', { path: '/vault/summaries/doc1.md' });
	});
});
