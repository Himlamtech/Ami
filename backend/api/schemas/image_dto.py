"""Image DTOs."""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class GenerateImageRequest(BaseModel):
    """Generate image request."""

    prompt: str
    size: str = "1024x1024"
    style: str = "natural"


class AnalyzeImageRequest(BaseModel):
    """Analyze image request."""

    image_url: str
    question: str = "What's in this image?"


class ImageResponse(BaseModel):
    """Image response."""

    url: str
    prompt: Optional[str] = None


class AnalyzeImageResponse(BaseModel):
    """Analyze image response."""

    description: str
    metadata: Dict[str, Any]
