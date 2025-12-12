import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { UserProfile } from '@/types/chat'

interface AuthState {
    user: UserProfile | null
    isAuthenticated: boolean
    isLoading: boolean
    login: (email: string, password: string) => Promise<void>
    logout: () => void
    setUser: (user: UserProfile | null) => void
}

export const useAuthStore = create<AuthState>()(
    persist(
        (set) => ({
            user: null,
            isAuthenticated: false,
            isLoading: false,

            login: async (email: string, _password: string) => {
                set({ isLoading: true })

                // Simulate API call - Replace with real backend auth
                await new Promise(resolve => setTimeout(resolve, 800))

                // Demo: admin@ptit.edu.vn is admin, others are user
                const isAdmin = email.toLowerCase().includes('admin')
                const user: UserProfile = {
                    id: '1',
                    email,
                    displayName: isAdmin ? 'Admin PTIT' : 'Sinh viên PTIT',
                    major: 'Công nghệ thông tin',
                    academicLevel: 'undergraduate',
                    interests: [],
                }

                set({ user, isAuthenticated: true, isLoading: false })
            },

            logout: () => {
                set({ user: null, isAuthenticated: false })
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
