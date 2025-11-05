import { create } from 'zustand'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:6008/api/v1'

interface User {
    id: string
    username: string
    email?: string
    role?: 'admin' | 'user'
}

interface AuthStore {
    token: string | null
    user: User | null
    isLoading: boolean
    setToken: (token: string | null) => void
    setUser: (user: User | null) => void
    setIsLoading: (loading: boolean) => void
    logout: () => void
    initialize: () => Promise<void>
}

export const useAuthStore = create<AuthStore>((set, get) => ({
    token: localStorage.getItem('auth_token'),
    user: null,
    isLoading: false,
    setToken: (token) => {
        if (token) {
            localStorage.setItem('auth_token', token)
        } else {
            localStorage.removeItem('auth_token')
        }
        set({ token })
    },
    setUser: (user) => set({ user }),
    setIsLoading: (loading) => set({ isLoading: loading }),
    logout: () => {
        localStorage.removeItem('auth_token')
        set({ token: null, user: null })
    },
    initialize: async () => {
        const token = localStorage.getItem('auth_token')
        set({ token })

        // If token exists, fetch user info
        if (token) {
            try {
                const response = await fetch(`${API_URL}/auth/me`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                })

                if (response.ok) {
                    const userData = await response.json()
                    set({ user: userData })
                } else {
                    // Token invalid, clear it
                    localStorage.removeItem('auth_token')
                    set({ token: null, user: null })
                }
            } catch (error) {
                console.error('Failed to fetch user info:', error)
                // Keep token but user will be null
            }
        }
    },
}))

