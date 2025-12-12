export interface DashboardStats {
    totalRequests: number
    requestsChange: number
    activeUsers: number
    usersChange: number
    avgLatency: number
    latencyChange: number
    errorRate: number
    errorRateChange: number
    totalDocuments?: number
    totalSessions?: number
    totalChunks?: number
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

export interface DataSource {
    id: string
    name: string
    description?: string
    base_url: string
    source_type: 'web_crawler' | 'api' | 'file_upload' | 'database'
    category: 'academic' | 'administrative' | 'general'
    data_type: 'html' | 'pdf' | 'json' | 'markdown'
    schedule_cron?: string
    status: 'active' | 'inactive' | 'error' | 'pending'
    last_crawl_at?: string
    next_crawl_at?: string
    crawl_count: number
    success_count: number
    error_count: number
    last_error?: string
    created_at: string
    updated_at: string
    crawl_config?: {
        selectors?: string[]
        exclude_selectors?: string[]
        max_depth?: number
        max_pages?: number
        follow_links?: boolean
        allowed_domains?: string[]
        rate_limit_delay?: number
        timeout?: number
        user_agent?: string
    }
    auth_config?: {
        auth_type: 'none' | 'basic' | 'bearer' | 'api_key' | 'cookie'
        has_credentials: boolean
    }
}

export interface DataSourceStats {
    total: number
    active: number
    inactive: number
    error: number
    by_type: { type: string; count: number }[]
    by_category: { category: string; count: number }[]
}
