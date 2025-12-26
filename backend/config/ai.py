"""
AI configuration - LLM providers, embeddings, and AI services.

Note: pydantic-settings automatically maps environment variables to field names
(case-insensitive). For example, field `openai_api_key` maps to env var `OPENAI_API_KEY`.
"""

from pydantic import Field
from .base import BaseConfig


class OpenAIConfig(BaseConfig):
    """OpenAI configuration."""

    openai_api_key: str = Field(default="")
    # Use a vision-capable model by default so image endpoints work out of the box
    openai_model_qa: str = Field(default="gpt-4o-mini")
    openai_model_reasoning: str = Field(default="o4-mini")
    openai_max_retries: int = Field(default=3, ge=0, le=10)
    openai_timeout: float = Field(default=60.0, ge=1.0)

    # Convenience properties
    @property
    def api_key(self) -> str:
        return self.openai_api_key

    @property
    def model_qa(self) -> str:
        return self.openai_model_qa

    @property
    def model_reasoning(self) -> str:
        return self.openai_model_reasoning

    @property
    def max_retries(self) -> int:
        return self.openai_max_retries

    @property
    def timeout(self) -> float:
        return self.openai_timeout


class AnthropicConfig(BaseConfig):
    """Anthropic (Claude) configuration."""

    anthropic_api_key: str = Field(default="")
    anthropic_model_qa: str = Field(default="claude-3-5-haiku-20241022")
    anthropic_model_reasoning: str = Field(default="claude-sonnet-4-20250514")
    anthropic_max_retries: int = Field(default=3, ge=0, le=10)
    anthropic_timeout: float = Field(default=60.0, ge=1.0)

    # Convenience properties
    @property
    def api_key(self) -> str:
        return self.anthropic_api_key

    @property
    def model_qa(self) -> str:
        return self.anthropic_model_qa

    @property
    def model_reasoning(self) -> str:
        return self.anthropic_model_reasoning

    @property
    def max_retries(self) -> int:
        return self.anthropic_max_retries

    @property
    def timeout(self) -> float:
        return self.anthropic_timeout


class GeminiConfig(BaseConfig):
    """Google Gemini configuration."""

    gemini_api_key: str = Field(default="")
    gemini_model_qa: str = Field(default="gemini-2.5-flash-lite-preview-09-2025")
    gemini_model_reasoning: str = Field(default="gemini-3-pro-preview")
    gemini_model_web_search: str = Field(default="gemini-2.0-flash")
    gemini_model_tts: str = Field(default="gemini-2.5-flash-preview-tts")
    gemini_tts_voice: str = Field(default="Kore")  # 30 voice options

    # Convenience properties
    @property
    def api_key(self) -> str:
        return self.gemini_api_key

    @property
    def model_qa(self) -> str:
        return self.gemini_model_qa

    @property
    def model_reasoning(self) -> str:
        return self.gemini_model_reasoning

    @property
    def model_web_search(self) -> str:
        return self.gemini_model_web_search

    @property
    def model_tts(self) -> str:
        return self.gemini_model_tts

    @property
    def tts_voice(self) -> str:
        return self.gemini_tts_voice


class EmbeddingConfig(BaseConfig):
    """Embedding model configuration."""

    huggingface_embedding_model: str = Field(
        default="dangvantuan/vietnamese-document-embedding"
    )
    embedding_dimension: int = Field(default=768)
    embedding_batch_size: int = Field(default=32)
    embedding_device: str = Field(default="cuda")  # "cpu" or "cuda"

    # Convenience properties
    @property
    def model(self) -> str:
        return self.huggingface_embedding_model

    @property
    def dimension(self) -> int:
        return self.embedding_dimension

    @property
    def batch_size(self) -> int:
        return self.embedding_batch_size

    @property
    def device(self) -> str:
        return self.embedding_device


class STTConfig(BaseConfig):
    """Speech-to-Text configuration."""

    stt_model: str = Field(default="nguyenvulebinh/wav2vec2-base-vi-vlsp2020")
    stt_device: str = Field(default="cuda")  # "cpu" or "cuda"

    # Convenience properties
    @property
    def model(self) -> str:
        return self.stt_model

    @property
    def device(self) -> str:
        return self.stt_device


class RAGConfig(BaseConfig):
    """RAG (Retrieval-Augmented Generation) configuration."""

    rag_top_k: int = Field(default=5, ge=1, le=20)
    rag_similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)

    # Convenience properties
    @property
    def top_k(self) -> int:
        return self.rag_top_k

    @property
    def similarity_threshold(self) -> float:
        return self.rag_similarity_threshold


class LLMConfig(BaseConfig):
    """Aggregated LLM configuration."""

    default_llm_provider: str = Field(default="openai")
    default_llm_mode: str = Field(default="qa")

    openai: OpenAIConfig = Field(default_factory=OpenAIConfig)
    anthropic: AnthropicConfig = Field(default_factory=AnthropicConfig)
    gemini: GeminiConfig = Field(default_factory=GeminiConfig)


# Singleton instances
openai_config = OpenAIConfig()
anthropic_config = AnthropicConfig()
gemini_config = GeminiConfig()
embedding_config = EmbeddingConfig()
stt_config = STTConfig()
rag_config = RAGConfig()
