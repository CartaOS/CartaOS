import { render, screen, fireEvent } from '@testing-library/svelte';
import Page from '../+page.svelte';
import { axe } from 'jest-axe';

describe('Home page (+page.svelte)', () => {
	it('renders tabs and shows Pipeline actions by default', async () => {
		render(Page);

		// Tabs visible
		expect(screen.getByRole('button', { name: 'Pipeline' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Lab' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Settings' })).toBeInTheDocument();

		// Initial render starts a refresh causing buttons to be in a loading state.
		// Wait until queues are refreshed before asserting the action labels.
		await screen.findByText(/File queues refreshed successfully\./i, undefined, { timeout: 5000 });

		// Default view = Pipeline, with main action buttons
		expect(screen.getByRole('button', { name: 'Triage' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'OCR Batch' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Summarize Batch' })).toBeInTheDocument();
	});

	it('switches to Lab view and shows lab-specific controls', async () => {
		render(Page);

		await fireEvent.click(screen.getByRole('button', { name: 'Lab' }));

		// Heading from LabView (currently Portuguese title)
		expect(screen.getByRole('heading', { name: /Laboratório \(03_Lab\)/ })).toBeInTheDocument();
		// Refresh control present
		expect(screen.getByRole('button', { name: 'Refresh Lab Files' })).toBeInTheDocument();
	});

	it('switches to Settings view and shows settings form controls', async () => {
		render(Page);

		await fireEvent.click(screen.getByRole('button', { name: 'Settings' }));

		// Settings heading
		expect(screen.getByRole('heading', { name: 'Settings' })).toBeInTheDocument();
		// Save button present
		expect(screen.getByRole('button', { name: 'Save Settings' })).toBeInTheDocument();
		// Inputs present
		expect(screen.getByLabelText(/API Key/i)).toBeInTheDocument();
		expect(screen.getByLabelText(/Obsidian Vault Path/i)).toBeInTheDocument();
	});

	it('has no obvious accessibility violations on initial render', async () => {
		const { container } = render(Page);
		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});

	it('exposes a live status region that updates after refresh', async () => {
		render(Page);
		// After initial refresh completes, status message should be announced and visible
		await screen.findByText(/File queues refreshed successfully\./i, undefined, { timeout: 5000 });
		const status = screen.getByRole('status');
		expect(status).toHaveTextContent(/File queues refreshed successfully\./i);
	});
});
