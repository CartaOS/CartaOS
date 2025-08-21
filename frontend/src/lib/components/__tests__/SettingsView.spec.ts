import { render, screen, fireEvent, waitFor } from '@testing-library/svelte';
import { axe } from 'jest-axe';
import SettingsView from '../SettingsView.svelte';
import type { Mock } from 'vitest';
import { invoke } from '@tauri-apps/api/core';

const mockInvoke = invoke as unknown as Mock;

describe('SettingsView (integration)', () => {
  beforeEach(() => {
    mockInvoke.mockReset();
  });

  it('loads settings on mount and shows success status', async () => {
    mockInvoke.mockImplementation(async (cmd: string) => {
      if (cmd === 'load_settings') return { api_key: 'k', base_dir: '/vault' };
      return undefined;
    });

    const { container } = render(SettingsView);

    // Wait for inputs to be populated after onMount
    const apiInput = await screen.findByLabelText('API Key (Google Gemini):');
    const baseInput = await screen.findByLabelText('Obsidian Vault Path:');

    await waitFor(() => {
      expect((apiInput as HTMLInputElement).value).toBe('k');
      expect((baseInput as HTMLInputElement).value).toBe('/vault');
      expect(screen.getByText('Settings loaded.')).toBeInTheDocument();
    });

    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('saves settings successfully', async () => {
    mockInvoke.mockImplementation(async (cmd: string, args?: unknown) => {
      if (cmd === 'load_settings') return { api_key: '', base_dir: '' };
      if (cmd === 'save_settings') {
        expect(args).toEqual({ apiKey: 'newK', baseDir: '/new' });
        return undefined;
      }
      return undefined;
    });

    render(SettingsView);

    const apiInput = await screen.findByLabelText('API Key (Google Gemini):');
    const baseInput = screen.getByLabelText('Obsidian Vault Path:');

    await fireEvent.input(apiInput, { target: { value: 'newK' } });
    await fireEvent.input(baseInput, { target: { value: '/new' } });

    await fireEvent.click(screen.getByRole('button', { name: 'Save Settings' }));

    await waitFor(() => {
      expect(screen.getByText('Settings saved successfully!')).toBeInTheDocument();
    });
  });

  it('handles load and save errors gracefully', async () => {
    mockInvoke.mockImplementation(async (cmd: string) => {
      if (cmd === 'load_settings') throw new Error('boom-load');
      if (cmd === 'save_settings') throw new Error('boom-save');
      return undefined;
    });

    render(SettingsView);

    await screen.findByText(/Error loading settings:/);

    // Try saving
    await fireEvent.click(screen.getByRole('button', { name: /Save Settings|Saving.../ }));

    await screen.findByText(/Error saving settings:/);
  });
});
