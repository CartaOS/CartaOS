import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import Page from '../+page.svelte';

const mockInvoke = invoke as unknown as Mock;

describe('Pipeline view (+page.svelte)', () => {
  beforeEach(() => {
    mockInvoke.mockReset();
  });

  it('loads queues on mount and shows status message', async () => {
    mockInvoke.mockImplementation(async (cmd: string, args?: unknown) => {
      if (cmd === 'get_files_in_stage') {
        const stage = (args as { stage: string }).stage;
        if (stage === '02_Triage') return ['triage1'];
        if (stage === '03_Lab') return ['lab1'];
        if (stage === '04_ReadyForOCR') return [];
        if (stage === '05_ReadyForSummary') return [];
      }
      return undefined;
    });

    render(Page);

    // Status should eventually reflect refresh completion
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // Columns render items
    expect(screen.getByText('triage1')).toBeInTheDocument();
    expect(screen.getByText('lab1')).toBeInTheDocument();
  });

  it('runs triage and updates status', async () => {
    mockInvoke.mockImplementation(async (cmd: string) => {
      if (cmd === 'run_triage') return 'Triage done';
      if (cmd === 'get_files_in_stage') {
        // keep queues empty to simplify
        return [];
      }
      return undefined;
    });

    render(Page);

    // Wait until initial refresh has completed so buttons are enabled
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // Click Triage button (label changed)
    await fireEvent.click(screen.getByRole('button', { name: 'Triage' }));

    // Ensure command invoked
    await waitFor(() => {
      expect(mockInvoke).toHaveBeenCalledWith('run_triage');
    });

    // After the follow-up refresh, we end with the standard success status
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });
  });

  it('handles errors from OCR batch', async () => {
    mockInvoke.mockImplementation(async (cmd: string) => {
      if (cmd === 'run_ocr_batch') throw new Error('ocr-fail');
      if (cmd === 'get_files_in_stage') return [];
      return undefined;
    });

    render(Page);

    // Wait until initial refresh has completed so buttons are enabled
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    await fireEvent.click(screen.getByRole('button', { name: 'OCR Batch' }));

    await waitFor(() => {
      expect(screen.getByText(/ERROR in OCR Batch:/)).toBeInTheDocument();
      expect(screen.getByText(/ocr-fail/)).toBeInTheDocument();
    });
  });
});
