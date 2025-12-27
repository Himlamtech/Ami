import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:11121/api/v1';

const client = axios.create({
    baseURL: `${API_URL}/admin`,
    headers: {
        'Content-Type': 'application/json',
        'X-Admin-API-Key': localStorage.getItem('adminToken') || '',
    },
});

export const adminApi = {
    // Analytics endpoints
    analytics: {
        overview: () => client.get('/analytics/overview'),
        costs: () => client.get('/analytics/costs'),
        usage: () => client.get('/analytics/usage'),
    },
    // Feedback endpoints
    feedback: {
        dashboard: () => client.get('/feedback/dashboard'),
    },
    // Conversation endpoints
    conversations: {
        list: (filters?: any) => client.get('/conversations', { params: filters }),
        detail: (id: string) => client.get(`/conversations/${id}`),
    },
    // User management endpoints
    users: {
        list: (filters?: any) => client.get('/users', { params: filters }),
        detail: (id: string) => client.get(`/users/${id}`),
        sessions: (id: string) => client.get(`/users/${id}/sessions`),
    },
    // Document management endpoints
    documents: {
        list: () => client.get('/documents'),
        delete: (id: string) => client.delete(`/documents/${id}`),
    },
};
