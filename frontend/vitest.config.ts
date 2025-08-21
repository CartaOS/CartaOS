import { defineConfig } from 'vitest/config';
import { sveltekit } from '@sveltejs/kit/vite';

export default defineConfig({
  plugins: [sveltekit()],
  resolve: {
    conditions: ['browser']
  },
  test: {
    globals: true,      // <— habilita describe/it/expect sem importar
    environment: 'jsdom',
    setupFiles: ['tests/setup.ts'],
    exclude: [
      'e2e/**',                 // não rodar specs do Playwright no Vitest
      '**/node_modules/**',    // garantir exclusão de testes de deps
      '**/dist/**',
      '**/build/**'
    ],
    coverage: {
      enabled: true,
      reporter: ['text-summary', 'lcov'],
      reportsDirectory: './coverage',
      all: false,
      thresholds: {
        lines: 90,
        statements: 90,
        branches: 85,
        functions: 70
      }
    }
  }
});
