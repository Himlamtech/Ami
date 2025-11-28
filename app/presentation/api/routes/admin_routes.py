"""Admin routes - Simplified."""

from fastapi import APIRouter, HTTPException, status
from typing import List

from app.presentation.api.schemas.auth_dto import UserResponse


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(skip: int = 0, limit: int = 100):
    """List all users (admin only)."""
    from app.infrastructure.factory import get_factory
    
    factory = get_factory()
    user_repo = factory.get_user_repository()
    
    users = await user_repo.list_users(skip=skip, limit=limit)
    
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            role_ids=user.role_ids,
        )
        for user in users
    ]


@router.get("/stats")
async def get_stats():
    """Get system statistics."""
    from app.infrastructure.factory import get_factory
    
    factory = get_factory()
    
    # Get counts
    user_repo = factory.get_user_repository()
    doc_repo = factory.get_document_repository()
    chat_repo = factory.get_chat_repository()
    
    total_users = await user_repo.count()
    total_docs = await doc_repo.count()
    
    return {
        "total_users": total_users,
        "total_documents": total_docs,
        "version": "2.0.0-refactored",
    }
