import { render, fireEvent } from '@testing-library/svelte';
import Harness from './ActionButtonFormHarness.svelte';

describe('ActionButton in form', () => {
	it('does not submit the form when clicked', async () => {
		const { getByRole, getByTestId } = render(Harness);
		const btn = getByRole('button', { name: 'Click Me' });
		expect(getByTestId('submit-count').textContent).toBe('0');

		await fireEvent.click(btn);

		// Click should not submit the form because button has type="button"
		expect(getByTestId('submit-count').textContent).toBe('0');
	});
});
