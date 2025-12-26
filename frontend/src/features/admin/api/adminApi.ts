import { api } from '@/lib/api'
import type {
    DashboardStats,
    AdminConversation,
    FeedbackItem,
    KnowledgeGap,
    AdminUser,
    PromptTemplate,
    ModelConfig,
    DataSource,
    DataSourceStats,
    MonitorTarget,
    PendingUpdate,
    PendingUpdateDetail,
} from '@/types/admin'

export const adminApi = {
    // Dashboard
    getDashboardStats: async () => {
        try {
            // Fetch metrics from analytics overview
            const metrics = await api.get<any>('/admin/analytics/overview', { period: 'today' })
            // Fetch counts from system stats
            const counts = await api.get<any>('/admin/stats')

            return {
                totalRequests: metrics.requests || 0,
                requestsChange: 0,
                activeUsers: metrics.active_users || 0,
                usersChange: 0,
                avgLatency: metrics.avg_latency_ms || 0,
                latencyChange: 0,
                errorRate: metrics.error_rate || 0,
                errorRateChange: 0,
                totalDocuments: counts.total_documents || 0,
                totalSessions: counts.total_chat_sessions || 0,
                totalChunks: counts.total_chunks || 0
            } as DashboardStats
        } catch (error) {
            console.error('[Admin API] Failed to fetch dashboard stats:', error)
            // Return empty stats on error
            return {
                totalRequests: 0,
                requestsChange: 0,
                activeUsers: 0,
                usersChange: 0,
                avgLatency: 0,
                latencyChange: 0,
                errorRate: 0,
                errorRateChange: 0,
                totalDocuments: 0,
                totalSessions: 0,
                totalChunks: 0
            } as DashboardStats
        }
    },

    // Conversations
    getConversations: async (params?: {
        page?: number
        limit?: number
        search?: string
        hasNegativeFeedback?: boolean
    }) => {
        const response = await api.get<{ items: any[]; total: number }>('/admin/conversations', params)
        return {
            data: response.items.map((item: any) => ({
                id: item.id,
                userId: item.user_id,
                userName: item.user_name || 'User',
                studentId: 'N/A', // Not available in list view yet
                title: item.title,
                preview: '...', // Not available in list view yet
                messageCount: item.message_count,
                lastActive: item.last_activity,
                status: item.status as any,
                hasNegativeFeedback: item.has_negative_feedback || false
            })),
            total: response.total
        }
    },

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

    // Data Sources
    getDataSources: (params?: {
        skip?: number
        limit?: number
        status?: string
        category?: string
    }) => api.get<{ items: DataSource[]; total: number; skip: number; limit: number }>('/admin/data-sources', params),

    getDataSourceStats: async () => {
        const response = await api.get<{ items: DataSource[]; total: number }>('/admin/data-sources', { skip: 0, limit: 100 })
        const sources = response.items

        return {
            total: response.total, // Use total from API response, not sources.length
            active: sources.filter(s => s.status === 'active').length,
            inactive: sources.filter(s => s.status === 'inactive').length,
            error: sources.filter(s => s.status === 'error').length,
            by_type: Object.entries(
                sources.reduce((acc, s) => {
                    acc[s.source_type] = (acc[s.source_type] || 0) + 1
                    return acc
                }, {} as Record<string, number>)
            ).map(([type, count]) => ({ type, count })),
            by_category: Object.entries(
                sources.reduce((acc, s) => {
                    acc[s.category] = (acc[s.category] || 0) + 1
                    return acc
                }, {} as Record<string, number>)
            ).map(([category, count]) => ({ category, count }))
        } as DataSourceStats
    },

    getDataSource: (id: string) => api.get<DataSource>(`/admin/data-sources/${id}`),

    createDataSource: (data: any) => api.post<DataSource>('/admin/data-sources', data),

    updateDataSource: (id: string, data: any) => api.put<DataSource>(`/admin/data-sources/${id}`, data),

    deleteDataSource: (id: string) => api.delete(`/admin/data-sources/${id}`),

    testDataSource: (data: any) => api.post('/admin/data-sources/test', data),

    triggerCrawl: (id: string) => api.post(`/admin/data-sources/${id}/crawl`),

    // Monitor Targets
    getMonitorTargets: (params?: { skip?: number; limit?: number }) =>
        api.get<{ items: MonitorTarget[]; total: number; skip: number; limit: number }>(
            '/admin/monitor-targets',
            params
        ),

    createMonitorTarget: (data: {
        name: string
        url: string
        collection: string
        category: string
        interval_hours: number
        selector?: string
        metadata?: Record<string, string>
    }) => api.post<MonitorTarget>('/admin/monitor-targets', data),

    updateMonitorTarget: (id: string, data: Partial<Omit<MonitorTarget, 'id'>>) =>
        api.put<MonitorTarget>(`/admin/monitor-targets/${id}`, data),

    deleteMonitorTarget: (id: string) => api.delete<{ success: boolean }>(`/admin/monitor-targets/${id}`),

    // Pending approvals
    getPendingUpdates: (params?: {
        skip?: number
        limit?: number
        status?: string
        detection_type?: string
        category?: string
    }) =>
        api.get<{ items: PendingUpdate[]; total: number; skip: number; limit: number }>(
            '/admin/approvals',
            params
        ),

    getPendingUpdateDetail: (id: string) =>
        api.get<PendingUpdateDetail>(`/admin/approvals/${id}`),

    approvePendingUpdate: (id: string, note?: string) =>
        api.post(`/admin/approvals/${id}/approve`, note ? { note } : undefined),

    rejectPendingUpdate: (id: string, note?: string) =>
        api.post(`/admin/approvals/${id}/reject`, note ? { note } : undefined),
}
