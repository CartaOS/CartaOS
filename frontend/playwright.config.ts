import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	timeout: 30 * 1000,
	fullyParallel: true,
	reporter: [['html', { outputFolder: 'e2e-artifacts/report' }], ['list']],
	// Allow small pixel differences due to rendering on CI runners
	expect: {
		toHaveScreenshot: {
			maxDiffPixelRatio: 0.02 // allow up to 2% pixel diff
		}
	},
	use: {
		baseURL: 'http://127.0.0.1:4173',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
		video: 'retain-on-failure',
		// Normalize rendering across environments
		locale: 'en-US',
		timezoneId: 'UTC',
		// Use a consistent scale factor
		deviceScaleFactor: 1
	},
	projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
	
});
