import { test, expect } from '@playwright/test';

// Performance tests using Playwright timing assertions
// This test verifies that key interactions meet performance thresholds

test.describe('Performance checks', () => {
	test.beforeEach(async ({ page }) => {
		await page.goto('/');
	});

	test('home page loads within performance threshold', async ({ page }) => {
		const startTime = Date.now();
		
		// Wait for the main heading to be visible (page fully loaded)
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
		
		const loadTime = Date.now() - startTime;
		
		// Assert page loads within 3 seconds
		expect(loadTime).toBeLessThan(3000);
		console.log(`Home page load time: ${loadTime}ms`);
	});

	test('navigation between views is responsive', async ({ page }) => {
		// Test navigation to Lab view
		const labStartTime = Date.now();
		await page.getByRole('button', { name: 'Lab' }).click();
		await expect(page.getByRole('heading', { name: /Lab/i })).toBeVisible();
		const labNavTime = Date.now() - labStartTime;
		
		// Assert navigation takes less than 1 second
		expect(labNavTime).toBeLessThan(1000);
		console.log(`Lab navigation time: ${labNavTime}ms`);

		// Test navigation to Settings view
		const settingsStartTime = Date.now();
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();
		const settingsNavTime = Date.now() - settingsStartTime;
		
		// Assert navigation takes less than 1 second
		expect(settingsNavTime).toBeLessThan(1000);
		console.log(`Settings navigation time: ${settingsNavTime}ms`);

		// Test navigation to Summaries view
		const summariesStartTime = Date.now();
		await page.getByRole('button', { name: 'Summaries' }).click();
		await expect(page.getByRole('heading', { name: 'Summaries' })).toBeVisible();
		const summariesNavTime = Date.now() - summariesStartTime;
		
		// Assert navigation takes less than 1 second
		expect(summariesNavTime).toBeLessThan(1000);
		console.log(`Summaries navigation time: ${summariesNavTime}ms`);

		// Test navigation back to Pipeline
		const pipelineStartTime = Date.now();
		await page.getByRole('button', { name: 'Pipeline' }).click();
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();
		const pipelineNavTime = Date.now() - pipelineStartTime;
		
		// Assert navigation takes less than 1 second
		expect(pipelineNavTime).toBeLessThan(1000);
		console.log(`Pipeline navigation time: ${pipelineNavTime}ms`);
	});

	test('form interactions are responsive', async ({ page }) => {
		// Navigate to Settings for form testing
		await page.getByRole('button', { name: 'Settings' }).click();
		await expect(page.getByRole('heading', { name: 'Settings' })).toBeVisible();

		// Test form input responsiveness
		const inputStartTime = Date.now();
		const apiKeyInput = page.locator('#apiKey');
		await apiKeyInput.fill('test-performance-key');
		const inputTime = Date.now() - inputStartTime;
		
		// Assert form input takes less than 500ms
		expect(inputTime).toBeLessThan(500);
		console.log(`Form input time: ${inputTime}ms`);

		// Test button click responsiveness
		const buttonStartTime = Date.now();
		const saveButton = page.getByRole('button', { name: /save/i });
		await saveButton.click();
		
		// Wait for status message to appear (indicates processing complete)
		await expect(page.locator('[role="status"]')).toBeVisible();
		const buttonTime = Date.now() - buttonStartTime;
		
		// Assert button response takes less than 2 seconds
		expect(buttonTime).toBeLessThan(2000);
		console.log(`Button response time: ${buttonTime}ms`);
	});

	test('measures Core Web Vitals with basic thresholds', async ({ page }) => {
		// Navigate to home page and measure performance
		const response = await page.goto('/');
		expect(response?.status()).toBe(200);

		// Wait for page to be fully loaded
		await expect(page.getByRole('heading', { name: 'CartaOS' })).toBeVisible();

		// Evaluate Core Web Vitals using Performance API
		const vitals = await page.evaluate(() => {
			return new Promise((resolve) => {
				// Simple performance measurement
				const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
				
				const metrics = {
					// First Contentful Paint approximation
					fcp: navigation.responseEnd - navigation.fetchStart,
					// Largest Contentful Paint approximation  
					lcp: navigation.loadEventEnd - navigation.fetchStart,
					// Total load time
					loadTime: navigation.loadEventEnd - navigation.fetchStart,
					// DOM Content Loaded
					domContentLoaded: navigation.domContentLoadedEventEnd - navigation.fetchStart
				};
				
				resolve(metrics);
			});
		});

		console.log('Performance metrics:', vitals);

		// Assert basic performance thresholds
		expect(vitals.fcp).toBeLessThan(2000); // FCP < 2s
		expect(vitals.lcp).toBeLessThan(4000); // LCP < 4s  
		expect(vitals.loadTime).toBeLessThan(5000); // Total load < 5s
		expect(vitals.domContentLoaded).toBeLessThan(3000); // DCL < 3s
	});
});
