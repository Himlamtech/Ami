"""Multimodal endpoints: voice, image, TTS."""

from typing import Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from app.config.services import ServiceRegistry
from app.api.schemas.multimodal_dto import (
    VoiceQueryResponse,
    ImageQueryResponse,
    TTSRequest,
)


router = APIRouter(prefix="/multimodal", tags=["Multimodal"])


def _get_stt_service():
    from app.infrastructure.ai.stt import Wav2Vec2STTService

    return Wav2Vec2STTService()


def _get_embedding_service():
    return ServiceRegistry.get_embedding()


def _get_vector_store():
    return ServiceRegistry.get_vector_store()


def _get_llm_service():
    return ServiceRegistry.get_llm()


@router.post("/voice-query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    user_id: Optional[str] = Form(None),
    language: str = Form("vi"),
):
    """Process voice query through STT + RAG pipeline."""
    from app.application.use_cases.multimodal import VoiceQueryUseCase, VoiceQueryInput

    if not audio.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Audio file required",
        )

    ext = audio.filename.split(".")[-1].lower()
    supported = ["wav", "mp3", "m4a", "flac", "ogg", "webm", "opus"]
    if ext not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported audio format: {ext}. Supported: {', '.join(supported)}",
        )

    audio_bytes = await audio.read()

    try:
        use_case = VoiceQueryUseCase(
            stt_service=_get_stt_service(),
            embedding_service=_get_embedding_service(),
            vector_store=_get_vector_store(),
            llm_service=_get_llm_service(),
        )

        result = await use_case.execute(
            VoiceQueryInput(
                audio_bytes=audio_bytes,
                audio_format=ext,
                session_id=session_id,
                user_id=user_id,
                language=language,
            )
        )

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
            detail=f"Voice processing failed: {str(e)}",
        )


@router.post("/image-query", response_model=ImageQueryResponse)
async def image_query(
    image: UploadFile = File(...),
    question: Optional[str] = Form(None),
    session_id: Optional[str] = Form(None),
):
    """Process image query with Vision + RAG."""
    from app.application.use_cases.multimodal import ImageQueryUseCase, ImageQueryInput

    if not image.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file required",
        )

    ext = image.filename.split(".")[-1].lower()
    supported = ["jpg", "jpeg", "png", "webp", "gif"]
    if ext not in supported:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image format: {ext}. Supported: {', '.join(supported)}",
        )

    if ext == "jpg":
        ext = "jpeg"

    image_bytes = await image.read()

    if len(image_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image too large. Maximum size: 10MB",
        )

    try:
        use_case = ImageQueryUseCase(
            llm_service=_get_llm_service(),
            embedding_service=_get_embedding_service(),
            vector_store=_get_vector_store(),
        )

        result = await use_case.execute(
            ImageQueryInput(
                image_bytes=image_bytes,
                image_format=ext,
                question=question,
                session_id=session_id,
            )
        )

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
            detail=f"Image processing failed: {str(e)}",
        )


@router.post("/text-to-speech")
async def text_to_speech(request: TTSRequest):
    """Convert text to speech audio."""
    if not request.text.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text cannot be empty",
        )

    if len(request.text) > 2000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text too long. Maximum: 2000 characters",
        )

    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="TTS service not yet implemented",
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


__all__ = ["router"]
