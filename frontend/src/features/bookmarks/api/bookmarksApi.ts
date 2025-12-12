
import { api } from '@/lib/api'

export interface Bookmark {
    id: string
    user_id: string
    session_id: string
    message_id: string
    query: string
    response: string
    title?: string
    tags: string[]
    notes?: string
    folder?: string
    created_at: string
    updated_at: string
}

export interface BookmarkListResponse {
    bookmarks: Bookmark[]
    total: number
    skip: number
    limit: number
}

export const bookmarksApi = {
    getAll: () => api.get<BookmarkListResponse>('/bookmarks'),

    delete: (id: string) => api.delete(`/bookmarks/${id}`),

    search: (query: string, tags?: string) =>
        api.get<BookmarkListResponse>('/bookmarks/search', { q: query, tags }),

    create: (data: Partial<Bookmark>) => api.post<Bookmark>('/bookmarks', data)
}
