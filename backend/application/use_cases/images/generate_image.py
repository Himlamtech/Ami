"""Generate Image use case - DALL-E integration."""

import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.infrastructure.ai.llm.openai_llm import OpenAILLMService
from app.infrastructure.persistence.minio.minio_storage import MinIOStorage

logger = logging.getLogger(__name__)


@dataclass
class GenerateImageInput:
    """Input for image generation."""

    prompt: str
    size: str = "1024x1024"
    style: str = "natural"


@dataclass
class GenerateImageOutput:
    """Output from image generation."""

    url: str
    prompt: str


class GenerateImageUseCase:
    """
    Use Case: Generate image using DALL-E and store in MinIO.

    Pipeline:
    1. Generate image with DALL-E
    2. Upload to MinIO storage
    3. Return presigned URL

    Single Responsibility: Image generation workflow
    """

    def __init__(
        self,
        llm_service: OpenAILLMService,
        storage: MinIOStorage,
    ):
        self.llm_service = llm_service
        self.storage = storage

    async def execute(self, input_data: GenerateImageInput) -> GenerateImageOutput:
        """
        Generate image from text prompt.

        Args:
            input_data: Image generation parameters

        Returns:
            GenerateImageOutput with URL to generated image
        """
        # 1. Generate image with DALL-E
        logger.info(f"Generating image with prompt: {input_data.prompt[:50]}...")
        image_bytes = await self.llm_service.generate_image(
            prompt=input_data.prompt,
            size=input_data.size,
            style=input_data.style,
        )

        # 2. Upload to MinIO
        file_name = f"generated_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.png"

        url = await self.storage.upload_file(
            file_data=image_bytes,
            filename=file_name,
            content_type="image/png",
            path_prefix="generated-images",
        )

        # 3. Extract object name from URL for presigned URL generation
        object_name = url.split(f"/{self.storage.bucket}/")[-1]

        # 4. Generate presigned URL (valid for 1 hour)
        presigned_url = await self.storage.get_presigned_url(
            object_name=object_name,
            expires_seconds=3600,
        )

        logger.info(f"Image generated and uploaded: {object_name}")

        return GenerateImageOutput(
            url=presigned_url,
            prompt=input_data.prompt,
        )
