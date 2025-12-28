export interface Message {
    id: string
    role: 'user' | 'assistant'
    content: string
    timestamp: string
    sources?: Source[]
    webSources?: string[]
    tools?: ToolProgress[]
    toolStage?: string
    steps?: string[]
    feedback?: Feedback
    isStreaming?: boolean
    attachments?: Attachment[]
}

export interface Source {
    id: string
    title: string
    score: number
    url?: string
}

export interface Feedback {
    type: 'helpful' | 'not_helpful'
    comment?: string
    categories?: string[]
}

export interface ToolProgress {
    id: string
    type: string
    status: 'pending' | 'running' | 'success' | 'failed' | 'skipped'
    reasoning?: string
    error?: string
}

export interface Conversation {
    id: string
    title: string
    preview: string
    messageCount: number
    lastActive: string
    status: 'active' | 'archived'
    hasFeedback?: boolean
}

export interface ChatSession {
    sessionId: string
    userId: string
    messages: Message[]
    createdAt: string
    updatedAt: string
}

export interface SendMessageRequest {
    message: string
    sessionId?: string
    attachments?: Attachment[]
}

export interface Attachment {
    type: 'image' | 'document'
    name: string
    url: string
    size: number
}

export interface SuggestedQuestion {
    id: string
    text: string
    category?: string
    relevance_score?: number
    source?: string
}

export type ThinkingMode = 'fast' | 'thinking'

export interface UserProfile {
    id: string
    name?: string
    displayName?: string
    email?: string
    studentId?: string
    major?: string
    year?: string
    academicLevel?: string
    interests?: string[]
    avatar?: string
    preferences?: UserPreferences
}

export interface UserPreferences {
    detailLevel: 'brief' | 'detailed'
    language: 'vi' | 'en'
    notifications: boolean
}
