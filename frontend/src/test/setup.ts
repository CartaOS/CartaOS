import '@testing-library/jest-dom/vitest';
import { afterEach, vi } from 'vitest';
import { cleanup } from '@testing-library/svelte';

// Ensure we clean up the DOM between tests
afterEach(() => {
	cleanup();
});

// Mock Tauri APIs to prevent runtime errors during component import/render in jsdom
vi.mock('@tauri-apps/api', () => ({
	// Provide minimal namespaces that might be imported
	window: {},
	path: {},
	fs: {},
	shell: {}
}));

vi.mock('@tauri-apps/api/core', () => ({
	invoke: vi.fn(async () => undefined)
}));

// Mock event API that LogPanel.svelte uses
vi.mock('@tauri-apps/api/event', () => ({
	listen: vi.fn(async () => ({ unlisten: () => {} }))
}));

// Minimal stub for Tauri internals used by some APIs in jsdom
// @ts-ignore
if (!(globalThis as any).window) {
	// jsdom provides window, but guard just in case
	(globalThis as any).window = {} as any;
}
// @ts-ignore
(window as any).__TAURI_INTERNALS__ = (window as any).__TAURI_INTERNALS__ || {
	transformCallback: (_cb?: (...args: any[]) => any) => {
		// return an id and store nothing; our mocks don't rely on it
		return 1;
	}
};
