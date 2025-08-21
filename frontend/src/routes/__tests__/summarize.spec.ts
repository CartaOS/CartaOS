import { render, screen } from '@testing-library/svelte';
import Page from '../+page.svelte';

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(async () => 'ok'),
}));

describe('Pipeline summarization actions', () => {
  it('shows batch summarize button', async () => {
    render(Page);
    expect(
      await screen.findByRole('button', { name: /summarize batch/i })
    ).toBeInTheDocument();
  });
});
