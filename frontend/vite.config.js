// src/renderer/vite.config.js
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: './', // 确保构建后资源的相对路径正确
  build: {
    outDir: 'dist', // 构建输出目录，相对于frontend目录
    emptyOutDir: true, // 构建前清空输出目录
    // 为Electron环境添加特殊处理
    rollupOptions: {
      external: ['electron'],
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'), // 配置路径别名，方便导入
    },
  },
  server: {
    port: 5173, // Vite 开发服务器端口
    host: '127.0.0.1', // 指定host以避免IPv6权限问题
    // 为Electron开发模式添加特殊处理
    proxy: {
      '/electron': {
        target: 'http://localhost:5173',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/electron/, ''),
      },
    },
  },
  define: {
    // 为Electron开发模式定义全局变量
    __ELECTRON__: JSON.stringify(true),
  },
});