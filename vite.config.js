import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite' // [!code ++]

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(), // [!code ++]
  ],
  base: '/CPT208-GradHelper/',
  server: {
    proxy: {
      '/ielts-api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ielts-api/, ''),
      },
      '/ai-assistant-api': {
        target: 'http://127.0.0.1:8001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/ai-assistant-api/, ''),
      },
    },
  },
})
