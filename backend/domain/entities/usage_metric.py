"""Usage metric domain entities for analytics tracking."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum


class RequestStatus(Enum):
    """Status of API request."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"


class LLMProvider(Enum):
    """LLM provider."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    LOCAL = "local"


@dataclass
class UsageMetric:
    """
    Usage metric entity for tracking API requests.

    Tracks each API request for analytics and monitoring.
    """

    # Identity
    id: str

    # Request info
    endpoint: str
    method: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None

    # Performance
    latency_ms: int = 0  # Response time in milliseconds
    status: RequestStatus = RequestStatus.SUCCESS
    status_code: int = 200
    error_message: Optional[str] = None

    # Request details
    request_size_bytes: int = 0
    response_size_bytes: int = 0

    # Context
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    def is_error(self) -> bool:
        """Check if request resulted in error."""
        return self.status != RequestStatus.SUCCESS

    def is_slow(self, threshold_ms: int = 3000) -> bool:
        """Check if request was slow."""
        return self.latency_ms > threshold_ms

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "endpoint": self.endpoint,
            "method": self.method,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "latency_ms": self.latency_ms,
            "status": self.status.value,
            "status_code": self.status_code,
            "error_message": self.error_message,
            "request_size_bytes": self.request_size_bytes,
            "response_size_bytes": self.response_size_bytes,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class LLMUsage:
    """
    LLM usage entity for tracking token usage and costs.

    Tracks each LLM call for cost monitoring.
    """

    # Identity
    id: str

    # LLM info
    provider: LLMProvider
    model: str

    # Token usage
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0

    # Cost (in USD)
    input_cost: float = 0.0
    output_cost: float = 0.0
    total_cost: float = 0.0

    # Context
    use_case: str = "chat"  # chat, rag, summary, etc.
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    message_id: Optional[str] = None

    # Performance
    latency_ms: int = 0

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    def calculate_cost(
        self, input_price_per_1k: float, output_price_per_1k: float
    ) -> None:
        """Calculate cost based on token prices."""
        self.input_cost = (self.input_tokens / 1000) * input_price_per_1k
        self.output_cost = (self.output_tokens / 1000) * output_price_per_1k
        self.total_cost = self.input_cost + self.output_cost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "provider": self.provider.value,
            "model": self.model,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "input_cost": self.input_cost,
            "output_cost": self.output_cost,
            "total_cost": self.total_cost,
            "use_case": self.use_case,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "message_id": self.message_id,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class DailyUsageStats:
    """
    Aggregated daily usage statistics.

    Pre-computed daily stats for faster dashboard queries.
    """

    # Identity
    id: str
    date: datetime  # Date only (no time)

    # Request stats
    total_requests: int = 0
    successful_requests: int = 0
    error_requests: int = 0

    # User stats
    unique_users: int = 0
    unique_sessions: int = 0

    # Performance stats
    avg_latency_ms: float = 0.0
    p50_latency_ms: float = 0.0
    p95_latency_ms: float = 0.0
    p99_latency_ms: float = 0.0

    # LLM stats
    total_tokens: int = 0
    total_cost: float = 0.0
    cost_by_provider: Dict[str, float] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)
    cost_by_use_case: Dict[str, float] = field(default_factory=dict)

    # Endpoint stats
    requests_by_endpoint: Dict[str, int] = field(default_factory=dict)

    def error_rate(self) -> float:
        """Calculate error rate."""
        if self.total_requests == 0:
            return 0.0
        return self.error_requests / self.total_requests

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "date": self.date.isoformat(),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "error_requests": self.error_requests,
            "unique_users": self.unique_users,
            "unique_sessions": self.unique_sessions,
            "avg_latency_ms": self.avg_latency_ms,
            "p50_latency_ms": self.p50_latency_ms,
            "p95_latency_ms": self.p95_latency_ms,
            "p99_latency_ms": self.p99_latency_ms,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "cost_by_provider": self.cost_by_provider,
            "cost_by_model": self.cost_by_model,
            "cost_by_use_case": self.cost_by_use_case,
            "requests_by_endpoint": self.requests_by_endpoint,
            "error_rate": self.error_rate(),
        }
