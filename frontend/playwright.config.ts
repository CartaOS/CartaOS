import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './e2e',
	timeout: 30 * 1000,
	fullyParallel: true,
	reporter: [['html', { outputFolder: 'e2e-artifacts/report' }], ['list']],
	use: {
		baseURL: 'http://127.0.0.1:4173',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
		video: 'retain-on-failure'
	},
	projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
	webServer: {
		command: 'npm run preview -- --port=4173',
		url: 'http://127.0.0.1:4173',
		reuseExistingServer: true,
		stdout: 'pipe',
		stderr: 'pipe'
	}
});
