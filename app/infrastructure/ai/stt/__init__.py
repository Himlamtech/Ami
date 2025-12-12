"""Speech-to-Text implementations."""

from .wav2vec2_stt import Wav2Vec2STTService
from .gemini_stt import GeminiSTTService

__all__ = ["Wav2Vec2STTService", "GeminiSTTService"]
