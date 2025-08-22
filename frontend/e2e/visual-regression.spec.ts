import { test, expect } from '@playwright/test';

// Visual regression tests for key components
// This test captures screenshots and compares them for visual changes

test.describe('Visual regression tests', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
	});

	test('ActionButton component visual states', async ({ page }) => {
		// Navigate to a view with ActionButton components
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

		// Screenshot the Save Settings button in normal state
		const saveButton = page.getByRole('button', { name: /save/i });
		await expect(saveButton).toBeVisible();
		await expect(saveButton).toHaveScreenshot('action-button-normal.png');

		// Fill form to enable button
		const apiKeyInput = page.locator('#apiKey');
		await apiKeyInput.fill('test-api-key-for-visual');
		
		// Screenshot enabled button state
		await expect(saveButton).toHaveScreenshot('action-button-enabled.png');

		// Click to trigger loading state and capture if possible
		await saveButton.click();
		
		// Wait a moment to potentially capture loading state
		await page.waitForTimeout(100);
		await expect(saveButton).toHaveScreenshot('action-button-loading.png');
	});

	test('QueueColumn component visual states', async ({ page }) => {
		// Navigate to Pipeline view (default)
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();

		// Screenshot the main pipeline area
		const mainContent = page.locator('main');
		await expect(mainContent).toHaveScreenshot('pipeline-main-view.png');
	});

	test('LogPanel component visual states', async ({ page }) => {
		// Navigate to Pipeline view where LogPanel is visible
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();

		// Screenshot the log panel area
		const logPanel = page.locator('.log-panel, [class*="log"]').first();
		if (await logPanel.isVisible()) {
			await expect(logPanel).toHaveScreenshot('log-panel.png');
		} else {
			// If log panel is not immediately visible, look for status message area
			const statusArea = page.locator('text=Waiting for action').locator('..').first();
			await expect(statusArea).toHaveScreenshot('status-message-area.png');
		}
	});

	test('Navigation tabs visual consistency', async ({ page }) => {
		// Screenshot Pipeline button in active state
		const pipelineBtn = page.getByRole('button', { name: 'Pipeline', exact: true });
		await expect(pipelineBtn).toHaveScreenshot('nav-pipeline-button.png');

		// Navigate to Lab and screenshot Lab button
		await page.getByRole('button', { name: 'Lab', exact: true }).click();
		await expect(page.getByRole('heading', { name: /Lab/i })).toBeVisible();
		const labBtn = page.getByRole('button', { name: 'Lab', exact: true });
		await expect(labBtn).toHaveScreenshot('nav-lab-button.png');
	});

	test('Form components visual states', async ({ page }) => {
		// Navigate to Settings for form testing
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

		// Screenshot form in initial state
		const settingsForm = page.locator('.settings-view, form').first();
		await expect(settingsForm).toHaveScreenshot('settings-form-initial.png');

		// Fill form and screenshot filled state
		const apiKeyInput = page.locator('#apiKey');
		const baseDirInput = page.locator('#baseDir');
		
		await apiKeyInput.fill('sample-api-key-12345');
		await baseDirInput.fill('/home/user/ObsidianVault');
		
		await expect(settingsForm).toHaveScreenshot('settings-form-filled.png');

		// Clear one field to show validation state
		await apiKeyInput.clear();
		await expect(settingsForm).toHaveScreenshot('settings-form-validation.png');
	});

	test('Responsive layout visual checks', async ({ page }) => {
		// Test different viewport sizes for responsive design
		
		// Desktop view (default)
		await expect(page.locator('body')).toHaveScreenshot('layout-desktop.png');

		// Tablet view
		await page.setViewportSize({ width: 768, height: 1024 });
		await expect(page.locator('body')).toHaveScreenshot('layout-tablet.png');

		// Mobile view
		await page.setViewportSize({ width: 375, height: 667 });
		await expect(page.locator('body')).toHaveScreenshot('layout-mobile.png');

		// Reset to desktop
		await page.setViewportSize({ width: 1280, height: 720 });
	});

	test('Color theme consistency', async ({ page }) => {
		// Test color consistency across different components
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toHaveScreenshot('heading-colors.png');

		// Test individual navigation buttons
		const pipelineButton = page.getByRole('button', { name: 'Pipeline' });
		await expect(pipelineButton).toHaveScreenshot('pipeline-button.png');

		const labButton = page.getByRole('button', { name: 'Lab' });
		await expect(labButton).toHaveScreenshot('lab-button.png');
	});
});
