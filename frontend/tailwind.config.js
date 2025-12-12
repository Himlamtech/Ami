/** @type {import('tailwindcss').Config} */
export default {
    darkMode: ["class"],
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Primary - PTIT Red
                primary: {
                    50: '#FEF2F2',
                    100: '#FDE8E8',
                    200: '#FECACA',
                    300: '#FCA5A5',
                    400: '#F87171',
                    500: '#DC2626',
                    600: '#B91C1C',
                    700: '#991B1B',
                    800: '#7F1D1D',
                    900: '#450A0A',
                    DEFAULT: '#DC2626',
                    foreground: '#FFFFFF',
                },
                // Secondary - Blue Trust
                secondary: {
                    50: '#EFF6FF',
                    100: '#DBEAFE',
                    200: '#BFDBFE',
                    300: '#93C5FD',
                    400: '#60A5FA',
                    500: '#3B82F6',
                    600: '#2563EB',
                    700: '#1D4ED8',
                    800: '#1E40AF',
                    900: '#1E3A8A',
                    DEFAULT: '#3B82F6',
                    foreground: '#FFFFFF',
                },
                // Neutral - Gray
                neutral: {
                    50: '#F9FAFB',
                    100: '#F3F4F6',
                    200: '#E5E7EB',
                    300: '#D1D5DB',
                    400: '#9CA3AF',
                    500: '#6B7280',
                    600: '#4B5563',
                    700: '#374151',
                    800: '#1F2937',
                    900: '#111827',
                },
                // Semantic
                success: '#10B981',
                warning: '#F59E0B',
                error: '#EF4444',
                info: '#3B82F6',
                // shadcn/ui compatibility
                border: '#E5E7EB',
                input: '#E5E7EB',
                ring: '#DC2626',
                background: '#FFFFFF',
                foreground: '#111827',
                destructive: {
                    DEFAULT: '#EF4444',
                    foreground: '#FFFFFF',
                },
                muted: {
                    DEFAULT: '#F3F4F6',
                    foreground: '#6B7280',
                },
                accent: {
                    DEFAULT: '#F3F4F6',
                    foreground: '#111827',
                },
                popover: {
                    DEFAULT: '#FFFFFF',
                    foreground: '#111827',
                },
                card: {
                    DEFAULT: '#FFFFFF',
                    foreground: '#111827',
                },
            },
            fontFamily: {
                sans: ['Inter', 'system-ui', 'sans-serif'],
                mono: ['JetBrains Mono', 'monospace'],
            },
            fontSize: {
                'display': ['36px', { lineHeight: '1.25', fontWeight: '700' }],
                'h1': ['30px', { lineHeight: '1.25', fontWeight: '700' }],
                'h2': ['24px', { lineHeight: '1.25', fontWeight: '600' }],
                'h3': ['20px', { lineHeight: '1.25', fontWeight: '600' }],
                'h4': ['16px', { lineHeight: '1.25', fontWeight: '600' }],
                'body-lg': ['18px', { lineHeight: '1.5', fontWeight: '400' }],
                'body': ['16px', { lineHeight: '1.5', fontWeight: '400' }],
                'body-sm': ['14px', { lineHeight: '1.5', fontWeight: '400' }],
                'caption': ['12px', { lineHeight: '1.5', fontWeight: '400' }],
            },
            spacing: {
                'xs': '4px',
                'sm': '8px',
                'md': '16px',
                'lg': '24px',
                'xl': '32px',
                '2xl': '48px',
                '3xl': '64px',
            },
            borderRadius: {
                'sm': '4px',
                'md': '8px',
                'lg': '12px',
                'xl': '16px',
            },
            boxShadow: {
                'sm': '0 1px 2px rgba(0,0,0,0.05)',
                'DEFAULT': '0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)',
                'md': '0 4px 6px rgba(0,0,0,0.1)',
                'lg': '0 10px 15px rgba(0,0,0,0.1)',
                'xl': '0 20px 25px rgba(0,0,0,0.1)',
            },
        },
    },
    plugins: [],
}
