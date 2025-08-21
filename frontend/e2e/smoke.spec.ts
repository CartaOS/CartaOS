import { test, expect } from '@playwright/test';

// Simple smoke test: app serves and root page renders title
// Adjust expectations if the landing page content changes.

test('loads home page and shows title', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle(/CartaOS/i);
  // Verify visible heading contains CartaOS (be lenient)
  const h1 = page.getByRole('heading', { level: 1 });
  await expect(h1).toContainText(/CartaOS/i);
});
