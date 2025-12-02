import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
    plugins: [react()],
    base: '/',  // Changed from '/v2/' - standalone service
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@styles': path.resolve(__dirname, './src/styles'),
            '@components': path.resolve(__dirname, './src/components'),
        },
    },
    server: {
        port: 11120,
        host: '127.0.0.1'
    },
    build: {
        outDir: 'dist',
        sourcemap: false
    }
})

