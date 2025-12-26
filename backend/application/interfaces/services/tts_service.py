"""Text-to-Speech service interface."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class VoiceGender(Enum):
    """Voice gender options."""

    MALE = "male"
    FEMALE = "female"


class SpeechSpeed(Enum):
    """Speech speed options."""

    SLOW = "slow"
    NORMAL = "normal"
    FAST = "fast"


@dataclass
class TTSConfig:
    """Configuration for TTS."""

    voice_gender: VoiceGender = VoiceGender.FEMALE
    speed: SpeechSpeed = SpeechSpeed.NORMAL
    language: str = "vi"

    # Voice customization
    pitch: float = 1.0  # 0.5 - 2.0
    volume: float = 1.0  # 0.0 - 1.0


@dataclass
class TTSResult:
    """Result from text-to-speech synthesis."""

    audio_bytes: bytes
    audio_format: str  # wav, mp3
    duration_seconds: float
    sample_rate: int

    # Metadata
    text_length: int = 0
    voice_used: str = ""


class ITTSService(ABC):
    """Interface for Text-to-Speech service."""

    @abstractmethod
    async def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
    ) -> TTSResult:
        """
        Synthesize text to speech.

        Args:
            text: Text to convert to speech
            config: TTS configuration

        Returns:
            TTSResult with audio bytes
        """
        pass

    @abstractmethod
    async def synthesize_ssml(
        self,
        ssml: str,
        config: Optional[TTSConfig] = None,
    ) -> TTSResult:
        """
        Synthesize SSML to speech.

        Args:
            ssml: SSML markup text
            config: TTS configuration

        Returns:
            TTSResult with audio bytes
        """
        pass

    @abstractmethod
    async def get_available_voices(self) -> list:
        """Get list of available voices."""
        pass

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if TTS service is available."""
        pass
