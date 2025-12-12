"""DTOs for multimodal endpoints (voice, image, TTS)."""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class VoiceQueryResponse(BaseModel):
    transcription: str
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    duration_seconds: float
    session_id: Optional[str] = None


class ImageQueryResponse(BaseModel):
    description: str
    response: str
    extracted_text: Optional[str] = None
    detected_objects: List[str] = []
    related_documents: List[Dict[str, Any]] = []


class TTSRequest(BaseModel):
    text: str
    voice_gender: str = "female"
    speed: str = "normal"
    language: str = "vi"


__all__ = ["VoiceQueryResponse", "ImageQueryResponse", "TTSRequest"]
