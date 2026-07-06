import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    port: 5173,
    proxy: {
      '/predict': 'http://127.0.0.1:8000',
      '/train': 'http://127.0.0.1:8000',
      '/dashboard': 'http://127.0.0.1:8000',
      '/drift': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
    },
  },
  build: {
    outDir: 'dist',
  },
});
