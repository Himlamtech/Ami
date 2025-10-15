"""
Domain models and DTOs.
Comprehensive request/response models with extensive configuration options.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class ThinkingMode(str, Enum):
    """Thinking/reasoning modes for generation."""

    DISABLED = "disabled"
    CHAIN_OF_THOUGHT = "chain_of_thought"
    STEP_BY_STEP = "step_by_step"
    REASONING = "reasoning"


class ChunkConfig(BaseModel):
    """Configuration for document chunking."""

    chunk_size: int = Field(default=512, ge=100, le=4000)
    chunk_overlap: int = Field(default=50, ge=0, le=500)
    strategy: Literal["fixed", "semantic", "sentence"] = "fixed"


class RAGConfig(BaseModel):
    """Configuration for RAG retrieval."""

    enabled: bool = True
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    rerank: bool = False
    include_sources: bool = True
    metadata_filter: Optional[Dict[str, Any]] = None


class GenerationConfig(BaseModel):
    """Configuration for LLM generation."""

    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=None, ge=1, le=100000)
    top_p: float = Field(default=1.0, ge=0.0, le=1.0)
    frequency_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    presence_penalty: float = Field(default=0.0, ge=-2.0, le=2.0)
    stop_sequences: Optional[List[str]] = None


class Message(BaseModel):
    """Chat message model."""

    role: Literal["system", "user", "assistant"] = "user"
    content: str


class ChatRequest(BaseModel):
    """Comprehensive chat request with RAG support."""

    messages: List[Message]
    model: Optional[str] = Field(
        default=None, description="LLM provider: openai, gemini, anthropic"
    )
    thinking_mode: ThinkingMode = ThinkingMode.DISABLED
    system_prompt: Optional[str] = None
    rag_config: RAGConfig = Field(default_factory=RAGConfig)
    generation_config: GenerationConfig = Field(default_factory=GenerationConfig)
    embedding_provider: Optional[str] = None
    vector_store: Optional[str] = None
    collection: str = "default"
    stream: bool = False


class ChatResponse(BaseModel):
    """Chat response model."""

    message: Message
    sources: Optional[List[Dict[str, Any]]] = None
    usage: Optional[Dict[str, int]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class UploadRequest(BaseModel):
    """Document upload request."""

    content: Optional[str] = None
    file_path: Optional[str] = None
    collection: str = "default"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunk_config: ChunkConfig = Field(default_factory=ChunkConfig)
    embedding_provider: Optional[str] = None
    vector_store: Optional[str] = None


class UploadResponse(BaseModel):
    """Document upload response."""

    doc_ids: List[str]
    chunk_count: int
    collection: str
    message: str


class SearchRequest(BaseModel):
    """Vector search request."""

    query: str
    collection: str = "default"
    top_k: int = Field(default=5, ge=1, le=50)
    similarity_threshold: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata_filter: Optional[Dict[str, Any]] = None
    embedding_provider: Optional[str] = None
    vector_store: Optional[str] = None


class SearchResponse(BaseModel):
    """Vector search response."""

    results: List[Dict[str, Any]]
    count: int
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentInfo(BaseModel):
    """Document information model."""

    id: str
    content: str
    metadata: Dict[str, Any]
    collection: str
    created_at: datetime
    embedding_dims: Optional[int] = None


class ListDocumentsRequest(BaseModel):
    """List documents request."""

    collection: Optional[str] = None
    metadata_filter: Optional[Dict[str, Any]] = None
    limit: int = Field(default=50, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    vector_store: Optional[str] = None


class ListDocumentsResponse(BaseModel):
    """List documents response."""

    documents: List[DocumentInfo]
    total_count: int
    limit: int
    offset: int


class DeleteResponse(BaseModel):
    """Delete operation response."""

    deleted_count: int
    message: str


class ModelInfo(BaseModel):
    """Model/provider information."""

    name: str
    type: Literal["llm", "embedding", "vector_store"]
    available: bool
    config: Dict[str, Any] = Field(default_factory=dict)


class ProviderStatus(BaseModel):
    """Provider status information."""

    providers: Dict[str, List[ModelInfo]]
    default_providers: Dict[str, str]


class DatabaseStats(BaseModel):
    """Vector database statistics."""

    total_documents: int
    total_chunks: int
    collections: List[str]
    storage_size: Optional[str] = None
    vector_store: str


class CrawlStatus(str, Enum):
    """Status of a crawl task."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class CrawlTask(BaseModel):
    """Task for crawling a URL."""

    url: str
    title: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    output_filename: Optional[str] = None
    status: CrawlStatus = CrawlStatus.PENDING
    error: Optional[str] = None


class CrawlResult(BaseModel):
    """Result of a crawl operation."""

    task: CrawlTask
    success: bool
    content: Optional[str] = None
    content_length: int = 0
    error: Optional[str] = None
    duration_seconds: float = 0.0
    saved_path: Optional[str] = None


class CrawlBatchReport(BaseModel):
    """Report for a batch of crawl operations."""

    total_tasks: int
    completed: int
    failed: int
    skipped: int
    duration_seconds: float
    results: List[CrawlResult]
    timestamp: datetime = Field(default_factory=datetime.now)
