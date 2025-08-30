import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
  build: {
    lib: {
      entry: 'src/embed/index.ts',
      name: 'BraxChat',
      fileName: 'brax-chat',
      formats: ['umd', 'iife']
    },
    rollupOptions: {
      external: [],
      output: {
        globals: {}
      }
    }
  }
})