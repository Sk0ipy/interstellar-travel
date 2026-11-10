import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// In development the Flask backend runs on :5000; forward everything that is not the React app.
const backend = 'http://127.0.0.1:5000'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': backend,
      '/admin': backend,
      '/static': backend,
      '/robots.txt': backend,
    },
  },
})
