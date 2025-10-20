import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@styles': path.resolve(__dirname, './src/styles'),
            '@components': path.resolve(__dirname, './src/components'),
        },
    },
    server: {
        port: 6009,
        host: '127.0.0.1'
    },
    build: {
        outDir: 'dist',
        sourcemap: false
    }
})

