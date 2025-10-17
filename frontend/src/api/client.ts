import axios from 'axios'
import { useAuthStore } from '../store/authStore'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:6008/api/v1'

export const apiClient = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
})

// Request interceptor to add auth token
apiClient.interceptors.request.use((config) => {
    const token = useAuthStore.getState().token
    if (token) {
        config.headers.Authorization = `Bearer ${token}`
    }
    return config
})

// Response interceptor to handle auth errors
apiClient.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            useAuthStore.getState().logout()
        }
        return Promise.reject(error)
    }
)

// Auth API
export const authAPI = {
    login: async (username: string, password: string) => {
        const response = await apiClient.post('/auth/login', { username, password })
        return response.data
    },
    me: async () => {
        const response = await apiClient.get('/auth/me')
        return response.data
    },
}

// Documents API
export const documentsAPI = {
    list: async (params: {
        skip?: number
        limit?: number
        is_active?: boolean
        collection?: string
    }) => {
        const response = await apiClient.get('/admin/documents/', { params })
        return response.data
    },
    get: async (id: string) => {
        const response = await apiClient.get(`/admin/documents/${id}`)
        return response.data
    },
    upload: async (file: File, collection: string = 'default') => {
        const formData = new FormData()
        formData.append('file', file)
        const response = await apiClient.post(`/admin/documents/?collection=${collection}`, formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
        return response.data
    },
    update: async (id: string, data: { filename?: string; collection?: string; metadata?: any }) => {
        const response = await apiClient.put(`/admin/documents/${id}`, data)
        return response.data
    },
    softDelete: async (id: string) => {
        await apiClient.delete(`/admin/documents/${id}`)
    },
    restore: async (id: string) => {
        const response = await apiClient.post(`/admin/documents/${id}/restore`)
        return response.data
    },
    listCollections: async () => {
        const response = await apiClient.get('/admin/documents/collections/list')
        return response.data
    },
}

