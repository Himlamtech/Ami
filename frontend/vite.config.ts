import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
    plugins: [react()],
    resolve: {
        alias: {
            '@': fileURLToPath(new URL('./src', import.meta.url)),
        },
    },
    server: {
        port: 11120,
        proxy: {
            '/api': {
                target: 'http://localhost:11121',
                changeOrigin: true,
            },
        },
    },
    build: {
        chunkSizeWarningLimit: 600,
        rollupOptions: {
            output: {
                manualChunks: (id) => {
                    if (id.includes('node_modules')) {
                        if (id.includes('react-markdown') || id.includes('react-syntax-highlighter') || id.includes('refractor') || id.includes('prismjs')) {
                            return 'markdown'
                        }
                        if (id.includes('recharts') || id.includes('d3')) {
                            return 'charts'
                        }
                        if (id.includes('@radix-ui')) {
                            return 'radix'
                        }
                        if (id.includes('react-router')) {
                            return 'router'
                        }
                        if (id.includes('@tanstack') || id.includes('zustand')) {
                            return 'state'
                        }
                    }
                },
            },
        },
    },
})
