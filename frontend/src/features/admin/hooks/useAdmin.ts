import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { adminApi } from '../api/adminApi'

export function useAnalytics(period?: string) {
    const dashboardQuery = useQuery({
        queryKey: ['admin', 'dashboard'],
        queryFn: adminApi.getDashboardStats,
        staleTime: 1000 * 60 * 2, // 2 minutes
    })

    return {
        dashboard: dashboardQuery.data,
        isLoading: dashboardQuery.isLoading,
        refetch: () => {
            dashboardQuery.refetch()
        },
    }
}

export function useConversations(params?: Parameters<typeof adminApi.getConversations>[0]) {
    const queryClient = useQueryClient()

    const conversationsQuery = useQuery({
        queryKey: ['admin', 'conversations', params],
        queryFn: () => adminApi.getConversations(params),
    })

    const archiveMutation = useMutation({
        mutationFn: adminApi.archiveConversation,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'conversations'] })
        },
    })

    const deleteMutation = useMutation({
        mutationFn: adminApi.deleteConversation,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'conversations'] })
        },
    })

    return {
        conversations: conversationsQuery.data?.data ?? [],
        total: conversationsQuery.data?.total ?? 0,
        isLoading: conversationsQuery.isLoading,
        archiveConversation: archiveMutation.mutate,
        deleteConversation: deleteMutation.mutate,
        refetch: conversationsQuery.refetch,
    }
}

export function useFeedback(params?: Parameters<typeof adminApi.getFeedbackList>[0]) {
    const queryClient = useQueryClient()

    const feedbackQuery = useQuery({
        queryKey: ['admin', 'feedback', params],
        queryFn: () => adminApi.getFeedbackList(params),
    })

    const dashboardQuery = useQuery({
        queryKey: ['admin', 'feedback', 'dashboard'],
        queryFn: adminApi.getFeedbackDashboard,
    })

    const markReviewedMutation = useMutation({
        mutationFn: adminApi.markFeedbackReviewed,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'feedback'] })
        },
    })

    return {
        feedback: feedbackQuery.data?.data ?? [],
        total: feedbackQuery.data?.total ?? 0,
        dashboard: dashboardQuery.data,
        isLoading: feedbackQuery.isLoading,
        markReviewed: markReviewedMutation.mutate,
        refetch: feedbackQuery.refetch,
    }
}

export function useKnowledge() {
    const queryClient = useQueryClient()

    const gapsQuery = useQuery({
        queryKey: ['admin', 'knowledge', 'gaps'],
        queryFn: adminApi.getKnowledgeGaps,
    })

    const updateStatusMutation = useMutation({
        mutationFn: ({ id, status }: { id: string; status: string }) =>
            adminApi.updateGapStatus(id, status as 'todo' | 'in_progress' | 'resolved' | 'ignored'),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'knowledge'] })
        },
    })

    return {
        gaps: gapsQuery.data ?? [],
        isLoading: gapsQuery.isLoading,
        updateGapStatus: updateStatusMutation.mutate,
        refetch: gapsQuery.refetch,
    }
}

export function useUsers(params?: Parameters<typeof adminApi.getUsers>[0]) {
    const usersQuery = useQuery({
        queryKey: ['admin', 'users', params],
        queryFn: () => adminApi.getUsers(params),
    })

    return {
        users: usersQuery.data?.data ?? [],
        total: usersQuery.data?.total ?? 0,
        isLoading: usersQuery.isLoading,
        refetch: usersQuery.refetch,
    }
}

export function useSettings() {
    const queryClient = useQueryClient()

    const promptsQuery = useQuery({
        queryKey: ['admin', 'config', 'prompts'],
        queryFn: adminApi.getPromptTemplates,
    })

    const modelQuery = useQuery({
        queryKey: ['admin', 'config', 'models'],
        queryFn: adminApi.getModelConfig,
    })

    const updatePromptMutation = useMutation({
        mutationFn: ({ id, content }: { id: string; content: string }) =>
            adminApi.updatePromptTemplate(id, content),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'config', 'prompts'] })
        },
    })

    const updateModelMutation = useMutation({
        mutationFn: adminApi.updateModelConfig,
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['admin', 'config', 'models'] })
        },
    })

    return {
        prompts: promptsQuery.data ?? [],
        modelConfig: modelQuery.data,
        isLoading: promptsQuery.isLoading || modelQuery.isLoading,
        updatePrompt: updatePromptMutation.mutate,
        updateModelConfig: updateModelMutation.mutate,
    }
}
