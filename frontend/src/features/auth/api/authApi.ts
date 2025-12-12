import { api } from '@/lib/api'

export interface LoginRequest {
    email: string
    password: string
}

export interface RegisterRequest {
    email: string
    password: string
    password_confirmation: string
    full_name: string
}

export interface AuthResponse {
    user_id: string
    token: string
    role: string
    full_name: string
    email: string
}

export const authApi = {
    login: (data: LoginRequest): Promise<AuthResponse> =>
        api.post('/auth/login', data),

    register: (data: RegisterRequest): Promise<AuthResponse> =>
        api.post('/auth/register', {
            email: data.email,
            password: data.password,
            password_confirmation: data.password_confirmation,
            full_name: data.full_name
        }),
}
