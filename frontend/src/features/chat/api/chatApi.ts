/**
 * Chat API - Direct backend connection
 */

import { api } from '@/lib/api'
import type { Attachment, Message, SuggestedQuestion, Source, ToolProgress } from '@/types/chat'

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

export interface OrchestrateRequest {
    query: string
    session_id?: string
    user_id?: string
}

export interface OrchestrateResponse {
    answer: string
    session_id?: string
    message_id?: string
    request_id?: string
    primary_tool?: string
    tools?: Array<{
        type?: string
        status?: string
        reasoning?: string
        result?: Record<string, any>
        error?: string
    }>
    metrics?: Record<string, any>
    success?: boolean
    error?: string
}

export interface Session {
    id: string
    user_id: string
    title: string
    message_count: number
    created_at: string
    updated_at: string
}

export interface VoiceQueryResponse {
    transcription: string
    response: string
    sources: any[]
}

export interface ImageQueryResponse {
    description: string
    response: string
    extracted_text?: string
    detected_objects?: string[]
    related_documents?: any[]
}

interface ChatMessageDTO {
    id: string
    session_id: string
    role: 'user' | 'assistant' | 'system'
    content: string
    created_at: string
    attachments?: Attachment[]
    metadata?: Record<string, any>
}

interface ChatHistoryDTO {
    session: Session
    messages: ChatMessageDTO[]
    total: number
}

const mapSources = (metadata?: Record<string, any>): Source[] | undefined => {
    const rawSources = metadata?.sources
    if (!Array.isArray(rawSources)) {
        return undefined
    }
    return rawSources.map((source, idx) => ({
        id: source.id || source.document_id || `source-${idx}`,
        title: source.title || 'Unknown',
        url: source.url,
        score: source.score ?? source.relevance_score ?? 0,
    }))
}

const mapWebSources = (metadata?: Record<string, any>): string[] | undefined => {
    const rawSources = metadata?.web_sources
    if (!Array.isArray(rawSources) || rawSources.length === 0) {
        return undefined
    }
    return rawSources.filter((url) => typeof url === 'string' && url.length > 0)
}

const mapTools = (metadata?: Record<string, any>): ToolProgress[] | undefined => {
    const rawTools = metadata?.tools
    if (!Array.isArray(rawTools)) {
        return undefined
    }
    return rawTools.map((tool, idx) => ({
        id: tool.id || `tool-${idx}`,
        type: tool.type || 'unknown',
        status: tool.status || 'pending',
        reasoning: tool.reasoning,
        error: tool.error,
    }))
}

export const chatApi = {
    orchestrate: (request: OrchestrateRequest): Promise<OrchestrateResponse> =>
        api.post('/chat/orchestrate', request),
    orchestrateStream: (
        request: OrchestrateRequest,
        onMessage: (chunk: string) => void,
        onDone?: () => void
    ) => api.stream('/chat/orchestrate/stream', request, onMessage, onDone),

    smartQuery: (request: SmartQueryRequest): Promise<SmartQueryResponse> =>
        api.post('/smart-query', request),

    smartQueryStream: (
        request: SmartQueryRequest,
        onMessage: (chunk: string) => void,
        onDone?: () => void
    ) => api.stream('/smart-query/stream', request, onMessage, onDone),

    sendVoiceQuery: (audioBlob: Blob): Promise<VoiceQueryResponse> => {
        const formData = new FormData()
        formData.append('audio', audioBlob, 'recording.webm')
        return api.postFormData<VoiceQueryResponse>('/multimodal/voice-query', formData)
    },

    sendImageQuery: (imageFile: File, question?: string): Promise<ImageQueryResponse> => {
        const formData = new FormData()
        formData.append('image', imageFile)
        if (question) {
            formData.append('question', question)
        }
        return api.postFormData<ImageQueryResponse>('/multimodal/image-query', formData)
    },

    getSessions: async (): Promise<Session[]> => {
        const response = await api.get<Session[]>('/chat/sessions')
        return response || []
    },

    getConversation: async (sessionId: string): Promise<{ session: Session; messages: Message[] }> => {
        const response = await api.get<ChatHistoryDTO>(`/chat/sessions/${sessionId}/history`)
        return {
            session: response.session,
            messages: response.messages.map((message) => {
                const isAssistant = message.role === 'assistant' || message.role === 'system'
                return {
                    id: message.id,
                    role: isAssistant ? 'assistant' : 'user',
                    content: message.content,
                    timestamp: message.created_at,
                    attachments: message.attachments ?? [],
                    sources: mapSources(message.metadata),
                    tools: mapTools(message.metadata),
                    webSources: mapWebSources(message.metadata),
                }
            }),
        }
    },

    logMessage: async (data: {
        sessionId: string
        role: 'user' | 'assistant'
        content: string
        attachments?: Attachment[]
        metadata?: Record<string, any>
    }): Promise<Message> => {
        const response = await api.post<ChatMessageDTO>('/chat/messages', {
            session_id: data.sessionId,
            role: data.role,
            content: data.content,
            attachments: data.attachments,
            metadata: data.metadata,
        })

        const isAssistant = response.role === 'assistant' || response.role === 'system'

        return {
            id: response.id,
            role: isAssistant ? 'assistant' : 'user',
            content: response.content,
            timestamp: response.created_at,
            attachments: response.attachments ?? [],
            sources: mapSources(response.metadata),
        }
    },

    createSession: (title?: string): Promise<Session> =>
        api.post('/chat/sessions', { title }),

    deleteConversation: (sessionId: string): Promise<void> =>
        api.delete(`/chat/sessions/${sessionId}`),


    getSuggestions: async (params?: {
        count?: number
        includePopular?: boolean
        includePersonalized?: boolean
    }): Promise<SuggestedQuestion[]> => {
        const response = await api.get<{ suggestions: any[] }>('/suggestions', {
            count: params?.count,
            include_popular: params?.includePopular,
            include_personalized: params?.includePersonalized,
        })
        return response.suggestions.map((s) => ({
            id: s.id,
            text: s.text,
            category: s.category,
            relevance_score: s.relevance_score,
            source: s.source,
        }))
    },

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

    submitFeedback: async (data: {
        sessionId: string
        messageId: string
        userId: string
        feedbackType: 'helpful' | 'not_helpful'
    }) => {
        return api.post('/feedback/submit', {
            session_id: data.sessionId,
            message_id: data.messageId,
            user_id: data.userId,
            feedback_type: data.feedbackType,
        })
    },
}

export default chatApi
