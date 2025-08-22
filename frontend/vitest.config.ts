/// <reference types="vitest/config" />
import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
// import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';
const dirname =
	typeof __dirname !== 'undefined' ? __dirname : path.dirname(fileURLToPath(import.meta.url));

// More info at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon
export default defineConfig({
	plugins: [sveltekit()],
	resolve: {
		conditions: ['browser']
	},
	test: {
		globals: true,
		// <— habilita describe/it/expect sem importar
		environment: 'jsdom',
		setupFiles: ['tests/setup.ts'],
		exclude: [
			'e2e/**',
			// não rodar specs do Playwright no Vitest
			'**/node_modules/**',
			// garantir exclusão de testes de deps
			'**/dist/**',
			'**/build/**'
		],
		coverage: {
			enabled: true,
			reporter: ['text-summary', 'lcov'],
			reportsDirectory: './coverage',
			all: false,
			thresholds: {
				lines: 87,
				statements: 87,
				branches: 85,
				functions: 70
			}
		},
		// projects: [
		// 	{
		// 		extends: true,
		// 		plugins: [
		// 			// The plugin will run tests for the stories defined in your Storybook config
		// 			// See options at: https://storybook.js.org/docs/next/writing-tests/integrations/vitest-addon#storybooktest
		// 			storybookTest({
		// 				configDir: path.join(dirname, '.storybook')
		// 			})
		// 		],
		// 		test: {
		// 			name: 'storybook',
		// 			browser: {
		// 				enabled: true,
		// 				headless: true,
		// 				provider: 'playwright',
		// 				instances: [
		// 					{
		// 						browser: 'chromium'
		// 					}
		// 				]
		// 			},
		// 			setupFiles: ['.storybook/vitest.setup.ts']
		// 		}
		// 	}
		// ]
	}
});
