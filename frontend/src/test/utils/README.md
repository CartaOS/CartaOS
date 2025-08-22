# Testing Utilities for Tauri Mocks

This folder provides helpers to mock Tauri's `invoke` and common queue fixtures in Vitest.

## API

- `makeInvokeMock(handlers: Record<string, InvokeHandler | unknown>): Mock`
  Replace `@tauri-apps/api/core` `invoke` with a mock that routes by command name.
  - If the value is a function, it is called with `(cmd, args)`.
  - If the value is a literal, it is returned directly.

- `withQueues({ triage?, lab?, ocr?, summary? }): InvokeHandler`
  Returns a handler for `get_files_in_stage` that serves arrays per stage.

- `withError(cmd: string, error?: unknown): InvokeHandler`
  Throws `error` when `cmd` matches; otherwise returns `undefined`.

## Example

```ts
import { render, screen, waitFor } from '@testing-library/svelte';
import Page from '../../routes/+page.svelte';
import { makeInvokeMock, withQueues } from './tauriMock';

makeInvokeMock({
	get_files_in_stage: withQueues({ triage: ['a.pdf'], lab: ['b.pdf'] }),
	run_summarize_batch: 'ok'
});

render(Page);
await waitFor(() => {
	expect(screen.getByRole('status')).toHaveTextContent('File queues refreshed successfully.');
});
```
