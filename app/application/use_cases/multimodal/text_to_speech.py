"""Text-to-Speech use case."""

from dataclasses import dataclass
from typing import Optional

from app.application.interfaces.services.tts_service import (
    ITTSService,
    TTSConfig,
    VoiceGender,
    SpeechSpeed,
)


@dataclass
class TextToSpeechInput:
    """Input for text-to-speech."""
    text: str
    voice_gender: str = "female"  # male, female
    speed: str = "normal"  # slow, normal, fast
    language: str = "vi"


@dataclass
class TextToSpeechOutput:
    """Output from text-to-speech."""
    audio_bytes: bytes
    audio_format: str
    duration_seconds: float
    text_length: int


class TextToSpeechUseCase:
    """
    Use Case: Convert text to speech audio.
    
    Converts response text to audio for voice output.
    Single Responsibility: Text to audio conversion
    """
    
    def __init__(self, tts_service: ITTSService):
        self.tts_service = tts_service
    
    async def execute(self, input_data: TextToSpeechInput) -> TextToSpeechOutput:
        """
        Convert text to speech.
        
        Args:
            input_data: Text and voice configuration
            
        Returns:
            TextToSpeechOutput with audio bytes
        """
        # Build config
        gender = VoiceGender.FEMALE
        if input_data.voice_gender.lower() == "male":
            gender = VoiceGender.MALE
        
        speed = SpeechSpeed.NORMAL
        if input_data.speed.lower() == "slow":
            speed = SpeechSpeed.SLOW
        elif input_data.speed.lower() == "fast":
            speed = SpeechSpeed.FAST
        
        config = TTSConfig(
            voice_gender=gender,
            speed=speed,
            language=input_data.language,
        )
        
        # Preprocess text for TTS
        processed_text = self._preprocess_text(input_data.text)
        
        # Synthesize
        result = await self.tts_service.synthesize(
            text=processed_text,
            config=config,
        )
        
        return TextToSpeechOutput(
            audio_bytes=result.audio_bytes,
            audio_format=result.audio_format,
            duration_seconds=result.duration_seconds,
            text_length=len(input_data.text),
        )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for better TTS output."""
        # Remove markdown formatting
        text = text.replace("**", "")
        text = text.replace("*", "")
        text = text.replace("_", "")
        text = text.replace("`", "")
        
        # Remove URLs
        import re
        text = re.sub(r'http[s]?://\S+', '', text)
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Limit length for TTS
        max_length = 1000
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        return text.strip()
