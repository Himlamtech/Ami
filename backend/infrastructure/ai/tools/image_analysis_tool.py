"""
Image Analysis Tool Handler - Analyze image artifacts with Vision.
"""

import logging
from typing import Dict, Any, Optional

from app.domain.enums.tool_type import ToolType
from app.application.interfaces.services.tool_executor_service import IToolHandler
from app.application.interfaces.services.llm_service import ILLMService
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import (
    IVectorStoreService,
)
from app.application.use_cases.multimodal.image_query import (
    ImageQueryUseCase,
    ImageQueryInput,
)


logger = logging.getLogger(__name__)


class ImageAnalysisToolHandler(IToolHandler):
    """
    Handler for analyze_image tool.

    Executes the Vision + RAG pipeline and returns analysis + response.
    """

    def __init__(
        self,
        llm_service: ILLMService,
        embedding_service: Optional[IEmbeddingService],
        vector_store: IVectorStoreService,
    ):
        self._llm = llm_service
        self._embedding = embedding_service
        self._vector_store = vector_store

    @property
    def tool_type(self) -> ToolType:
        return ToolType.ANALYZE_IMAGE

    def validate_arguments(self, arguments: Dict[str, Any]) -> bool:
        """Validate tool arguments."""
        return "image_bytes" in arguments

    async def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute image analysis tool.

        Args:
            arguments:
                - image_bytes: Raw image bytes (required)
                - image_format: jpeg/png/webp/gif (optional)
                - question: User question about the image (optional)

        Returns:
            {
                "description": str,
                "response": str,
                "extracted_text": str | None,
                "detected_objects": List[str],
                "related_documents": List[Dict]
            }
        """
        image_bytes = arguments.get("image_bytes")
        image_format = arguments.get("image_format", "jpeg")
        question = arguments.get("question")

        logger.info("Image analysis tool executing")

        use_case = ImageQueryUseCase(
            llm_service=self._llm,
            embedding_service=self._embedding,
            vector_store=self._vector_store,
        )

        result = await use_case.execute(
            ImageQueryInput(
                image_bytes=image_bytes,
                image_format=image_format,
                question=question,
            )
        )

        return {
            "description": result.description,
            "response": result.response,
            "extracted_text": result.extracted_text,
            "detected_objects": result.detected_objects,
            "related_documents": result.related_documents,
        }
