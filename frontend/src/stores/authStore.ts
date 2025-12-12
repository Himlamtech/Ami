import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { UserProfile } from '@/types/chat'
import { authApi } from '@/features/auth/api/authApi'

interface AuthState {
    user: (UserProfile & { role?: string }) | null
    token: string | null
    isAuthenticated: boolean
    isLoading: boolean
    login: (email: string, password: string) => Promise<void>
    register: (data: { email: string; password: string; full_name: string }) => Promise<void>
    logout: () => void
    setUser: (user: UserProfile | null) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            token: null,
            isAuthenticated: false,
            isLoading: false,

            login: async (email: string, password: string) => {
                set({ isLoading: true })
                try {
                    const response = await authApi.login({ email, password })

                    const user: UserProfile & { role?: string } = {
                        id: response.user_id,
                        email: response.email,
                        displayName: response.full_name,
                        major: 'Công nghệ thông tin', // Default
                        academicLevel: 'undergraduate', // Default
                        interests: [],
                        role: response.role
                    }

                    set({
                        user,
                        token: response.token,
                        isAuthenticated: true,
                        isLoading: false
                    })
                } catch (error) {
                    set({ isLoading: false })
                    throw error
                }
            },

            register: async (data) => {
                set({ isLoading: true })
                try {
                    const response = await authApi.register({
                        email: data.email,
                        password: data.password,
                        password_confirmation: data.password, // Frontend validates match
                        full_name: data.full_name
                    })

                    const user: UserProfile & { role?: string } = {
                        id: response.user_id,
                        email: response.email,
                        displayName: response.full_name,
                        major: 'Công nghệ thông tin',
                        academicLevel: 'undergraduate',
                        interests: [],
                        role: response.role
                    }

                    set({
                        user,
                        token: response.token,
                        isAuthenticated: true,
                        isLoading: false
                    })
                } catch (error) {
                    set({ isLoading: false })
                    throw error
                }
            },

            logout: () => {
                set({ user: null, token: null, isAuthenticated: false })
            },

            setUser: (user) => {
                set({ user, isAuthenticated: !!user })
            },
        }),
        {
            name: 'ami-auth',
        }
    )
)
