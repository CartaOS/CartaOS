import { render, screen } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import LabView from '../LabView.svelte';

describe('LabView', () => {
	it('renders heading and description', async () => {
		const { container } = render(LabView);
		expect(
			screen.getByRole('heading', { level: 2, name: 'Laboratório (03_Lab)' })
		).toBeInTheDocument();
		expect(
			screen.getByText('Aqui você verá os arquivos que precisam de correção manual no ScanTailor.')
		).toBeInTheDocument();

		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});
});
