"""AI services - LLM, Embeddings, STT, TTS.

Use submodule imports directly when needed:
- from infrastructure.ai.llm import OpenAILLMService, GeminiLLMService
- from infrastructure.ai.embeddings import HuggingFaceEmbeddings
- from infrastructure.ai.stt import Wav2Vec2STTService, GeminiSTTService
- from infrastructure.ai.tts import GeminiTTSService
"""

# Lazy imports to avoid missing optional dependencies
__all__ = [
    "llm",
    "embeddings",
    "stt",
    "tts",
]
