"""Vision AI service using Gemini Vision API."""

import base64
from typing import Optional, List
import google.generativeai as genai

from app.config import app_config


class GeminiVisionService:
    """Vision service using Google Gemini."""

    def __init__(self):
        """Initialize Gemini Vision service."""
        if not app_config.gemini_api_key:
            raise ValueError("GEMINI_API_KEY not configured")
        
        genai.configure(api_key=app_config.gemini_api_key)
        # Use gemini-2.5-flash which supports vision
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    async def analyze_image(
        self,
        image_bytes: bytes,
        prompt: Optional[str] = None,
    ) -> dict:
        """
        Analyze image and return description.
        
        Args:
            image_bytes: Image data in bytes
            prompt: Optional custom prompt for analysis
            
        Returns:
            dict with description, extracted_text, detected_objects
        """
        try:
            # Default prompt if not provided
            if not prompt:
                prompt = """Phân tích hình ảnh này và cung cấp:
1. Mô tả chi tiết nội dung
2. Văn bản được trích xuất (nếu có)
3. Các đối tượng được phát hiện

Trả lời bằng tiếng Việt."""

            # Convert bytes to base64 for Gemini
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            
            # Generate content
            response = self.model.generate_content([prompt, image])
            
            # Parse response
            description = response.text
            
            # Try to extract structured info from response
            extracted_text = self._extract_text_from_response(description)
            detected_objects = self._extract_objects_from_response(description)
            
            return {
                "description": description,
                "extracted_text": extracted_text,
                "detected_objects": detected_objects,
            }
            
        except Exception as e:
            raise Exception(f"Vision analysis failed: {str(e)}")

    async def extract_text(self, image_bytes: bytes) -> Optional[str]:
        """Extract text from image (OCR)."""
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = "Trích xuất TẤT CẢ văn bản trong hình ảnh này. Chỉ trả về văn bản, không thêm giải thích."
            
            response = self.model.generate_content([prompt, image])
            return response.text.strip()
            
        except Exception as e:
            return None

    async def describe_image(self, image_bytes: bytes) -> str:
        """Get detailed description of image."""
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = "Mô tả chi tiết hình ảnh này bằng tiếng Việt. Bao gồm: đối tượng chính, màu sắc, bố cục, văn bản (nếu có)."
            
            response = self.model.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            return f"Không thể mô tả hình ảnh: {str(e)}"

    async def answer_question_about_image(
        self,
        image_bytes: bytes,
        question: str,
    ) -> str:
        """Answer a specific question about the image."""
        try:
            import io
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            
            prompt = f"Dựa vào hình ảnh, hãy trả lời câu hỏi sau bằng tiếng Việt:\n\n{question}"
            
            response = self.model.generate_content([prompt, image])
            return response.text
            
        except Exception as e:
            return f"Không thể trả lời câu hỏi: {str(e)}"

    def _extract_text_from_response(self, response: str) -> Optional[str]:
        """Extract text content from vision response."""
        # Simple heuristic: look for text after keywords
        keywords = ["văn bản", "text", "chữ", "nội dung"]
        lines = response.lower().split("\n")
        
        text_lines = []
        capture = False
        
        for line in lines:
            if any(kw in line for kw in keywords):
                capture = True
                continue
            if capture and line.strip():
                # Stop if we hit another section
                if any(x in line for x in ["đối tượng", "object", "mô tả", "description"]):
                    break
                text_lines.append(line.strip())
        
        return "\n".join(text_lines) if text_lines else None

    def _extract_objects_from_response(self, response: str) -> List[str]:
        """Extract detected objects from vision response."""
        # Simple heuristic: look for objects after keywords
        keywords = ["đối tượng", "object", "phát hiện"]
        lines = response.lower().split("\n")
        
        objects = []
        capture = False
        
        for line in lines:
            if any(kw in line for kw in keywords):
                capture = True
                continue
            if capture and line.strip():
                # Stop if we hit another section
                if any(x in line for x in ["văn bản", "text", "mô tả khác"]):
                    break
                # Extract object names (remove bullets, numbers)
                obj = line.strip().lstrip("-*•123456789. ")
                if obj:
                    objects.append(obj)
        
        return objects[:10]  # Limit to 10 objects


__all__ = ["GeminiVisionService"]
