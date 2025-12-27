"""
Gemini Text-to-Speech implementation.
Uses Google's Gemini TTS model for speech synthesis.
Supports Vietnamese and 23 other languages.
"""

import logging
import wave
import io
from typing import Optional, List

import google.genai as genai
from google.genai import types

from application.interfaces.services.tts_service import (
    ITTSService,
    TTSConfig,
    TTSResult,
    SpeechSpeed,
)
from config import gemini_config
from config.ai import GeminiConfig

logger = logging.getLogger(__name__)


# Available Gemini TTS voices with descriptions
GEMINI_VOICES = {
    "Zephyr": "Bright",
    "Puck": "Upbeat",
    "Charon": "Informative",
    "Kore": "Firm",
    "Fenrir": "Excitable",
    "Leda": "Youthful",
    "Orus": "Firm",
    "Aoede": "Breezy",
    "Callirrhoe": "Easy-going",
    "Autonoe": "Bright",
    "Enceladus": "Breathy",
    "Iapetus": "Clear",
    "Umbriel": "Easy-going",
    "Algieba": "Smooth",
    "Despina": "Smooth",
    "Erinome": "Clear",
    "Algenib": "Gravelly",
    "Rasalgethi": "Informative",
    "Laomedeia": "Upbeat",
    "Achernar": "Soft",
    "Alnilam": "Firm",
    "Schedar": "Even",
    "Gacrux": "Mature",
    "Pulcherrima": "Forward",
    "Achird": "Friendly",
    "Zubenelgenubi": "Casual",
    "Vindemiatrix": "Gentle",
    "Sadachbia": "Lively",
    "Sadaltager": "Knowledgeable",
    "Sulafat": "Warm",
}


class GeminiTTSService(ITTSService):
    """
    Gemini Text-to-Speech service.

    Uses Google's native TTS capabilities with:
    - 30 different voice options
    - 24 supported languages (including Vietnamese)
    - Style control via prompts
    """

    def __init__(
        self,
        config: Optional[GeminiConfig] = None,
    ):
        """
        Initialize Gemini TTS service.

        Args:
            config: Gemini configuration. If None, uses global gemini_config.
        """
        self.config = config or gemini_config
        self._client = genai.Client(api_key=self.config.api_key)
        self._model = self.config.model_tts
        self._default_voice = self.config.tts_voice

        logger.info(
            f"Initialized GeminiTTSService - Model: {self._model}, "
            f"Default voice: {self._default_voice}"
        )

    def _get_speed_instruction(self, speed: SpeechSpeed) -> str:
        """Get speed instruction for prompt."""
        speed_map = {
            SpeechSpeed.SLOW: "Speak slowly and clearly",
            SpeechSpeed.NORMAL: "",
            SpeechSpeed.FAST: "Speak quickly",
        }
        return speed_map.get(speed, "")

    def _build_prompt(self, text: str, config: TTSConfig) -> str:
        """Build TTS prompt with style instructions."""
        instructions = []

        # Add speed instruction
        speed_inst = self._get_speed_instruction(config.speed)
        if speed_inst:
            instructions.append(speed_inst)

        # Build final prompt
        if instructions:
            instruction_text = ". ".join(instructions)
            return f"{instruction_text}: {text}"

        return text

    async def synthesize(
        self,
        text: str,
        config: Optional[TTSConfig] = None,
    ) -> TTSResult:
        """
        Synthesize text to speech using Gemini TTS.

        Args:
            text: Text to convert to speech
            config: TTS configuration

        Returns:
            TTSResult with audio bytes (PCM WAV format)
        """
        if config is None:
            config = TTSConfig()

        try:
            # Build prompt with instructions
            prompt = self._build_prompt(text, config)

            # Configure TTS
            voice_name = self._default_voice
            tts_config = types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name=voice_name,
                        )
                    )
                ),
            )

            logger.debug(
                f"Synthesizing with voice: {voice_name}, text length: {len(text)}"
            )

            # Generate audio
            response = await self._client.aio.models.generate_content(
                model=self._model,
                contents=prompt,
                config=tts_config,
            )

            # Extract audio data with safety checks
            if not response.candidates or not response.candidates[0].content:
                raise RuntimeError("No audio generated from TTS model")

            parts = response.candidates[0].content.parts
            if not parts or not parts[0].inline_data:
                raise RuntimeError("No audio data in response")

            audio_data = parts[0].inline_data.data
            if not audio_data:
                raise RuntimeError("Empty audio data received")

            # Convert to WAV format
            wav_bytes = self._pcm_to_wav(audio_data)

            # Calculate duration (PCM: 24kHz, 16-bit, mono)
            duration = len(audio_data) / (
                24000 * 2
            )  # bytes / (sample_rate * bytes_per_sample)

            logger.info(f"TTS completed: {len(wav_bytes)} bytes, {duration:.2f}s")

            return TTSResult(
                audio_bytes=wav_bytes,
                audio_format="wav",
                duration_seconds=duration,
                sample_rate=24000,
                text_length=len(text),
                voice_used=voice_name,
            )

        except Exception as e:
            logger.error(f"Error in Gemini TTS: {e}")
            raise RuntimeError(f"Failed to synthesize speech: {str(e)}")

    async def synthesize_ssml(
        self,
        ssml: str,
        config: Optional[TTSConfig] = None,
    ) -> TTSResult:
        """
        Synthesize SSML to speech.

        Note: Gemini TTS doesn't natively support SSML.
        This extracts text from SSML and synthesizes it.

        Args:
            ssml: SSML markup text
            config: TTS configuration

        Returns:
            TTSResult with audio bytes
        """
        import re

        # Strip SSML tags to get plain text
        text = re.sub(r"<[^>]+>", "", ssml)
        text = text.strip()

        logger.warning("SSML not natively supported, using extracted text")
        return await self.synthesize(text, config)

    async def get_available_voices(self) -> List[dict]:
        """
        Get list of available Gemini TTS voices.

        Returns:
            List of voice dictionaries with name and description
        """
        return [
            {"name": name, "description": desc} for name, desc in GEMINI_VOICES.items()
        ]

    async def is_available(self) -> bool:
        """Check if Gemini TTS service is available."""
        try:
            # Simple API key validation
            return bool(self.config.api_key)
        except Exception:
            return False

    def _pcm_to_wav(
        self,
        pcm_data: bytes,
        channels: int = 1,
        sample_rate: int = 24000,
        sample_width: int = 2,
    ) -> bytes:
        """
        Convert raw PCM audio to WAV format.

        Args:
            pcm_data: Raw PCM audio bytes
            channels: Number of audio channels (default: 1 mono)
            sample_rate: Sample rate in Hz (default: 24000)
            sample_width: Bytes per sample (default: 2 for 16-bit)

        Returns:
            WAV formatted audio bytes
        """
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm_data)

        buffer.seek(0)
        return buffer.read()


if __name__ == "__main__":
    import asyncio

    async def test_tts():
        service = GeminiTTSService()

        # List voices
        voices = await service.get_available_voices()
        print(f"Available voices: {len(voices)}")

        # Test synthesis
        result = await service.synthesize("Xin chào, tôi là trợ lý ảo.")
        print(f"Audio: {len(result.audio_bytes)} bytes, {result.duration_seconds:.2f}s")

        # Save to file
        with open("test_output.wav", "wb") as f:
            f.write(result.audio_bytes)
        print("Saved to test_output.wav")

    asyncio.run(test_tts())
