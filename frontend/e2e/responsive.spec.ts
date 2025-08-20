import { test, expect, Page } from '@playwright/test';

async function stubTauri(page: Page) {
  await page.addInitScript(() => {
    // @ts-expect-error minimal internals for @tauri-apps/api
    window.__TAURI_INTERNALS__ = window.__TAURI_INTERNALS__ || {
      transformCallback: () => 1,
    };

    // @ts-expect-error simple in-memory queues snapshot controllable from tests
    window.__mocks__ = {
      queues: {
        triage: ['sample.pdf'],
        lab: [],
        ocr: [],
        summary: [],
      },
    };

    // @ts-expect-error provide minimal subset of Tauri API used by the app
    window.__TAURI__ = {
      invoke: async (cmd: string, args?: any) => {
        if (cmd === 'get_files_in_stage') {
          const stage = args?.stage as string;
          // @ts-expect-error
          const q = window.__mocks__.queues;
          switch (stage) {
            case '02_Triage': return q.triage;
            case '03_Lab': return q.lab;
            case '04_ReadyForOCR': return q.ocr;
            case '05_ReadyForSummary': return q.summary;
          }
        }
        return undefined;
      },
      event: {
        _listeners: new Map<string, Function[]>(),
        listen: async (event: string, cb: (payload: any) => void) => {
          const map = (window as any).__TAURI__.event._listeners as Map<string, Function[]>;
          const arr = map.get(event) ?? [];
          arr.push(cb);
          map.set(event, arr);
          return () => {
            const current = map.get(event) ?? [];
            map.set(event, current.filter((h) => h !== cb));
          };
        },
        emit: (event: string, payload?: any) => {
          const map = (window as any).__TAURI__.event._listeners as Map<string, Function[]>;
          for (const h of map.get(event) ?? []) h({ event, payload });
        },
      },
    };
  });
}

async function setQueues(page: Page, qs: { triage?: string[]; lab?: string[]; ocr?: string[]; summary?: string[] }) {
  await page.evaluate((qs) => {
    // @ts-expect-error update snapshot and emit
    Object.assign(window.__mocks__.queues, qs);
    // @ts-expect-error
    window.__TAURI__.event.emit('queues-changed');
  }, qs);
}

test.describe('Responsive smoke', () => {
  test('mobile/tablet/desktop render and auto-refresh', async ({ page }) => {
    await stubTauri(page);

    // Desktop
    await page.setViewportSize({ width: 1366, height: 900 });
    await page.goto('/');
    await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
    await expect(page.getByText('sample.pdf')).toBeVisible();

    // Trigger auto-refresh and check UI updates
    await setQueues(page, { triage: ['sample.pdf', 'new.pdf'], lab: ['work.tif'] });
    await expect(page.getByText('new.pdf')).toBeVisible();
    await expect(page.getByText('work.tif')).toBeVisible();

    // Tablet screenshot
    await page.setViewportSize({ width: 820, height: 1000 });
    await page.screenshot({ path: 'e2e-artifacts/tablet.png', fullPage: true });

    // Mobile screenshot
    await page.setViewportSize({ width: 390, height: 844 });
    await page.screenshot({ path: 'e2e-artifacts/mobile.png', fullPage: true });
  });
});
