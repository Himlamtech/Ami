"""AI services - LLM, Embeddings, STT, TTS.

Use submodule imports directly when needed:
- from app.infrastructure.ai.llm import OpenAILLMService, GeminiLLMService
- from app.infrastructure.ai.embeddings import HuggingFaceEmbeddings
- from app.infrastructure.ai.stt import Wav2Vec2STTService, GeminiSTTService
- from app.infrastructure.ai.tts import GeminiTTSService
"""

# Lazy imports to avoid missing optional dependencies
__all__ = [
    "llm",
    "embeddings",
    "stt",
    "tts",
]
