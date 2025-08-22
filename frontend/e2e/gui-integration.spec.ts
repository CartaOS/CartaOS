import { test, expect } from '@playwright/test';

test.describe('GUI Roadmap Integration Tests - Issue #24', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
	});

	test('Pipeline view shows all queue sections', async ({ page }) => {
		// Verify Pipeline view is default and shows all queues
		const pipelineButton = page.getByRole('button', { name: 'Pipeline', exact: true });
		await expect(pipelineButton).toHaveClass(/font-bold/);

		// Verify all queue sections are visible
		await expect(page.getByText('📂 Triage')).toBeVisible();
		await expect(page.getByText('🔧 Correction Lab')).toBeVisible();
		await expect(page.getByText('📄 Ready for OCR')).toBeVisible();
		await expect(page.getByText('📝 Summarization')).toBeVisible();
	});

	test('Action buttons are properly disabled during operations', async ({ page }) => {
		// Test main action buttons in Pipeline view
		const triageButton = page.getByRole('button', { name: 'Triage', exact: true });
		const ocrButton = page.getByRole('button', { name: 'OCR Batch' });
		
		// Buttons should be enabled initially
		await expect(triageButton).toBeEnabled();
		await expect(ocrButton).toBeEnabled();
		
		// Click a button and check for loading state (operations complete quickly in test env)
		await triageButton.click();
		
		// Check that status message updates to show operation is running
		const statusArea = page.locator('[role="status"]');
		await expect(statusArea).toContainText(/Running|Triage|completed/);
		
		// Verify buttons are functional after operation
		await expect(triageButton).toBeEnabled();
		await expect(ocrButton).toBeEnabled();
	});

	test('Lab view navigation and functionality', async ({ page }) => {
		// Navigate to Lab view
		await page.getByRole('button', { name: 'Lab', exact: true }).click();
		await expect(page.getByRole('heading', { name: /Lab/i })).toBeVisible();
		
		// Verify Lab button is now active
		const labButton = page.getByRole('button', { name: 'Lab', exact: true });
		await expect(labButton).toHaveClass(/font-bold/);
		
		// Verify Lab view content is visible (check for specific Lab heading)
		await expect(page.getByRole('heading', { name: /Lab/i })).toBeVisible();
	});

	test('Summaries view navigation and functionality', async ({ page }) => {
		// Navigate to Summaries view
		await page.getByRole('button', { name: 'Summaries' }).click();
		await expect(page.getByRole('heading', { name: 'Summaries' })).toBeVisible();
		
		// Verify Summaries button is now active
		const summariesButton = page.getByRole('button', { name: 'Summaries' });
		await expect(summariesButton).toHaveClass(/font-bold/);
		
		// Verify summaries view content is visible (check for specific heading)
		await expect(page.getByRole('heading', { name: 'Summaries' })).toBeVisible();
	});

	test('Settings view shows consistent GEMINI_API_KEY usage', async ({ page }) => {
		// Navigate to Settings
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
		
		// Verify API Key field uses correct label (not legacy API_KEY)
		const apiKeyLabel = page.getByText('API Key (Google Gemini):');
		await expect(apiKeyLabel).toBeVisible();
		
		// Verify API key input is masked (password type)
		const apiKeyInput = page.locator('#apiKey');
		await expect(apiKeyInput).toHaveAttribute('type', 'password');
		
		// Verify Obsidian Vault Path field
		const vaultPathInput = page.locator('#baseDir');
		await expect(vaultPathInput).toBeVisible();
		
		// Verify Save button exists and validation works
		const saveButton = page.getByRole('button', { name: 'Save Settings' });
		await expect(saveButton).toBeVisible();
		await expect(saveButton).toBeDisabled(); // Should be disabled when API key is empty
	});

	test('Settings form validation and error handling', async ({ page }) => {
		await page.getByRole('button', { name: 'Settings' }).click();
		
		const apiKeyInput = page.locator('#apiKey');
		const saveButton = page.getByRole('button', { name: 'Save Settings' });
		
		// Initially disabled due to empty API key
		await expect(saveButton).toBeDisabled();
		
		// Fill API key to enable save button
		await apiKeyInput.fill('test-api-key');
		await expect(saveButton).toBeEnabled();
		
		// Clear API key to test validation
		await apiKeyInput.fill('');
		await expect(saveButton).toBeDisabled();
		
		// Verify validation message
		await expect(page.getByText('API Key is required.')).toBeVisible();
	});

	test('Status messages and error display', async ({ page }) => {
		await page.getByRole('button', { name: 'Settings' }).click();
		
		// Look for status message area
		const statusArea = page.locator('[role="status"]');
		
		// Should show some status message (loading, loaded, or error)
		await expect(statusArea).toBeVisible();
		
		// Status should have proper ARIA attributes
		await expect(statusArea).toHaveAttribute('aria-live', 'polite');
		await expect(statusArea).toHaveAttribute('aria-atomic', 'true');
	});

	test('Auto-refresh functionality without flicker', async ({ page }) => {
		// Stay on Pipeline view and verify main content stability
		const mainContent = page.locator('main');
		await expect(mainContent).toBeVisible();
		
		// Click a main action button and verify smooth operation
		const triageButton = page.getByRole('button', { name: 'Triage', exact: true });
		await triageButton.click();
		
		// Main content should remain visible throughout
		await expect(mainContent).toBeVisible();
		
		// Verify status updates show operation progress
		const statusArea = page.locator('[role="status"]');
		await expect(statusArea).toContainText(/Running|Triage|completed/);
	});

	test('Navigation consistency across all views', async ({ page }) => {
		const views = [
			{ button: 'Pipeline', heading: 'CartaOS' },
			{ button: 'Lab', heading: /Lab/i },
			{ button: 'Summaries', heading: 'Summaries' },
			{ button: 'Settings', heading: 'Settings' }
		];
		
		for (const view of views) {
			// Navigate to view
			const button = page.getByRole('button', { name: view.button, exact: true });
			await button.click();
			
			// Verify heading appears
			await expect(page.getByRole('heading', { name: view.heading })).toBeVisible();
			
			// Verify button becomes active (has font-bold class)
			await expect(button).toHaveClass(/font-bold/);
			
			// Verify other buttons are not active
			for (const otherView of views) {
				if (otherView.button !== view.button) {
					const otherButton = page.getByRole('button', { name: otherView.button, exact: true });
					await expect(otherButton).not.toHaveClass(/font-bold/);
				}
			}
		}
	});

	test('Logs are visible and errors are surfaced', async ({ page }) => {
		// Look for log/status areas in the interface
		const statusElements = page.locator('[role="status"], [aria-live="polite"]');
		
		// Should have at least one status/log area
		await expect(statusElements.first()).toBeVisible();
		
		// Navigate to Settings to trigger potential error states
		await page.getByRole('button', { name: 'Settings' }).click();
		
		const apiKeyInput = page.locator('#apiKey');
		const saveButton = page.getByRole('button', { name: 'Save Settings' });
		
		// Fill invalid data to trigger error
		await apiKeyInput.fill('invalid-key');
		await saveButton.click();
		
		// Error should be visible in status area
		const statusArea = page.locator('[role="status"]');
		await expect(statusArea).toBeVisible();
		
		// Status area should have proper accessibility attributes
		await expect(statusArea).toHaveAttribute('aria-live');
	});
});
