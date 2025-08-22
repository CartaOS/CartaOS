import { render, screen, fireEvent } from '@testing-library/svelte';
import SettingsView from '../SettingsView.svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';

const mockInvoke = invoke as unknown as Mock;

describe('SettingsView validation', () => {
	beforeEach(() => {
		mockInvoke.mockReset();
	});

	it('disables save and marks API key invalid when empty; shows validation message; then saves when valid', async () => {
		mockInvoke.mockImplementation(async (cmd: string) => {
			if (cmd === 'load_settings') return { api_key: '', base_dir: '' };
			if (cmd === 'save_settings') return undefined;
			return undefined;
		});

		render(SettingsView);

		// Inputs present
		const apiInput = await screen.findByLabelText('API Key (Google Gemini):');
		const baseInput = screen.getByLabelText('Obsidian Vault Path:');
		expect(apiInput).toBeInTheDocument();
		expect(baseInput).toBeInTheDocument();

		// API key empty => invalid
		expect(apiInput).toHaveAttribute('aria-invalid', 'true');
		expect(screen.getByText('API Key is required.')).toBeInTheDocument();

		// Save disabled
		const saveBtn = screen.getByRole('button', { name: 'Save Settings' });
		expect(saveBtn).toBeDisabled();

		// Click save while invalid via keyboard (should early-return and set status)
		await fireEvent.click(saveBtn);
		const status1 = await screen.findByRole('status');
		expect(status1).toHaveTextContent('API Key is required.');

		// Enter API key to become valid
		await fireEvent.input(apiInput, { target: { value: 'abc' } });
		expect(apiInput).toHaveAttribute('aria-invalid', 'false');
		expect(saveBtn).not.toBeDisabled();

		// Also fill base dir and save successfully
		await fireEvent.input(baseInput, { target: { value: '/vault' } });
		await fireEvent.click(saveBtn);
		const status2 = await screen.findByRole('status');
		expect(status2).toHaveTextContent('Settings saved successfully!');
	});
});
