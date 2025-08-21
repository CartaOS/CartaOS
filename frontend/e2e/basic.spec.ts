import { test, expect } from '@playwright/test';
import AxeBuilder from '@axe-core/playwright';

// Basic smoke + a11y on home route

test.beforeEach(async ({ page }) => {
  await page.goto('/');
});

test('loads home and shows title', async ({ page }) => {
  await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
  await expect(page.getByText('Your Document Processing Pipeline')).toBeVisible();
});

test('has no critical/serious accessibility violations on home', async ({ page }) => {
  const results = await new AxeBuilder({ page })
    .withTags(['wcag2a', 'wcag2aa'])
    .analyze();

  const problematic = results.violations.filter(v =>
    v.impact === 'critical' || v.impact === 'serious'
  );

  const msg = problematic.map(v => `${v.id}: ${v.description}`).join('\n');
  expect(problematic, msg).toHaveLength(0);
});
