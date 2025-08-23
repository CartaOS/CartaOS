import { render, screen } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import LabView from '../LabView.svelte';

describe('LabView', () => {
	it('renders heading and description', async () => {
		const { container } = render(LabView);
		expect(
			screen.getByRole('heading', { level: 2, name: 'Lab (03_Lab)' })
		).toBeInTheDocument();
		expect(
			screen.getByText('Here you will see files that need human correction in ScanTailor.')
		).toBeInTheDocument();

		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});
});
