import { describe, it, expect, vi } from 'vitest';
import { openFilesDialog } from '../dialog';

declare global {
	interface Window {
		__TAURI__?: {
			dialog?: {
				open?: (opts: { multiple?: boolean; title?: string }) => Promise<string | string[] | null>;
			};
		};
	}
}

describe('openFilesDialog wrapper', () => {
	const original = window.__TAURI__;

	afterEach(() => {
		window.__TAURI__ = original;
	});

	it('returns null when tauri dialog is unavailable', async () => {
		window.__TAURI__ = undefined;
		const res = await openFilesDialog();
		expect(res).toBeNull();
	});

	it('normalizes single string to array', async () => {
		window.__TAURI__ = {
			dialog: {
				open: vi.fn(async () => 'one.pdf')
			}
		};
		const res = await openFilesDialog({ multiple: false, title: 'Pick file' });
		expect(res).toEqual(['one.pdf']);
	});

	it('passes through array selection', async () => {
		window.__TAURI__ = {
			dialog: {
				open: vi.fn(async () => ['a.pdf', 'b.pdf'])
			}
		};
		const res = await openFilesDialog({ multiple: true });
		expect(res).toEqual(['a.pdf', 'b.pdf']);
	});

	it('returns null when open resolves to null', async () => {
		window.__TAURI__ = {
			dialog: {
				open: vi.fn(async () => null)
			}
		};
		const res = await openFilesDialog();
		expect(res).toBeNull();
	});
});
