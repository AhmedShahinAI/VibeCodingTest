import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api/v1/auth': 'http://localhost:3001',
      '/api/v1/rbac': 'http://localhost:3002',
      '/api/v1/tenants': 'http://localhost:3002',
      '/api/v1/me': 'http://localhost:3001',
    },
  },
});
