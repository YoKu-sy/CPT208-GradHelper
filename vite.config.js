import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite' // [!code ++]

export default defineConfig({
  plugins: [
    vue(),
    tailwindcss(), // [!code ++]
  ],
  base: '/CPT208-GradHelper/',
})
