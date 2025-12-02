"""Image routes - Simplified."""

from fastapi import APIRouter, HTTPException, status

from app.api.schemas.image_dto import (
    GenerateImageRequest,
    AnalyzeImageRequest,
    ImageResponse,
)


router = APIRouter(prefix="/images", tags=["images"])


@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: GenerateImageRequest):
    """Generate image from prompt."""
    # TODO: Implement with use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Image generation not yet implemented in refactored version"
    )


@router.post("/analyze")
async def analyze_image(request: AnalyzeImageRequest):
    """Analyze image with vision AI."""
    # TODO: Implement with use case
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Image analysis not yet implemented in refactored version"
    )
