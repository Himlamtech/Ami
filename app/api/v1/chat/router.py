"""Chat-facing API routes grouped cleanly."""

from fastapi import APIRouter

from app.api.v1.chat.history import router as history_router
from app.api.v1.chat.bookmarks import router as bookmarks_router
from app.api.v1.chat.image import router as image_router
from app.api.v1.chat.generate import router as generate_router
from app.api.v1.chat.smart_query import router as smart_query_router
from app.api.v1.chat.multimodal import router as multimodal_router
from app.api.v1.chat.profile import router as profile_router
from app.api.v1.chat.suggestion import router as suggestion_router
from app.api.v1.chat.feedback import router as feedback_router


router = APIRouter()
router.include_router(history_router)
router.include_router(bookmarks_router)
router.include_router(image_router)
router.include_router(generate_router)
router.include_router(smart_query_router)
router.include_router(multimodal_router)
router.include_router(profile_router)
router.include_router(suggestion_router)
router.include_router(feedback_router)

__all__ = ["router"]
