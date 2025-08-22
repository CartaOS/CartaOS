import '@testing-library/jest-dom/vitest';
import { expect, vi } from 'vitest';
import { toHaveNoViolations } from 'jest-axe';

// Extend expect with a11y matcher
expect.extend(toHaveNoViolations);

// Minimal global mocks for Tauri APIs used in components/tests
vi.mock('@tauri-apps/api/core', () => {
	return {
		invoke: vi.fn(async () => {
			// Default mock: return sensible defaults per command if needed by tests
			return undefined;
		})
	};
});

// Event mocking for LogPanel
const _eventListeners: Record<string, Array<(e: { payload: unknown }) => void>> = {};
const _unlistenCount: Record<string, number> = {};
vi.mock('@tauri-apps/api/event', () => {
	return {
		listen: vi.fn(async (event: string, cb: (e: { payload: unknown }) => void) => {
			_eventListeners[event] ||= [];
			_eventListeners[event].push(cb);
			// Return an UnlistenFn-like function
			return () => {
				_unlistenCount[event] = (_unlistenCount[event] || 0) + 1;
			};
		})
	};
});

// Expose a helper to emit tauri events from tests
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).__emitTauri = (event: string, payload: any) => {
	const listeners = _eventListeners[event] || [];
	const evt = { payload };
	for (const cb of listeners) cb(evt);
};

// Expose stats for tests to assert cleanup behavior
// eslint-disable-next-line @typescript-eslint/no-explicit-any
(globalThis as any).__getTauriEventStats = () => ({
	unlistenCount: { ..._unlistenCount }
});
