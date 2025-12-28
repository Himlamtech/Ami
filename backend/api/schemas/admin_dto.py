"""Admin DTOs for API schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ===== Common =====


class PaginationParams(BaseModel):
    """Common pagination parameters."""

    page: int = Field(default=1, ge=1)
    limit: int = Field(default=20, ge=1, le=100)

    @property
    def skip(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel):
    """Common paginated response."""

    total: int
    page: int
    pages: int
    limit: int


class DateRangeParams(BaseModel):
    """Date range filter parameters."""

    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


# ===== Conversation DTOs =====


class AdminSessionResponse(BaseModel):
    """Admin view of chat session."""

    id: str
    user_id: str
    user_name: Optional[str] = None
    title: str
    message_count: int
    status: str  # active, archived, deleted
    has_negative_feedback: bool = False
    last_activity: datetime
    created_at: datetime


class AdminSessionListResponse(PaginatedResponse):
    """Paginated list of sessions."""

    items: List[AdminSessionResponse]


class AdminMessageResponse(BaseModel):
    """Admin view of chat message."""

    id: str
    role: str
    content: str
    sources: List[Dict[str, Any]] = []
    feedback: Optional[Dict[str, Any]] = None
    created_at: datetime


class AdminSessionDetailResponse(BaseModel):
    """Detailed session view for admin."""

    session: AdminSessionResponse
    messages: List[AdminMessageResponse]
    user_profile: Optional[Dict[str, Any]] = None


class ExportRequest(BaseModel):
    """Export sessions request."""

    session_ids: List[str]
    format: str = Field(default="json", pattern="^(json|pdf|csv)$")


class ExportResponse(BaseModel):
    """Export response."""

    export_id: str
    status: str
    download_url: Optional[str] = None


# ===== Feedback DTOs =====


class FeedbackOverview(BaseModel):
    """Feedback dashboard overview."""

    total: int
    helpful_count: int
    not_helpful_count: int
    helpful_ratio: float
    avg_rating: float
    trend_vs_last_period: float = 0.0


class FeedbackTrend(BaseModel):
    """Feedback trend data point."""

    date: str
    total: int
    helpful: int
    not_helpful: int
    avg_rating: Optional[float] = None


class FeedbackDistribution(BaseModel):
    """Feedback distribution by type/category."""

    by_type: Dict[str, int]
    by_category: Dict[str, int]


class FeedbackDashboardResponse(BaseModel):
    """Complete feedback dashboard response."""

    overview: FeedbackOverview
    trends: List[FeedbackTrend]
    distribution: FeedbackDistribution


class AdminFeedbackResponse(BaseModel):
    """Admin view of feedback."""

    id: str
    session_id: str
    message_id: str
    user_id: str
    feedback_type: str
    rating: Optional[int] = None
    categories: List[str] = []
    comment: Optional[str] = None
    status: str
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime


class AdminFeedbackDetailResponse(BaseModel):
    """Detailed feedback with context."""

    feedback: AdminFeedbackResponse
    message_context: Dict[str, Any]
    user_info: Optional[Dict[str, Any]] = None


class AdminFeedbackListResponse(PaginatedResponse):
    """Paginated list of feedback."""

    items: List[AdminFeedbackResponse]


class ReviewFeedbackRequest(BaseModel):
    """Request to mark feedback as reviewed."""

    reviewed: bool = True
    notes: Optional[str] = None


class FeedbackIssue(BaseModel):
    """Top issue from feedback."""

    topic: str
    count: int
    examples: List[Dict[str, Any]] = []


class TopIssuesResponse(BaseModel):
    """Top issues response."""

    issues: List[FeedbackIssue]


# ===== Knowledge Quality DTOs =====


class KnowledgeHealthStats(BaseModel):
    """Knowledge base health statistics."""

    documents: int
    chunks: int
    collections: int
    avg_chunk_score: float
    coverage: float
    last_updated: datetime


class KnowledgeHealthResponse(BaseModel):
    """Knowledge health response."""

    stats: KnowledgeHealthStats
    coverage_by_category: List[Dict[str, Any]]
    freshness: Dict[str, int]  # {recent: n, stale: n, outdated: n}


class KnowledgeGapResponse(BaseModel):
    """Knowledge gap item."""

    id: str
    topic: str
    query_count: int
    avg_score: float = Field(default=0.0, alias="avg_confidence")
    sample_queries: List[str] = Field(default_factory=list, alias="example_queries")
    status: str
    priority: str = "medium"
    first_detected_at: Optional[datetime] = Field(default=None, alias="created_at")
    last_query_at: Optional[datetime] = Field(default=None, alias="updated_at")
    description: Optional[str] = None
    suggested_action: Optional[str] = None
    category: Optional[str] = None

    class Config:
        populate_by_name = True


class KnowledgeGapListResponse(PaginatedResponse):
    """Paginated list of knowledge gaps."""

    gaps: List[KnowledgeGapResponse]


class GapDetailResponse(BaseModel):
    """Detailed knowledge gap."""

    id: str
    topic: str
    description: Optional[str] = None
    example_queries: List[str] = []
    query_count: int
    avg_confidence: float
    category: Optional[str] = None
    priority: str = "medium"
    status: str
    suggested_action: Optional[str] = None
    notes: Optional[str] = None
    related_queries: List[Dict[str, Any]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UpdateGapStatusRequest(BaseModel):
    """Request to update gap status."""

    status: str = Field(..., pattern="^(todo|in_progress|resolved|dismissed)$")
    document_id: Optional[str] = None
    notes: Optional[str] = None


class LowConfidenceQuery(BaseModel):
    """Low confidence query."""

    query: str
    score: float
    response: Optional[str] = None
    feedback: Optional[str] = None
    timestamp: datetime


class LowConfidenceQueryResponse(BaseModel):
    """Low confidence query item for API."""

    id: str
    query: str
    max_score: float
    results_count: int
    timestamp: datetime
    user_id: Optional[str] = None


class LowConfidenceResponse(BaseModel):
    """Low confidence queries response."""

    queries: List[LowConfidenceQuery]


class CoverageItem(BaseModel):
    """Coverage by category item."""

    name: str
    doc_count: int
    query_coverage: float


class CoverageResponse(BaseModel):
    """Coverage response."""

    by_category: List[CoverageItem]


class CoverageAnalysisResponse(BaseModel):
    """Coverage analysis response."""

    total_topics: int
    well_covered: List[str]
    needs_improvement: List[str]
    poor_coverage: List[str]
    gaps_by_category: Dict[str, int]


# ===== User Profile DTOs =====


class AdminUserResponse(BaseModel):
    """Admin view of user profile."""

    user_id: str
    major: Optional[str] = None
    level: Optional[str] = None
    interests: List[str] = []
    sessions_count: int = 0
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserDetailResponse(BaseModel):
    """Detailed user profile."""

    user_id: str
    major: Optional[str] = None
    level: Optional[str] = None
    interests: List[str] = []
    preferences: Dict[str, Any] = {}
    sessions_count: int = 0
    total_messages: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    last_active: Optional[datetime] = None
    created_at: Optional[datetime] = None


class UserSessionResponse(BaseModel):
    """User session for admin."""

    session_id: str
    title: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    is_archived: bool = False


class UserAnalysisResponse(BaseModel):
    """User behavior analysis."""

    user_id: str
    total_sessions: int
    total_queries: int
    avg_queries_per_session: float
    top_topics: List[Dict[str, Any]]
    activity_by_day: Dict[str, int]
    engagement_score: int


class InterestProfile(BaseModel):
    """User interest profile."""

    topic: str
    score: float
    count: int


class UserInsightsResponse(BaseModel):
    """Active users insights."""

    period: str
    total_users: int
    active_users: int
    new_users: int
    returning_users: int
    by_major: Dict[str, int]
    by_level: Dict[str, int]


class AdminUserListResponse(PaginatedResponse):
    """Paginated list of users."""

    users: List[AdminUserResponse]
