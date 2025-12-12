export interface DashboardStats {
    totalRequests: number
    requestsChange: number
    activeUsers: number
    usersChange: number
    avgLatency: number
    latencyChange: number
    errorRate: number
    errorRateChange: number
}

export interface CostBreakdown {
    provider: string
    amount: number
    percentage: number
}

export interface FeedbackSummary {
    total: number
    helpfulRate: number
    avgRating: number
    byCategory: { category: string; count: number }[]
}

export interface TopQuery {
    query: string
    count: number
    avgScore: number
    feedbackRate: number
}

export interface AdminConversation {
    id: string
    userId: string
    userName: string
    studentId: string
    title: string
    preview: string
    messageCount: number
    lastActive: string
    status: 'active' | 'issues' | 'multiple_issues' | 'archived'
    hasNegativeFeedback: boolean
}

export interface FeedbackItem {
    id: string
    type: 'helpful' | 'not_helpful' | 'incomplete' | 'incorrect'
    userId: string
    userName: string
    studentId: string
    question: string
    response: string
    comment?: string
    categories: string[]
    sources: { title: string; score: number; outdated?: boolean }[]
    createdAt: string
    reviewed: boolean
}

export interface KnowledgeGap {
    id: string
    topic: string
    queryCount: number
    avgScore: number
    feedbackRate: number
    sampleQueries: string[]
    bestMatch?: { title: string; score: number; outdated?: boolean }
    suggestedAction: string
    status: 'todo' | 'in_progress' | 'resolved' | 'ignored'
    priority: 'high' | 'medium' | 'low'
}

export interface AdminUser {
    id: string
    name: string
    studentId: string
    major: string
    year: string
    sessionCount: number
    avgRating: number
    lastActive: string
    topInterests: string[]
}

export interface AnalyticsData {
    period: string
    requests: number
    users: number
    cost: number
}

export interface PromptTemplate {
    id: string
    name: string
    content: string
    variables: string[]
    version: number
    isActive: boolean
    lastUpdated: string
}

export interface ModelConfig {
    chat: {
        provider: 'openai' | 'anthropic' | 'gemini'
        model: string
        temperature: number
        maxTokens: number
    }
    embedding: {
        model: string
        dimension: number
    }
    rag: {
        topK: number
        minScore: number
    }
}

export interface BudgetAlert {
    threshold: number
    alertPercentage: number
    notifyEmail: boolean
}

export interface ModelConfig {
    provider: 'openai' | 'anthropic' | 'gemini'
    model: string
    temperature: number
    maxTokens: number
}
