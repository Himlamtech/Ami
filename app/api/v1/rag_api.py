# app/api/v1/rag_api.py
"""RAG Chat API endpoints."""

from fastapi import APIRouter, HTTPException

from app.services.rag import RAGService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()
rag_service = RAGService()


@router.post("/chat", response_model=ChatResponse)
async def rag_chat(request: ChatRequest) -> ChatResponse:
    """Chat với RAG service."""
    try:
        response = rag_service.generate_response(request.messages, request.session_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
