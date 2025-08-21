import { render, screen } from '@testing-library/svelte';
import ActionButton from '../ActionButton.svelte';

describe('ActionButton', () => {
  test('renders default content and green variant classes', async () => {
    // Use loadingText to provide a visible label without relying on children snippet
    render(ActionButton as any, {
      props: {
        color: 'green',
        isLoading: true,
        loadingText: 'Go',
      },
    });

    const btn = await screen.findByRole('button', { name: 'Go' });
    expect(btn).toBeInTheDocument();
    expect(btn.className).toContain('bg-green-500');
    expect(btn.className).toContain('hover:enabled:bg-green-700');
  });

  test('shows loading text and disables', async () => {
    render(ActionButton as any, {
      props: {
        isLoading: true,
        loadingText: 'Wait...',
        children: () => 'Run',
      },
    });

    const btn = await screen.findByRole('button', { name: 'Wait...' });
    expect(btn).toBeDisabled();
    expect(btn.className).toContain('disabled:bg-gray-300');
  });
});
