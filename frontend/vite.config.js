import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
// import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    // vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  server: {
    host: '0.0.0.0', // 允许外部访问
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://backend:8000', // 关键：指向后端容器
        changeOrigin: true,
        secure: false,
      },
      '/media': {
        target: 'http://backend:8000', // 新增：图片静态资源代理到后端
        changeOrigin: true,
        secure: false,
      }
    }
  }
})
