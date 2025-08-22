import { render, screen } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import Harness from './QueueColumnHarness.svelte';

describe('QueueColumn children snippet', () => {
	it('renders provided snippet with file param', async () => {
		const { container } = render(Harness);
		expect(await screen.findByRole('button', { name: 'Open x.pdf' })).toBeInTheDocument();
		expect(screen.getByRole('button', { name: 'Open y.pdf' })).toBeInTheDocument();

		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});
});
