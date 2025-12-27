"""Analyze Image use case - Vision AI wrapper."""

from dataclasses import dataclass
from typing import Optional, Dict, Any
import logging

from app.application.interfaces.services.llm_service import ILLMService

logger = logging.getLogger(__name__)


@dataclass
class AnalyzeImageInput:
    """Input for image analysis."""

    image_url: str
    question: str = "What's in this image?"


@dataclass
class AnalyzeImageOutput:
    """Output from image analysis."""

    description: str
    metadata: Dict[str, Any]


class AnalyzeImageUseCase:
    """
    Use Case: Analyze image using Vision AI.

    Pipeline:
    1. Download image from URL
    2. Analyze with Vision model
    3. Return structured response

    Single Responsibility: Image analysis workflow
    """

    def __init__(self, llm_service: ILLMService):
        self.llm_service = llm_service

    async def execute(self, input_data: AnalyzeImageInput) -> AnalyzeImageOutput:
        """
        Analyze image and answer question.

        Args:
            input_data: Image analysis parameters

        Returns:
            AnalyzeImageOutput with description and metadata
        """
        # 1. Prepare prompt
        prompt = f"""Phân tích hình ảnh này và trả lời câu hỏi sau.

Câu hỏi: {input_data.question}

Hãy cung cấp câu trả lời chi tiết bằng tiếng Việt."""

        # 2. Analyze image using Vision model
        logger.info(f"Analyzing image from URL: {input_data.image_url[:50]}...")
        
        # Check if LLM supports vision
        if not hasattr(self.llm_service, "image_qa"):
            raise RuntimeError("LLM service does not support vision analysis")

        response = await self.llm_service.image_qa(
            prompt=prompt,
            image=input_data.image_url,
        )

        logger.info(f"Image analysis complete: {len(response)} chars")

        return AnalyzeImageOutput(
            description=response,
            metadata={
                "image_url": input_data.image_url,
                "question": input_data.question,
            },
        )
