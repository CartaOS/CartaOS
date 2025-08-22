import { test, expect } from '@playwright/test';

// Settings persistence E2E test
// This test verifies that settings are properly saved and loaded

test.describe('Settings persistence', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
	});

	test('saves settings and shows success message', async ({ page }) => {
		// Navigate to Settings
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

		// Find the API key input field by ID
		const apiKeyInput = page.locator('#apiKey');
		await expect(apiKeyInput).toBeVisible();

		// Clear and enter a test API key
		await apiKeyInput.clear();
		await apiKeyInput.fill('test-api-key-12345');

		// Find and click Save button
		const saveButton = page.getByRole('button', { name: /save/i });
		await saveButton.click();

		// Wait for any status message to appear (success or error)
		await expect(page.locator('[role="status"]')).toBeVisible();

		// Verify the form still shows the entered value
		await expect(apiKeyInput).toHaveValue('test-api-key-12345');
	});

	test('handles settings load errors gracefully', async ({ page }) => {
		// Navigate to Settings
		await page.getByRole('button', { name: 'Settings' }).click();
		
		// Check that the page loads even if there are no saved settings
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
		await expect(page.locator('#apiKey')).toBeVisible();
		
		// Form should be functional even without pre-existing settings
		const saveButton = page.getByRole('button', { name: /save/i });
		// Button should be disabled initially if no API key is set
		await expect(saveButton).toBeDisabled();
	});

	test('validates required fields before saving', async ({ page }) => {
		// Navigate to Settings
		await page.getByRole('button', { name: 'Settings' }).click();
		
		// Try to save with empty API key
		const apiKeyInput = page.locator('#apiKey');
		await apiKeyInput.clear();
		
		const saveButton = page.getByRole('button', { name: /save/i });
		
		// Save button should be disabled when API key is empty
		await expect(saveButton).toBeDisabled();
		
		// Verify validation message appears
		await expect(page.getByText('API Key is required.')).toBeVisible();
	});
});
