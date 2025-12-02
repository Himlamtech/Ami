"""Multimodal API routes - Voice, Image, TTS."""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import io


# ===== DTOs =====

class VoiceQueryResponse(BaseModel):
    """Response from voice query."""
    transcription: str
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    duration_seconds: float
    session_id: Optional[str] = None


class ImageQueryResponse(BaseModel):
    """Response from image query."""
    description: str
    response: str
    extracted_text: Optional[str] = None
    detected_objects: List[str] = []
    related_documents: List[Dict[str, Any]] = []


class TTSRequest(BaseModel):
    """Request for text-to-speech."""
    text: str
    voice_gender: str = "female"
    speed: str = "normal"
    language: str = "vi"


# ===== Router =====

router = APIRouter(prefix="/multimodal", tags=["Multimodal"])


def get_stt_service():
    """Get STT service."""
    from app.infrastructure.stt.wav2vec2_stt import Wav2Vec2STTService
    return Wav2Vec2STTService()


def get_vector_store():
    """Get vector store service."""
    from app.infrastructure.factory.provider_factory import ProviderFactory
    factory = ProviderFactory()
    return factory.get_vector_store_service()


def get_llm_service():
    """Get LLM service."""
    from app.infrastructure.factory.provider_factory import ProviderFactory
    factory = ProviderFactory()
    return factory.get_llm_service()


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    language: str = Form("vi"),
):
    """
    Process voice query through STT + RAG pipeline.
    
    Accepts audio file, transcribes to text, and generates response.
    Supported formats: wav, mp3, m4a, flac, ogg, webm
    """
    from app.application.use_cases.multimodal import VoiceQueryUseCase, VoiceQueryInput
    
    # Validate file
    if not audio.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file required"
        )
    
    # Get file extension
    ext = audio.filename.split(".")[-1].lower()
    supported = ["wav", "mp3", "m4a", "flac", "ogg", "webm", "opus"]
    if ext not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {ext}. Supported: {', '.join(supported)}"
        )
    
    # Read audio bytes
    audio_bytes = await audio.read()
    
    # Execute use case
    try:
        use_case = VoiceQueryUseCase(
            stt_service=get_stt_service(),
            vector_store=get_vector_store(),
            llm_service=get_llm_service(),
        )
        
        result = await use_case.execute(VoiceQueryInput(
            audio_bytes=audio_bytes,
            audio_format=ext,
            session_id=session_id,
            user_id=user_id,
            language=language,
        ))
        
        return VoiceQueryResponse(
            transcription=result.transcription,
            response=result.response,
            sources=result.sources,
            confidence=result.confidence,
            duration_seconds=result.duration_seconds,
            session_id=result.session_id,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Voice processing failed: {str(e)}"
        )


@router.post("/image-query", response_model=ImageQueryResponse)
async def image_query(
    image: UploadFile = File(...),
    question: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    """
    Process image query with Vision + RAG.
    
    Analyzes image, extracts text/objects, and generates response.
    Supported formats: jpeg, png, webp, gif
    """
    from app.application.use_cases.multimodal import ImageQueryUseCase, ImageQueryInput
    
    # Validate file
    if not image.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file required"
        )
    
    # Get file extension
    ext = image.filename.split(".")[-1].lower()
    supported = ["jpg", "jpeg", "png", "webp", "gif"]
    if ext not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format: {ext}. Supported: {', '.join(supported)}"
        )
    
    # Normalize extension
    if ext == "jpg":
        ext = "jpeg"
    
    # Read image bytes
    image_bytes = await image.read()
    
    # Check file size (max 10MB)
    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large. Maximum size: 10MB"
        )
    
    # Execute use case
    try:
        use_case = ImageQueryUseCase(
            llm_service=get_llm_service(),
            vector_store=get_vector_store(),
        )
        
        result = await use_case.execute(ImageQueryInput(
            image_bytes=image_bytes,
            image_format=ext,
            question=question,
            session_id=session_id,
        ))
        
        return ImageQueryResponse(
            description=result.description,
            response=result.response,
            extracted_text=result.extracted_text,
            detected_objects=result.detected_objects,
            related_documents=result.related_documents,
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image processing failed: {str(e)}"
        )


@router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to speech audio.
    
    Returns audio file as streaming response.
    """
    from app.application.use_cases.multimodal import TextToSpeechUseCase, TextToSpeechInput
    
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty"
        )
    
    # Check text length
    if len(request.text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text too long. Maximum: 2000 characters"
        )
    
    try:
        # Note: TTS service needs to be implemented
        # This is a placeholder that returns an error
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="TTS service not yet implemented"
        )
        
        # When TTS is implemented:
        # use_case = TextToSpeechUseCase(tts_service=get_tts_service())
        # result = await use_case.execute(TextToSpeechInput(
        #     text=request.text,
        #     voice_gender=request.voice_gender,
        #     speed=request.speed,
        #     language=request.language,
        # ))
        #
        # return StreamingResponse(
        #     io.BytesIO(result.audio_bytes),
        #     media_type=f"audio/{result.audio_format}",
        #     headers={
        #         "Content-Disposition": f"attachment; filename=speech.{result.audio_format}"
        #     }
        # )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS failed: {str(e)}"
        )


@router.get("/capabilities")
async def get_capabilities():
    """Get available multimodal capabilities."""
    return {
        "voice_query": {
            "available": True,
            "formats": ["wav", "mp3", "m4a", "flac", "ogg", "webm"],
            "languages": ["vi"],
            "model": "wav2vec2-base-vi-vlsp2020",
        },
        "image_query": {
            "available": True,
            "formats": ["jpeg", "png", "webp", "gif"],
            "max_size_mb": 10,
            "features": ["description", "ocr", "object_detection"],
        },
        "text_to_speech": {
            "available": False,
            "note": "Coming soon",
        },
    }
