import { invoke } from '@tauri-apps/api/core';

// JSON IPC types
export type TriageJson = {
	status: 'success' | 'error';
	data?: { counts: { triage: number } };
	error?: string;
};

export type OcrJson = {
	status: 'success' | 'error';
	data?: { queued_for_ocr: string[]; counts: { queued: number } };
	error?: string;
};

export type SummarizeJson = {
	status: 'success' | 'error';
	data?: { target_file: string; options: { dry_run: boolean; debug: boolean; force_ocr: boolean } };
	error?: string;
};

// Helpers calling Tauri commands and parsing JSON strings from Python CLI
export async function triageJson(): Promise<TriageJson> {
	const out = await invoke<string>('run_triage_json');
	return JSON.parse(out) as TriageJson;
}

export async function ocrJson(): Promise<OcrJson> {
	const out = await invoke<string>('run_ocr_json');
	return JSON.parse(out) as OcrJson;
}

export async function summarizeJson(
	fileName: string,
	opts: { dry_run?: boolean; debug?: boolean; force_ocr?: boolean } = {}
): Promise<SummarizeJson> {
	const payload: { fileName: string; dryRun: boolean; debug: boolean; forceOcr: boolean } = {
		fileName,
		dryRun: !!opts.dry_run,
		debug: !!opts.debug,
		forceOcr: !!opts.force_ocr
	};
	const out = await invoke<string>('run_summarize_json', payload);
	return JSON.parse(out) as SummarizeJson;
}
