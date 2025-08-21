import { fireEvent, render, screen, waitFor } from '@testing-library/svelte';
import Page from '../+page.svelte';
import type { Mock } from 'vitest';

vi.mock('@tauri-apps/api/core', async (importOriginal) => {
  const actual = (await importOriginal()) as typeof import('@tauri-apps/api/core');
  return {
    ...actual,
    invoke: vi.fn(async (cmd: string, args?: Record<string, unknown>) => {
      if (cmd === 'get_files_in_stage') {
        const stage = args?.stage as string | undefined;
        if (stage === '02_Triage') return [];
        if (stage === '03_Lab') return [];
        if (stage === '04_ReadyForOCR') return [];
        if (stage === '05_ReadyForSummary') return ['doc.pdf'];
      }
      if (cmd === 'run_summarize_single') return 'ok';
      if (cmd === 'run_summarize_json') {
        const fileName = (args?.fileName as string | undefined) ?? 'doc.pdf';
        return JSON.stringify({ status: 'success', data: { target_file: fileName, options: { dry_run: false, debug: false, force_ocr: false } } });
      }
      return 'ok';
    }),
  };
});

import { invoke } from '@tauri-apps/api/core';
const mockInvoke = invoke as unknown as Mock;

describe('Pipeline summarization actions', () => {
  beforeEach(() => {
    mockInvoke.mockClear();
  });

  it('enriches summarize batch with current queue count', async () => {
    render(Page);

    // Wait initial refresh
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    const batchBtn = await screen.findByRole('button', { name: /summarize batch/i });
    await fireEvent.click(batchBtn);

    await waitFor(() => {
      expect(screen.getByText('Summarization Batch: 1 files ready')).toBeInTheDocument();
    });
  });

  it('shows batch summarize button', async () => {
    render(Page);
    expect(await screen.findByRole('button', { name: /summarize batch/i })).toBeInTheDocument();
  });

  it('enriches summarize single with JSON status', async () => {
    render(Page);

    // Wait initial refresh
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // There should be a Summarize button for doc.pdf
    const summarizeBtn = await screen.findByRole('button', { name: 'Summarize' });
    await fireEvent.click(summarizeBtn);

    await waitFor(() => {
      expect(screen.getByText('Summarize: doc.pdf acknowledged')).toBeInTheDocument();
    });
  });
});
