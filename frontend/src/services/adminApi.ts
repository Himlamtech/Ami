/**
 * Admin API Service - Direct backend connection
 */

import { api } from '@/lib/api'

// ===== Types =====

export interface AdminSession {
    id: string
    user_id: string
    title: string
    message_count: number
    status: string
    created_at: string
}

export interface FeedbackDashboardResponse {
    overview: {
        total: number
        helpful_count: number
        not_helpful_count: number
        helpful_ratio: number
    }
    trends: Array<{ date: string; total: number; helpful: number; not_helpful: number }>
}

export interface AnalyticsOverview {
    requests: number
    active_users: number
    avg_latency_ms: number
    error_rate: number
}

export interface KnowledgeHealthResponse {
    stats: {
        documents: number
        chunks: number
        collections: number
        coverage: number
    }
}

export interface CostAnalyticsResponse {
    total: number
    by_provider: Array<{ name: string; cost: number; percentage: number }>
    by_model: Array<{ name: string; cost: number; tokens: number }>
}

export interface AdminStats {
    documents_count: number
    chunks_count: number
    sessions_count: number
    users_count: number
}

// ===== API Functions =====

export const adminApi = {
    getConversations: (params?: { page?: number; limit?: number; status?: string }) =>
        api.get<{ conversations: AdminSession[] }>('/admin/conversations', params as Record<string, string | number | boolean | undefined>),

    getFeedbackDashboard: (period = '30d'): Promise<FeedbackDashboardResponse> =>
        api.get('/admin/feedback/dashboard', { period }),

    getAnalyticsOverview: (period = 'today'): Promise<AnalyticsOverview> =>
        api.get('/admin/analytics/overview', { period }),

    getCostAnalytics: (params?: { period?: string }): Promise<CostAnalyticsResponse> =>
        api.get('/admin/analytics/costs', params),

    getKnowledgeHealth: (): Promise<KnowledgeHealthResponse> =>
        api.get('/admin/knowledge/health'),

    getStats: (): Promise<AdminStats> => api.get('/admin/stats'),
}

export default adminApi
