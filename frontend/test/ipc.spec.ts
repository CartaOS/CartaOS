import { describe, it, expect, vi, beforeEach } from 'vitest';

vi.mock('@tauri-apps/api/core', () => {
	return {
		invoke: vi.fn(async (cmd: string, args?: any) => {
			if (cmd === 'run_triage_json') {
				return JSON.stringify({ status: 'success', data: { counts: { triage: 3 } } });
			}
			if (cmd === 'run_ocr_json') {
				return JSON.stringify({
					status: 'success',
					data: { queued_for_ocr: ['a.pdf'], counts: { queued: 1 } }
				});
			}
			if (cmd === 'run_summarize_json') {
				return JSON.stringify({
					status: 'success',
					data: {
						target_file: args?.fileName ?? 'x.pdf',
						options: { dry_run: !!args?.dryRun, debug: !!args?.debug, force_ocr: !!args?.forceOcr }
					}
				});
			}
			throw new Error('unknown command: ' + cmd);
		})
	};
});

import { triageJson, ocrJson, summarizeJson } from '../src/lib/ipc';

describe('ipc json helpers', () => {
	beforeEach(() => {
		// Reset mocks if needed
	});

	it('triageJson parses counts', async () => {
		const res = await triageJson();
		expect(res.status).toBe('success');
		expect(res.data?.counts.triage).toBe(3);
	});

	it('ocrJson returns queued items', async () => {
		const res = await ocrJson();
		expect(res.status).toBe('success');
		expect(res.data?.queued_for_ocr).toEqual(['a.pdf']);
		expect(res.data?.counts.queued).toBe(1);
	});

	it('summarizeJson passes options and file name', async () => {
		const res = await summarizeJson('doc.pdf', { dry_run: true, debug: false, force_ocr: false });
		expect(res.status).toBe('success');
		expect(res.data?.target_file).toBe('doc.pdf');
		expect(res.data?.options.dry_run).toBe(true);
		expect(res.data?.options.debug).toBe(false);
		expect(res.data?.options.force_ocr).toBe(false);
	});
});
