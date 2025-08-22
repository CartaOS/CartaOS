import type { Mock } from 'vitest';
import { invoke as realInvoke } from '@tauri-apps/api/core';

export type InvokeHandler = (
	cmd: string,
	args?: Record<string, unknown>
) => unknown | Promise<unknown>;

export function makeInvokeMock(handlers: Record<string, InvokeHandler | unknown>): Mock {
	const fn = vi.fn(async (cmd: string, args?: Record<string, unknown>) => {
		const h = handlers[cmd];
		if (typeof h === 'function') return (h as InvokeHandler)(cmd, args);
		if (h !== undefined) return h;
		return undefined;
	});
	// Swap the module's invoke to our mock
	(realInvoke as unknown as Mock).mockImplementation(fn);
	return fn as unknown as Mock;
}

export type Queues = {
	triage?: string[];
	lab?: string[];
	ocr?: string[];
	summary?: string[];
};

export function withQueues(q: Queues = {}): InvokeHandler {
	const triage = q.triage ?? [];
	const lab = q.lab ?? [];
	const ocr = q.ocr ?? [];
	const summary = q.summary ?? [];
	return async (_cmd: string, args?: Record<string, unknown>) => {
		const stage = args?.stage as string | undefined;
		if (stage === '02_Triage') return triage;
		if (stage === '03_Lab') return lab;
		if (stage === '04_ReadyForOCR') return ocr;
		if (stage === '05_ReadyForSummary') return summary;
		return [];
	};
}

export function withError(cmd: string, error: unknown = new Error('mock error')): InvokeHandler {
	return async (c: string) => {
		if (c === cmd) throw error;
		return undefined;
	};
}
