import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:11121/api/v1';

const client = axios.create({
    baseURL: API_URL,
    headers: { 'Content-Type': 'application/json' },
});

export const userApi = {
    // Chat endpoints
    chat: {
        query: (data: any) => client.post('/smart-query', data),
        getSessions: () => client.get('/chat/sessions'),
    },
    // Bookmarks endpoints
    bookmarks: {
        create: (data: any) => client.post('/bookmarks', data),
        list: () => client.get('/bookmarks'),
        delete: (id: string) => client.delete(`/bookmarks/${id}`),
    },
    // Profile endpoints
    profile: {
        get: (userId: string) => client.get(`/profile/${userId}`),
        update: (userId: string, data: any) => client.put(`/profile/${userId}`, data),
        setPreferences: (userId: string, data: any) =>
            client.put(`/profile/${userId}/preferences`, data),
    },
};
