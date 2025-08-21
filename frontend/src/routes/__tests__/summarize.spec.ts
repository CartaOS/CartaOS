import { render, screen } from '@testing-library/svelte';
import Page from '../+page.svelte';
import * as core from '@tauri-apps/api/core';

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(async (cmd: string, args?: any) => {
    if (cmd === 'get_files_in_stage') return [];
    return 'ok';
  }),
}));

describe('Pipeline summarization actions', () => {
  it('shows batch summarize button', async () => {
    render(Page);
    // Wait for initial loading to complete and static label to appear
    const btn = await screen.findByRole('button', { name: /summarization batch/i });
    expect(btn).toBeInTheDocument();
  });
});
