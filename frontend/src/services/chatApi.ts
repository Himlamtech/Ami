/**
 * Chat API Service - Maps to backend endpoints
 * Based on: smart_query_routes.py, multimodal_routes.py, chat_history_routes.py
 */

import { api } from '@/lib/api'

// ===== Types matching backend DTOs =====

export type ResponseIntent =
    | 'general_answer'
    | 'file_request'
    | 'form_request'
    | 'procedure_guide'
    | 'contact_info'
    | 'navigation'

export type SourceType = 'document' | 'web_search' | 'direct_knowledge'

export interface SourceReference {
    source_type: SourceType
    document_id?: string
    title?: string
    url?: string
    chunk_text?: string
    relevance_score: number
}

export interface Artifact {
    artifact_id: string
    document_id: string
    file_name: string
    artifact_type: string
    download_url: string
    preview_url?: string
    size_bytes: number
    size_display: string
    is_fillable: boolean
    fill_fields: string[]
}

export interface SmartQueryRequest {
    query: string
    session_id?: string
    collection?: string
    user_info?: Record<string, unknown>
    enable_rag?: boolean
    top_k?: number
    similarity_threshold?: number
    temperature?: number
    max_tokens?: number
}

export interface SmartQueryResponse {
    content: string
    intent: ResponseIntent
    artifacts: Artifact[]
    sources: SourceReference[]
    metadata: {
        model_used: string
        processing_time_ms: number
        tokens_used: number
        sources_count: number
        artifacts_count: number
        has_fillable_form: boolean
    }
}

// Chat Session types
export interface ChatSession {
    id: string
    user_id: string
    title: string
    message_count: number
    created_at: string
    updated_at: string
}

export interface ChatMessage {
    id: string
    session_id: string
    role: 'user' | 'assistant'
    content: string
    created_at: string
}

export interface ChatHistoryResponse {
    session: ChatSession
    messages: ChatMessage[]
    total: number
}

// Voice query types (multimodal)
export interface VoiceQueryResponse {
    transcription: string
    response: string
    sources: SourceReference[]
    confidence: number
    duration_seconds: number
    session_id?: string
}

// ===== API Functions =====

export const chatApi = {
    /**
     * Smart query with RAG and artifact detection
     * POST /api/v1/smart-query
     */
    smartQuery: (request: SmartQueryRequest): Promise<SmartQueryResponse> => {
        return api.post('/smart-query', request)
    },

    /**
     * Smart query with streaming response
     * POST /api/v1/smart-query/stream
     */
    smartQueryStream: (
        request: SmartQueryRequest,
        onChunk: (content: string) => void,
        onDone?: () => void
    ) => {
        return api.stream('/smart-query/stream', request, (data) => {
            try {
                const parsed = JSON.parse(data)
                if (parsed.content) {
                    onChunk(parsed.content)
                }
            } catch {
                // Raw text chunk
                onChunk(data)
            }
        }, onDone)
    },

    /**
     * Voice query - send audio file
     * POST /api/v1/multimodal/voice-query
     */
    voiceQuery: async (
        audioBlob: Blob,
        sessionId?: string
    ): Promise<VoiceQueryResponse> => {
        const formData = new FormData()
        formData.append('audio', audioBlob, 'audio.webm')
        if (sessionId) {
            formData.append('session_id', sessionId)
        }
        formData.append('language', 'vi')

        const response = await fetch('/api/v1/multimodal/voice-query', {
            method: 'POST',
            body: formData,
        })

        if (!response.ok) {
            throw new Error('Voice query failed')
        }

        return response.json()
    },

    // ===== Session Management =====

    /**
     * Create new chat session
     * POST /api/v1/chat/sessions
     */
    createSession: (title?: string): Promise<ChatSession> => {
        return api.post('/chat/sessions', { title })
    },

    /**
     * Get chat sessions
     * GET /api/v1/chat/sessions
     */
    getSessions: (params?: {
        skip?: number
        limit?: number
    }): Promise<{ sessions: ChatSession[], total: number }> => {
        return api.get('/chat/sessions', params)
    },

    /**
     * Get session history
     * GET /api/v1/chat/sessions/:id/history
     */
    getSessionHistory: (sessionId: string): Promise<ChatHistoryResponse> => {
        return api.get(`/chat/sessions/${sessionId}/history`)
    },

    /**
     * Delete session
     * DELETE /api/v1/chat/sessions/:id
     */
    deleteSession: (sessionId: string): Promise<void> => {
        return api.delete(`/chat/sessions/${sessionId}`)
    },

    /**
     * Update session title
     * PUT /api/v1/chat/sessions/:id
     */
    updateSession: (sessionId: string, title: string): Promise<ChatSession> => {
        return api.put(`/chat/sessions/${sessionId}`, { title })
    },
}

export default chatApi
