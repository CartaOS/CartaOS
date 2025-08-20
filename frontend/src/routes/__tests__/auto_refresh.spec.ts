import { render, screen, waitFor } from '@testing-library/svelte';
import Page from '../../routes/+page.svelte';
import { vi } from 'vitest';

// Mocks come from src/test/setup.ts
import * as core from '@tauri-apps/api/core';
import * as event from '@tauri-apps/api/event';

type InvokeArgs = { cmd: string; args?: any };

// Helper to set mocked queue contents for all directories
function setQueuesSnapshot(s: {
  triage?: string[];
  lab?: string[];
  ocr?: string[];
  summary?: string[];
}) {
  const snapshot = {
    triage: s.triage ?? [],
    lab: s.lab ?? [],
    ocr: s.ocr ?? [],
    summary: s.summary ?? [],
  };

  vi.mocked(core.invoke as any).mockImplementation(async (cmd: string, args?: any) => {
    if (cmd === 'get_files_in_stage') {
      const stage = args?.stage as string;
      switch (stage) {
        case '02_Triage':
          return snapshot.triage;
        case '03_Lab':
          return snapshot.lab;
        case '04_ReadyForOCR':
          return snapshot.ocr;
        case '05_ReadyForSummary':
          return snapshot.summary;
      }
    }
    return undefined;
  });
}

describe('Auto refresh on queues-changed', () => {
  test('updates lists after event', async () => {
    // Initial state
    setQueuesSnapshot({
      triage: ['a.pdf'],
      lab: [],
      ocr: [],
      summary: [],
    });

    render(Page);

    // Initial item visible in Triage column
    await screen.findByText('a.pdf');

    // Change snapshot and emit event
    setQueuesSnapshot({
      triage: ['a.pdf', 'b.pdf'],
      lab: ['x.tif'],
      ocr: [],
      summary: ['c.pdf'],
    });

    (event as any).__emit('queues-changed');

    // Expect new items to appear after refresh
    await waitFor(async () => {
      await screen.findByText('b.pdf');
      await screen.findByText('x.tif');
      await screen.findByText('c.pdf');
    });
  });
});
