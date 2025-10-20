import { create } from 'zustand'

interface User {
    id: string
    username: string
    email?: string
}

interface AuthStore {
    token: string | null
    user: User | null
    isLoading: boolean
    setToken: (token: string | null) => void
    setUser: (user: User | null) => void
    setIsLoading: (loading: boolean) => void
    logout: () => void
    initialize: () => void
}

export const useAuthStore = create<AuthStore>((set) => ({
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
    initialize: () => {
        const token = localStorage.getItem('auth_token')
        set({ token })
    },
}))

