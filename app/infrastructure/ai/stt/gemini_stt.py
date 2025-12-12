"""
Gemini Speech-to-Text implementation.
Uses Google's Gemini multimodal capabilities for audio transcription.
Alternative to local Wav2Vec2 - cloud-based, multilingual.
"""

import logging
from typing import Dict, Any, Optional

import google.genai as genai
from google.genai import types

from app.application.interfaces.services.stt_service import ISTTService
from app.config import gemini_config
from app.config.ai import GeminiConfig

logger = logging.getLogger(__name__)


# Supported audio formats by Gemini
SUPPORTED_FORMATS = {
    "wav": "audio/wav",
    "mp3": "audio/mp3",
    "aiff": "audio/aiff",
    "aac": "audio/aac",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
}


class GeminiSTTService(ISTTService):
    """
    Gemini Speech-to-Text service using audio understanding.

    Uses Gemini's multimodal capabilities to transcribe audio.
    Supports multiple languages and audio formats.

    Note: This is a cloud-based alternative to local Wav2Vec2.
    """

    def __init__(
        self,
        config: Optional[GeminiConfig] = None,
    ):
        """
        Initialize Gemini STT service.

        Args:
            config: Gemini configuration. If None, uses global gemini_config.
        """
        self.config = config or gemini_config
        self._client = genai.Client(api_key=self.config.api_key)
        self._model = self.config.model_qa  # Use QA model for transcription

        logger.info(f"Initialized GeminiSTTService with model: {self._model}")

    def _detect_mime_type(self, audio_data: bytes) -> str:
        """
        Detect audio MIME type from file header.

        Args:
            audio_data: Audio file bytes

        Returns:
            MIME type string
        """
        # Check file signatures
        if audio_data[:4] == b"RIFF":
            return "audio/wav"
        elif audio_data[:3] == b"ID3" or audio_data[:2] == b"\xff\xfb":
            return "audio/mp3"
        elif audio_data[:4] == b"fLaC":
            return "audio/flac"
        elif audio_data[:4] == b"OggS":
            return "audio/ogg"
        elif audio_data[:4] == b"FORM":
            return "audio/aiff"

        # Default to wav
        return "audio/wav"

    async def transcribe(
        self,
        audio_data: bytes,
        language: str = "vi",
        use_lm: bool = True,
    ) -> Dict[str, Any]:
        """
        Transcribe audio to text using Gemini.

        Args:
            audio_data: Audio file bytes
            language: Language code (default: "vi" for Vietnamese)
            use_lm: Not used for Gemini (always uses LM)

        Returns:
            Dict with transcription result
        """
        try:
            # Detect MIME type
            mime_type = self._detect_mime_type(audio_data)

            # Build prompt based on language
            if language == "vi":
                prompt = "Hãy phiên âm chính xác nội dung bài nói tiếng Việt này. Chỉ trả về văn bản đã phiên âm, không thêm gì khác."
            else:
                prompt = f"Generate an accurate transcript of this {language} speech. Return only the transcribed text, nothing else."

            # Create audio part
            audio_part = types.Part.from_bytes(
                data=audio_data,
                mime_type=mime_type,
            )

            logger.debug(
                f"Transcribing audio: {len(audio_data)} bytes, mime: {mime_type}"
            )

            # Generate transcription
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=[prompt, audio_part],
                config=types.GenerateContentConfig(
                    temperature=0.0,  # Deterministic for transcription
                    max_output_tokens=4096,
                ),
            )

            text = response.text.strip() if response.text else ""

            # Estimate duration (rough: 32 tokens/second for Gemini audio)
            # This is approximate since we don't have exact duration
            estimated_duration = len(audio_data) / 32000  # Very rough estimate

            logger.info(f"Transcription completed: {len(text)} chars")

            return {
                "text": text,
                "confidence": 0.95,  # Gemini doesn't provide confidence
                "language": language,
                "duration": estimated_duration,
                "model": self._model,
            }

        except Exception as e:
            logger.error(f"Error in Gemini STT: {e}")
            raise RuntimeError(f"Failed to transcribe audio: {str(e)}")

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
            use_lm: Not used for Gemini

        Returns:
            Same as transcribe()
        """
        try:
            # Read file
            with open(file_path, "rb") as f:
                audio_data = f.read()

            # Use transcribe
            result = await self.transcribe(audio_data, language, use_lm)
            result["file_path"] = file_path

            return result

        except FileNotFoundError:
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        except Exception as e:
            logger.error(f"Error reading audio file: {e}")
            raise

    async def transcribe_with_timestamps(
        self,
        audio_data: bytes,
        language: str = "vi",
    ) -> Dict[str, Any]:
        """
        Transcribe audio with timestamp information.

        Uses Gemini's ability to reference specific time segments.

        Args:
            audio_data: Audio file bytes
            language: Language code

        Returns:
            Dict with text and timestamps (if available)
        """
        try:
            mime_type = self._detect_mime_type(audio_data)

            if language == "vi":
                prompt = """Phiên âm bài nói này với thông tin thời gian.
Format: [MM:SS] Nội dung
Ví dụ:
[00:00] Xin chào
[00:05] Tôi là trợ lý ảo"""
            else:
                prompt = """Transcribe this speech with timestamps.
Format: [MM:SS] Content
Example:
[00:00] Hello
[00:05] I am an assistant"""

            audio_part = types.Part.from_bytes(
                data=audio_data,
                mime_type=mime_type,
            )

            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=[prompt, audio_part],
                config=types.GenerateContentConfig(
                    temperature=0.0,
                    max_output_tokens=4096,
                ),
            )

            text = response.text.strip() if response.text else ""

            return {
                "text": text,
                "has_timestamps": True,
                "language": language,
                "model": self._model,
            }

        except Exception as e:
            logger.error(f"Error in timestamped transcription: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """
        Check if Gemini STT service is ready.

        Returns:
            Dict with status and model info
        """
        try:
            # Check API key is configured
            if not self.config.api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "model": self._model,
                }

            return {
                "status": "ok",
                "model": self._model,
                "provider": "gemini",
                "supported_formats": list(SUPPORTED_FORMATS.keys()),
            }

        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "model": self._model,
            }


if __name__ == "__main__":
    import asyncio

    async def test_stt():
        service = GeminiSTTService()

        # Health check
        status = await service.health_check()
        print(f"Health: {status}")

        # Test with a file if available
        # result = await service.transcribe_file("test.wav", language="vi")
        # print(f"Transcription: {result['text']}")

    asyncio.run(test_stt())
