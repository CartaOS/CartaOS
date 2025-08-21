import { test, expect } from '@playwright/test';

// Lab flow smoke test (no Tauri invocations):
// - Navigate to Lab tab
// - Assert basic UI elements are present
// - Avoid clicking actions that would call Tauri invoke

test.describe('Lab flow (UI only)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('navigate to Lab and see empty state safely', async ({ page }) => {
    await page.getByRole('button', { name: 'Lab' }).click();

    await expect(page.getByRole('heading', { name: /Laboratório/i })).toBeVisible();
    await expect(page.getByText('Empty')).toBeVisible();

    // Ensure action buttons are not present in empty state
    await expect(page.getByRole('button', { name: 'Correct' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Finalized' })).toHaveCount(0);

    // Go back to Pipeline
    await page.getByRole('button', { name: 'Pipeline' }).click();
    await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
  });
});
