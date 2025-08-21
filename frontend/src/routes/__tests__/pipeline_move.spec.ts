import { render, screen, fireEvent, waitFor, within } from '@testing-library/svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';
import Page from '../+page.svelte';

const mockInvoke = invoke as unknown as Mock;

describe('Pipeline moves and refresh behavior', () => {
  beforeEach(() => {
    mockInvoke.mockReset();
  });

  it('finalizing a lab file moves it to OCR and refresh updates columns', async () => {
    // simple stateful mock
    const triage: string[] = [];
    let lab: string[] = ['doc1.pdf'];
    let ocr: string[] = [];
    const summary: string[] = [];

    mockInvoke.mockImplementation(async (cmd: string, args?: { stage?: string; fileName?: string }) => {
      if (cmd === 'get_files_in_stage') {
        const stage = args?.stage as string;
        if (stage === '02_Triage') return triage;
        if (stage === '03_Lab') return lab;
        if (stage === '04_ReadyForOCR') return ocr;
        if (stage === '05_ReadyForSummary') return summary;
      }
      if (cmd === 'finalize_lab_file') {
        const file = args?.fileName as string;
        lab = lab.filter((f) => f !== file);
        ocr = [...ocr, file];
        return `Finalized ${file}`;
      }
      return undefined;
    });

    render(Page);

    // Wait initial refresh success
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // Assert doc1 appears in Lab column first
    const labHeading = screen.getByRole('heading', { name: '🔧 Correction Lab' });
    const labColumn = labHeading.parentElement as HTMLElement;
    expect(within(labColumn).getByText('doc1.pdf')).toBeInTheDocument();

    // Click Finalized for that file
    const finalizeBtn = within(labColumn).getByRole('button', { name: 'Finalized' });
    await fireEvent.click(finalizeBtn);

    // After finalize, expect refresh success and that Lab shows Empty while OCR shows the file
    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // Lab empty
    expect(within(labColumn).getByText('Empty')).toBeInTheDocument();

    // OCR has the file
    const ocrHeading = screen.getByRole('heading', { name: '📄 Ready for OCR' });
    const ocrColumn = ocrHeading.parentElement as HTMLElement;
    expect(within(ocrColumn).getByText('doc1.pdf')).toBeInTheDocument();
  });

  it('auto-refresh updates data when files change', async () => {
    let toggle = 0;
    mockInvoke.mockImplementation(async (cmd: string, args?: { stage?: string }) => {
      if (cmd === 'get_files_in_stage') {
        const stage = args?.stage as string;
        if (stage === '03_Lab') return toggle === 0 ? [] : ['newfile.tif'];
        if (stage === '02_Triage' || stage === '04_ReadyForOCR' || stage === '05_ReadyForSummary') return [];
      }
      return undefined;
    });

    render(Page);

    await waitFor(() => {
      expect(screen.getByText('File queues refreshed successfully.')).toBeInTheDocument();
    });

    // Initially empty
    const labHeading = screen.getByRole('heading', { name: '🔧 Correction Lab' });
    const labColumn = labHeading.parentElement as HTMLElement;
    expect(within(labColumn).getByText('Empty')).toBeInTheDocument();

    // Change mock data and rely on auto-refresh (2s polling) to pick it up
    toggle = 1;
    await waitFor(
      () => {
        expect(within(labColumn).getByText('newfile.tif')).toBeInTheDocument();
      },
      { timeout: 4000 }
    );
  });
});
