"""Configuration routes."""

from fastapi import APIRouter
from app.config.settings import settings


router = APIRouter(prefix="/config", tags=["configuration"])


@router.get("/info")
async def get_config_info():
    """Get public configuration information."""
    return {
        "app_name": "AMI RAG System",
        "version": "2.0.0-refactored",
        "environment": settings.environment,
        "features": {
            "rag": True,
            "chat": True,
            "crawler": True,
            "images": False,  # Not yet implemented
        }
    }
