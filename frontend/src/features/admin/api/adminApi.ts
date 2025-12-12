import { api } from '@/lib/api'
import type {
    DashboardStats,
    AdminConversation,
    FeedbackItem,
    KnowledgeGap,
    AdminUser,
    PromptTemplate,
    ModelConfig,
} from '@/types/admin'

export const adminApi = {
    // Dashboard
    getDashboardStats: () => api.get<DashboardStats>('/admin/analytics/overview'),

    // Conversations
    getConversations: (params?: {
        page?: number
        limit?: number
        search?: string
        hasNegativeFeedback?: boolean
    }) => api.get<{ data: AdminConversation[]; total: number }>('/admin/conversations', params),

    getConversationDetail: (sessionId: string) =>
        api.get<AdminConversation>(`/admin/conversations/${sessionId}`),

    archiveConversation: (sessionId: string) =>
        api.put(`/admin/conversations/${sessionId}/archive`),

    deleteConversation: (sessionId: string) =>
        api.delete(`/admin/conversations/${sessionId}`),

    // Feedback
    getFeedbackDashboard: () => api.get('/admin/feedback/dashboard'),

    getFeedbackList: (params?: {
        page?: number
        limit?: number
        type?: string
        category?: string
    }) => api.get<{ data: FeedbackItem[]; total: number }>('/admin/feedback', params),

    markFeedbackReviewed: (feedbackId: string) =>
        api.put(`/admin/feedback/${feedbackId}/reviewed`),

    // Analytics
    getAnalytics: (params?: { period?: string; groupBy?: string }) =>
        api.get('/admin/analytics', params),

    getCostBreakdown: (params?: { period?: string }) =>
        api.get('/admin/analytics/costs', params),

    // Knowledge
    getKnowledgeGaps: () => api.get<KnowledgeGap[]>('/admin/knowledge/gaps'),

    updateGapStatus: (gapId: string, status: KnowledgeGap['status']) =>
        api.put(`/admin/knowledge/gaps/${gapId}`, { status }),

    // Users
    getUsers: (params?: {
        page?: number
        limit?: number
        search?: string
        major?: string
    }) => api.get<{ data: AdminUser[]; total: number }>('/admin/users', params),

    getUserDetail: (userId: string) => api.get<AdminUser>(`/admin/users/${userId}`),

    // Settings
    getPromptTemplates: () => api.get<PromptTemplate[]>('/admin/config/prompts'),

    updatePromptTemplate: (id: string, content: string) =>
        api.put(`/admin/config/prompts/${id}`, { content }),

    getModelConfig: () => api.get<ModelConfig>('/admin/config/models'),

    updateModelConfig: (config: Partial<ModelConfig>) =>
        api.put('/admin/config/models', config),
}
