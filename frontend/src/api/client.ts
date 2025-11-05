import axios, { AxiosInstance } from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:6008/api/v1'

// Types
export interface Message {
    role: 'system' | 'user' | 'assistant'
    content: string
}

export interface ChatRequest {
    messages: Message[]
    thinking_mode?: 'fast' | 'balance' | 'thinking'
    system_prompt?: string
    rag_config?: {
        enabled: boolean
        top_k: number
        similarity_threshold: number
        include_sources: boolean
        metadata_filter?: Record<string, unknown>
    }
    web_search_config?: {
        enabled: boolean
        max_results: number
        timeout: number
    }
    generation_config?: {
        temperature: number
        max_tokens?: number
        top_p: number
        frequency_penalty: number
        presence_penalty: number
    }
    collection?: string
    stream?: boolean
    session_id?: string
    auto_generate_title?: boolean
}

export interface ChatResponse {
    message: Message
    sources?: unknown[]
    web_sources?: unknown[]
    metadata: Record<string, unknown>
    session_id?: string
}

export interface ChatSession {
    id: string
    user_id: string
    title: string
    summary?: string
    message_count: number
    created_at: string
    updated_at: string
    last_message_at: string
    is_archived: boolean
    is_deleted: boolean
}

export interface ChatMessage {
    id: string
    session_id: string
    role: 'user' | 'assistant'
    content: string
    metadata?: Record<string, unknown>
    created_at: string
    edited_at?: string
    is_deleted: boolean
}

// User Management Types
export interface User {
    id: string
    username: string
    email: string
    full_name?: string
    role: 'admin' | 'user'
    is_active: boolean
    created_at: string
    last_login?: string
}

export interface UserCreate {
    username: string
    email: string
    password: string
    full_name?: string
    role?: 'admin' | 'user'
    is_active?: boolean
}

export interface UserUpdate {
    email?: string
    full_name?: string
    role?: 'admin' | 'user'
    is_active?: boolean
    password?: string
}

export interface UserListResponse {
    users: User[]
    total: number
    skip: number
    limit: number
}

// Log Management Types
export type LogLevel = 'debug' | 'info' | 'warning' | 'error' | 'critical'

export type LogAction =
    | 'login'
    | 'logout'
    | 'login_failed'
    | 'chat_message'
    | 'chat_response'
    | 'chat_error'
    | 'document_upload'
    | 'document_delete'
    | 'document_view'
    | 'crawl_start'
    | 'crawl_success'
    | 'crawl_error'
    | 'user_create'
    | 'user_update'
    | 'user_delete'
    | 'system_start'
    | 'system_error'
    | 'api_error'

export interface LogResponse {
    id: string
    level: LogLevel
    action: LogAction
    message: string
    user_id?: string
    username?: string
    session_id?: string
    metadata: Record<string, unknown>
    ip_address?: string
    user_agent?: string
    created_at: string
}

export interface LogCreate {
    level: LogLevel
    action: LogAction
    message: string
    user_id?: string
    username?: string
    session_id?: string
    metadata?: Record<string, unknown>
    ip_address?: string
    user_agent?: string
}

export interface LogListResponse {
    logs: LogResponse[]
    total: number
    skip: number
    limit: number
}

export interface LogStatsResponse {
    total_logs: number
    by_level: Record<string, number>
    by_action: Record<string, number>
    recent_errors: number
    active_users: number
}

export interface LogQueryParams {
    skip?: number
    limit?: number
    level?: LogLevel
    action?: LogAction
    user_id?: string
    username?: string
    start_date?: string
    end_date?: string
    search?: string
}

export interface UploadResponse {
    doc_ids: string[]
    chunk_count: number
    collection: string
    message: string
}

export interface ModelInfo {
    name: string
    type: 'llm' | 'embedding' | 'vector_store'
    available: boolean
}

export interface HealthStatus {
    status: 'healthy' | 'degraded'
    providers: Record<string, boolean | string>
    databases: Record<string, string>
    services: Record<string, string>
}

class APIClient {
    private client: AxiosInstance

    constructor() {
        this.client = axios.create({
            baseURL: API_URL,
            headers: {
                'Content-Type': 'application/json',
            },
        })

        // Add auth interceptor
        this.client.interceptors.request.use((config) => {
            const token = localStorage.getItem('auth_token')
            if (token) {
                config.headers.Authorization = `Bearer ${token}`
            }
            return config
        })
    }

    // ============= Chat Endpoints =============
    async generateChat(request: ChatRequest): Promise<ChatResponse> {
        const response = await this.client.post<ChatResponse>('/generate/chat', request)
        return response.data
    }

    // ============= Chat History Endpoints =============
    async createSession(title?: string): Promise<ChatSession> {
        const response = await this.client.post<ChatSession>('/chat-history/sessions', {
            title: title || 'New Chat',
        })
        return response.data
    }

    async listSessions(
        skip = 0,
        limit = 50,
        isArchived?: boolean,
        search?: string
    ): Promise<{ sessions: ChatSession[]; total_count: number }> {
        const response = await this.client.get<{ sessions: ChatSession[]; total_count: number }>(
            '/chat-history/sessions',
            {
                params: { skip, limit, is_archived: isArchived, search },
            }
        )
        return response.data
    }

    async getSession(
        sessionId: string,
        includeMessages = true
    ): Promise<ChatSession & { messages?: ChatMessage[] }> {
        const response = await this.client.get<ChatSession & { messages?: ChatMessage[] }>(
            `/chat-history/sessions/${sessionId}`,
            {
                params: { include_messages: includeMessages },
            }
        )
        return response.data
    }

    async updateSession(
        sessionId: string,
        updates: { title?: string; summary?: string }
    ): Promise<ChatSession> {
        const response = await this.client.patch<ChatSession>(`/chat-history/sessions/${sessionId}`, updates)
        return response.data
    }

    async deleteSession(sessionId: string): Promise<void> {
        await this.client.delete(`/chat-history/sessions/${sessionId}`)
    }

    async archiveSession(sessionId: string): Promise<void> {
        await this.client.post(`/chat-history/sessions/${sessionId}/archive`)
    }

    async restoreSession(sessionId: string): Promise<void> {
        await this.client.post(`/chat-history/sessions/${sessionId}/restore`)
    }

    async addMessage(
        sessionId: string,
        role: 'user' | 'assistant',
        content: string,
        metadata?: Record<string, unknown>
    ): Promise<ChatMessage> {
        const response = await this.client.post<ChatMessage>(
            `/chat-history/sessions/${sessionId}/messages`,
            {
                session_id: sessionId,
                role,
                content,
                metadata: metadata || {},
                attachments: [],
            }
        )
        return response.data
    }

    async listMessages(
        sessionId: string,
        skip = 0,
        limit = 100
    ): Promise<{ messages: ChatMessage[]; count: number }> {
        const response = await this.client.get<{ messages: ChatMessage[]; count: number }>(
            `/chat-history/sessions/${sessionId}/messages`,
            {
                params: { skip, limit },
            }
        )
        return response.data
    }

    async summarizeSession(sessionId: string): Promise<{ title: string; summary: string }> {
        const response = await this.client.post<{ title: string; summary: string }>(
            `/chat-history/sessions/${sessionId}/summarize`
        )
        return response.data
    }

    // ============= Vector Database Endpoints =============
    async uploadFile(file: File, collection = 'default'): Promise<UploadResponse> {
        const formData = new FormData()
        formData.append('file', file)
        formData.append('collection', collection)

        const response = await this.client.post<UploadResponse>('/vectordb/upload/file', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
        })
        return response.data
    }

    async uploadContent(
        content: string,
        collection = 'default',
        metadata?: Record<string, unknown>
    ): Promise<UploadResponse> {
        const response = await this.client.post<UploadResponse>('/vectordb/upload', {
            content,
            collection,
            metadata,
        })
        return response.data
    }

    // ============= Config Endpoints =============
    async getModels(): Promise<ModelInfo[]> {
        const response = await this.client.get<ModelInfo[]>('/config/models')
        return response.data
    }

    async getProviders(): Promise<Record<string, unknown>> {
        const response = await this.client.get<Record<string, unknown>>('/config/providers')
        return response.data
    }

    async getHealth(): Promise<HealthStatus> {
        const response = await this.client.get<HealthStatus>('/config/health')
        return response.data
    }

    async getStats(collection?: string): Promise<Record<string, unknown>> {
        const response = await this.client.get<Record<string, unknown>>('/vectordb/stats', {
            params: { collection },
        })
        return response.data
    }

    async getCollections(): Promise<string[]> {
        const response = await this.client.get<string[]>('/vectordb/collections')
        return response.data
    }

    async listDocuments(
        collection?: string,
        limit = 50,
        offset = 0
    ): Promise<{
        documents: Array<{
            id: string
            content: string
            metadata: Record<string, unknown>
            collection: string
            created_at: string
            embedding_dims?: number
        }>
        total_count: number
        limit: number
        offset: number
    }> {
        const response = await this.client.get('/vectordb/list', {
            params: { collection, limit, offset },
        })
        return response.data
    }

    async getDocument(docId: string): Promise<{
        id: string
        content: string
        metadata: Record<string, unknown>
        collection: string
        is_active: boolean
        created_at?: string
    }> {
        const response = await this.client.get(`/vectordb/${docId}`)
        return response.data
    }

    async deleteDocument(docId: string): Promise<{ deleted_count: number; message: string }> {
        const response = await this.client.delete(`/vectordb/${docId}`)
        return response.data
    }

    // ============= Crawl Endpoints =============
    async scrapeUrl(
        url: string,
        collection = 'web_content',
        onlyMainContent = true,
        autoIngest = true
    ): Promise<{
        success: boolean
        url: string
        markdown?: string
        content_length?: number
        duration_seconds: number
        error?: string
        ingested: boolean
        doc_id?: string
        chunk_count?: number
    }> {
        const response = await this.client.post('/crawl/scrape', {
            url,
            collection,
            only_main_content: onlyMainContent,
            auto_ingest: autoIngest,
        })
        return response.data
    }

    async crawlUrl(
        url: string,
        maxDepth = 2,
        limit = 10,
        collection = 'web_content',
        autoIngest = true
    ): Promise<{
        success: boolean
        url: string
        total_pages: number
        ingested_pages: number
        duration_seconds: number
        error?: string
    }> {
        const response = await this.client.post('/crawl/crawl', {
            url,
            max_depth: maxDepth,
            limit,
            collection,
            auto_ingest: autoIngest,
        })
        return response.data
    }

    // ============= Admin Endpoints =============
    async listUsers(): Promise<unknown[]> {
        const response = await this.client.get('/admin/users')
        return response.data
    }

    async createUser(username: string, password: string, email?: string): Promise<unknown> {
        const response = await this.client.post('/admin/users', {
            username,
            password,
            email,
        })
        return response.data
    }

    // ============= User Management Endpoints =============
    async getUsers(skip = 0, limit = 50, is_active?: boolean): Promise<UserListResponse> {
        const params: Record<string, unknown> = { skip, limit }
        if (is_active !== undefined) params.is_active = is_active
        const response = await this.client.get<UserListResponse>('/auth/users', { params })
        return response.data
    }

    async getUserById(userId: string): Promise<User> {
        const response = await this.client.get<User>(`/auth/users/${userId}`)
        return response.data
    }

    async registerUser(userData: UserCreate): Promise<User> {
        const response = await this.client.post<User>('/auth/register', userData)
        return response.data
    }

    async updateUser(userId: string, userData: UserUpdate): Promise<User> {
        const response = await this.client.put<User>(`/auth/users/${userId}`, userData)
        return response.data
    }

    async deleteUser(userId: string): Promise<void> {
        await this.client.delete(`/auth/users/${userId}`)
    }

    // ============= Log Management Endpoints =============
    async getLogs(params: LogQueryParams): Promise<LogListResponse> {
        const response = await this.client.get<LogListResponse>('/logs', { params })
        return response.data
    }

    async getLogStats(days = 7): Promise<LogStatsResponse> {
        const response = await this.client.get<LogStatsResponse>('/logs/stats', {
            params: { days },
        })
        return response.data
    }

    async createLog(logData: LogCreate): Promise<LogResponse> {
        const response = await this.client.post<LogResponse>('/logs', logData)
        return response.data
    }

    async clearOldLogs(days = 90): Promise<void> {
        await this.client.delete('/logs', { params: { days } })
    }
}

export const apiClient = new APIClient()

