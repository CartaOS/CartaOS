import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';

// Ensure we cleanup the DOM between tests
afterEach(() => {
  cleanup();
});

// Mock Tauri APIs to prevent runtime errors during component import/render in jsdom
vi.mock('@tauri-apps/api', () => ({
  // Provide minimal namespaces that might be imported
  window: {},
  path: {},
  fs: {},
  shell: {},
}));

vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(async () => undefined),
}));

// Mock event API that components use, with an internal emitter for tests
vi.mock('@tauri-apps/api/event', () => {
  const listeners = new Map<string, Array<(payload: unknown) => void>>();
  return {
    listen: vi.fn(async (event: string, handler: (payload: unknown) => void) => {
      const arr = listeners.get(event) ?? [];
      arr.push(handler);
      listeners.set(event, arr);
      return () => {
        const current = listeners.get(event) ?? [];
        listeners.set(
          event,
          current.filter((h) => h !== handler)
        );
      };
    }),
    __emit: (event: string, payload?: unknown) => {
      for (const h of listeners.get(event) ?? []) {
        try { h({ event, payload }); } catch {}
      }
    },
  };
});

// Minimal stub for Tauri internals used by some APIs in jsdom
// @ts-expect-error jsdom provides window, this is a guard for safety in tests
if (!(globalThis as any).window) {
  // jsdom provides window, but guard just in case
  (globalThis as any).window = {} as any;
}
// @ts-expect-error provide minimal TAURI internals for libs expecting it
(window as any).__TAURI_INTERNALS__ = (window as any).__TAURI_INTERNALS__ || {
  transformCallback: (_cb?: (...args: unknown[]) => unknown) => 1,
};
