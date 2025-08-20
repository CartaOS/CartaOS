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
    setupFiles: ['./src/test/setup.ts'],
    exclude: ['e2e/**', 'node_modules/**', 'dist/**'],
    environmentOptions: {
      jsdom: {
        url: 'http://localhost/'
      }
    }
  }
});
