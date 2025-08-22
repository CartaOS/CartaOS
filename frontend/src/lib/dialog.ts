export type OpenFilesOptions = {
	multiple?: boolean;
	title?: string;
};

// Lightweight wrapper that uses the Tauri global if available. This avoids a hard dependency
// on the dialog plugin for unit tests and lets us mock this module easily.
export async function openFilesDialog(
	opts: OpenFilesOptions = { multiple: true }
): Promise<string[] | null> {
	type TauriDialog = {
		open?: (options: { multiple?: boolean; title?: string }) => Promise<string | string[] | null>;
	};
	type TauriGlobal = { __TAURI__?: { dialog?: TauriDialog } };
	const tauri = window as unknown as TauriGlobal;
	const tauriOpen = tauri.__TAURI__?.dialog?.open;
	if (typeof tauriOpen === 'function') {
		const selection = await tauriOpen({ multiple: opts.multiple ?? true, title: opts.title });
		if (Array.isArray(selection)) return selection as string[];
		if (typeof selection === 'string') return [selection];
		return null;
	}
	// Not running under Tauri or dialog plugin not available.
	return null;
}
