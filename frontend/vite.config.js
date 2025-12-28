import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';
export default defineConfig({
    base: '/',
    plugins: [react()],
    envDir: path.resolve(__dirname, '..'),
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
        },
    },
    server: {
        port: 11120,
        proxy: {
            '/api': {
                target: 'http://localhost:11121',  // Dev local backend
                changeOrigin: true,
            },
        },
    },
    preview: {
        port: 11120,
        proxy: {
            '/api': {
                target: 'http://localhost:11101',  // Docker backend (exposed port)
                changeOrigin: true,
            },
        },
    },
});
