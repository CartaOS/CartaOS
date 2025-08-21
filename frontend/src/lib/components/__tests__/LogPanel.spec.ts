import { render, screen } from '@testing-library/svelte';
import LogPanel from '../LogPanel.svelte';
import * as event from '@tauri-apps/api/event';

describe('LogPanel', () => {
  test('renders incoming log messages', async () => {
    render(LogPanel as any);

    // Emit a mocked log-message event via our test setup emitter
    (event as any).__emit('log-message', {
      timestamp: '2025-01-01T00:00:00Z',
      message: 'Hello World',
    });

    // Assert content appears
    expect(await screen.findByText('Hello World')).toBeInTheDocument();
    expect(await screen.findByText('2025-01-01T00:00:00Z')).toBeInTheDocument();
  });
});
