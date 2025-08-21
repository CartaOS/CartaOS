import { render, screen, fireEvent } from '@testing-library/svelte';
import Page from '../+page.svelte';

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(async () => 'ok'),
}));

describe.skip('Pipeline summarization actions', () => {
  it('shows batch summarize button', async () => {
    render(Page);
    expect(
      screen.getByRole('button', { name: /run summarization batch/i })
    ).toBeInTheDocument();
  });
});
