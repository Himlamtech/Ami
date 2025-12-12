"""Image service interface."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IImageService(ABC):
    """
    Interface for AI image generation and vision providers.

    Renamed from IImageProvider for consistency.
    """

    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
    ) -> bytes:
        """
        Generate image from text prompt.

        Args:
            prompt: Image description prompt
            size: Image size (e.g., "1024x1024", "1792x1024")
            style: Image style (e.g., "natural", "vivid")

        Returns:
            Image bytes
        """
        pass

    @abstractmethod
    async def analyze_image(
        self,
        image_url: str,
        question: str = "What's in this image?",
        detail: str = "auto",
    ) -> Dict[str, Any]:
        """
        Analyze image and return description, labels, etc.

        Args:
            image_url: URL to image
            question: Question to ask about the image
            detail: Level of detail ("auto", "low", "high")

        Returns:
            Dict with:
                - description: Text description
                - labels: List of detected objects/concepts
                - ocr_text: Extracted text (if any)
                - confidence: Confidence score
        """
        pass

    @abstractmethod
    async def extract_text_ocr(self, image_url: str) -> Optional[str]:
        """
        Extract text from image using OCR.

        Args:
            image_url: URL to image

        Returns:
            Extracted text, None if no text found
        """
        pass
