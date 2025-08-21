import { render, screen } from '@testing-library/svelte';
import Layout from '../+layout.svelte';

describe('Layout', () => {
	it('renders without errors', () => {
		const { container } = render(Layout);
		expect(container).toBeTruthy();
		// Not asserting specific DOM since +layout only forwards children
	});
});
