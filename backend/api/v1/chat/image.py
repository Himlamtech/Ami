"""Image routes - Simplified."""

from fastapi import APIRouter, HTTPException, status
import logging

from app.api.schemas.image_dto import (
    GenerateImageRequest,
    AnalyzeImageRequest,
    ImageResponse,
    AnalyzeImageResponse,
)
from app.application.use_cases.images import (
    GenerateImageUseCase,
    GenerateImageInput,
    AnalyzeImageUseCase,
    AnalyzeImageInput,
)
from app.config.services import ServiceRegistry


router = APIRouter(prefix="/images", tags=["images"])
logger = logging.getLogger(__name__)


@router.post("/generate", response_model=ImageResponse)
async def generate_image(request: GenerateImageRequest):
    """Generate image from prompt."""
    try:
        # Get services
        llm_service = ServiceRegistry.get_llm(provider="openai")
        storage = ServiceRegistry.get_storage()

        if not llm_service or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        # Execute use case
        use_case = GenerateImageUseCase(
            llm_service=llm_service,
            storage=storage,
        )

        input_data = GenerateImageInput(
            prompt=request.prompt,
            size=request.size,
            style=request.style,
        )

        result = await use_case.execute(input_data)

        return ImageResponse(
            url=result.url,
            prompt=result.prompt,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image generation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image generation failed: {str(e)}",
        )


@router.post("/analyze", response_model=AnalyzeImageResponse)
async def analyze_image(request: AnalyzeImageRequest):
    """Analyze image with vision AI."""
    try:
        # Get LLM service with vision support
        llm_service = ServiceRegistry.get_llm(provider="openai")

        if not llm_service:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        # Execute use case
        use_case = AnalyzeImageUseCase(llm_service=llm_service)

        input_data = AnalyzeImageInput(
            image_url=request.image_url,
            question=request.question,
        )

        result = await use_case.execute(input_data)

        return AnalyzeImageResponse(
            description=result.description,
            metadata=result.metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}",
        )
