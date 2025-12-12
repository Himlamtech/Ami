/**
 * Chat API - Direct backend connection
 */

import { api } from '@/lib/api'
import type { Message, SuggestedQuestion } from '@/types/chat'

export interface SmartQueryRequest {
    query: string
    session_id?: string
    collection?: string
    enable_rag?: boolean
    top_k?: number
    temperature?: number
    max_tokens?: number
}

export interface SmartQueryResponse {
    content: string
    intent: string
    sources: Array<{
        document_id?: string
        title?: string
        url?: string
        relevance_score: number
    }>
    metadata: {
        model_used: string
        processing_time_ms: number
        tokens_used: number
    }
}

export interface Session {
    id: string
    user_id: string
    title: string
    message_count: number
    created_at: string
    updated_at: string
}

export const chatApi = {
    smartQuery: (request: SmartQueryRequest): Promise<SmartQueryResponse> =>
        api.post('/smart-query', request),

    smartQueryStream: (
        request: SmartQueryRequest,
        onMessage: (chunk: string) => void,
        onDone?: () => void
    ) => api.stream('/smart-query/stream', request, onMessage, onDone),

    getSessions: async (): Promise<Session[]> => {
        const response = await api.get<{ sessions: Session[] }>('/chat/sessions')
        return response.sessions || []
    },

    getConversation: (sessionId: string): Promise<{ messages: Message[] }> =>
        api.get(`/chat/sessions/${sessionId}/history`),

    createSession: (title?: string): Promise<Session> =>
        api.post('/chat/sessions', { title }),

    deleteConversation: (sessionId: string): Promise<void> =>
        api.delete(`/chat/sessions/${sessionId}`),

    submitFeedback: (messageId: string, data: { type: string; comment?: string }): Promise<void> =>
        api.post(`/feedback/${messageId}`, data),

    getSuggestions: (): Promise<SuggestedQuestion[]> =>
        api.get('/suggestions'),

    sendMessage: async (data: { message: string; sessionId?: string }) => {
        const response = await chatApi.smartQuery({
            query: data.message,
            session_id: data.sessionId,
        })

        const message: Message = {
            id: Date.now().toString(),
            role: 'assistant',
            content: response.content,
            timestamp: new Date().toISOString(),
            sources: response.sources.map((s, idx) => ({
                id: s.document_id || `source-${idx}`,
                title: s.title || 'Unknown',
                url: s.url,
                score: s.relevance_score
            }))
        }

        return { message, suggestions: [] as SuggestedQuestion[] }
    },
}

export default chatApi
