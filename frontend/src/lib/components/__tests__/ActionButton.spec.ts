import { render, screen, fireEvent } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import ActionButton from '../ActionButton.svelte';
import { vi } from 'vitest';

describe('ActionButton', () => {
	it('renders label when not loading and calls onclick', async () => {
		const onclick = vi.fn();
		render(ActionButton, { props: { onclick, isLoading: false, label: 'Click Me' } });

		const btn = screen.getByRole('button', { name: 'Click Me' });
		await fireEvent.click(btn);

		expect(onclick).toHaveBeenCalledTimes(1);
	});

	it('shows loading text and is disabled when isLoading', async () => {
		const onclick = vi.fn();
		render(ActionButton, { props: { onclick, isLoading: true, loadingText: 'Loading...' } });

		const btn = screen.getByRole('button', { name: 'Loading...' });
		expect(btn).toBeDisabled();
		await fireEvent.click(btn);
		expect(onclick).not.toHaveBeenCalled();
	});

	it('has no a11y violations', async () => {
		const { container } = render(ActionButton, {
			props: { onclick: () => {}, isLoading: false, label: 'Accessible' }
		});
		const results = await axe(container);
		expect(results).toHaveNoViolations();
	});

	it('uses type="button" to avoid accidental form submission', async () => {
		const onclick = vi.fn();
		render(ActionButton, { props: { onclick, label: 'Submit-ish' } });
		const btn = screen.getByRole('button', { name: 'Submit-ish' });
		expect(btn).toHaveAttribute('type', 'button');
	});
});
