"""Speech-to-Text service interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class ISTTService(ABC):
    """
    Interface for Speech-to-Text (STT) providers.

    Renamed from ISTTProvider for consistency.
    """

    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "vi",
        use_lm: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text.

        Args:
            audio_data: Audio file bytes
            language: Language code (default: "vi" for Vietnamese)
            use_lm: Use language model for better accuracy

        Returns:
            Dict with:
                - text: Transcribed text
                - confidence: Confidence score (if available)
                - language: Detected/specified language
                - duration: Audio duration in seconds
                - model: Model name used
        """
        pass

    @abstractmethod
    async def transcribe_file(
        self,
        file_path: str,
        language: str = "vi",
        use_lm: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text.

        Args:
            file_path: Path to audio file
            language: Language code
            use_lm: Use language model

        Returns:
            Same as transcribe()
        """
        pass

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if STT service is ready.

        Returns:
            Dict with status and model info
        """
        pass
