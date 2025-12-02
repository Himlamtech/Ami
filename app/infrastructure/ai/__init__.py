"""AI services - LLM, Embeddings, STT, Image Generation.

Use submodule imports directly when needed:
- from app.infrastructure.ai.llm import OpenAILLMService
- from app.infrastructure.ai.embeddings import HuggingFaceEmbeddings
- from app.infrastructure.ai.stt import Wav2Vec2STTService
- from app.infrastructure.ai.image_generation import OpenAIImageProvider
"""

# Lazy imports to avoid missing optional dependencies
__all__ = [
    "llm",
    "embeddings", 
    "stt",
    "image_generation",
]
