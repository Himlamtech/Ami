"""Image Query use case - Vision + RAG pipeline."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import base64

from application.interfaces.services.llm_service import ILLMService
from application.interfaces.services.vector_store_service import IVectorStoreService
from application.interfaces.services.embedding_service import IEmbeddingService


@dataclass
class ImageQueryInput:
    """Input for image query."""

    image_bytes: bytes
    image_format: str = "jpeg"  # jpeg, png, webp
    question: Optional[str] = None  # Optional question about image
    session_id: Optional[str] = None


@dataclass
class ImageQueryOutput:
    """Output from image query."""

    description: str
    response: str
    extracted_text: Optional[str] = None  # OCR text if any
    detected_objects: List[str] = None
    related_documents: List[Dict[str, Any]] = None

    def __post_init__(self):
        if self.detected_objects is None:
            self.detected_objects = []
        if self.related_documents is None:
            self.related_documents = []


class ImageQueryUseCase:
    """
    Use Case: Process image query with Vision and RAG.

    Pipeline:
    1. Analyze image with Vision model
    2. Extract relevant text/objects
    3. Search related documents (RAG)
    4. Generate contextual response

    Single Responsibility: Image-to-response pipeline
    """

    def __init__(
        self,
        llm_service: ILLMService,  # Must support vision
        embedding_service: Optional[IEmbeddingService],
        vector_store: IVectorStoreService,
    ):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    async def execute(self, input_data: ImageQueryInput) -> ImageQueryOutput:
        """
        Process image query.

        Args:
            input_data: Image query parameters

        Returns:
            ImageQueryOutput with analysis and response
        """
        # 1. Encode image to base64
        image_b64 = base64.b64encode(input_data.image_bytes).decode("utf-8")

        # 2. Analyze image with Vision
        analysis = await self._analyze_image(image_b64, input_data.image_format)

        description = analysis.get("description", "")
        extracted_text = analysis.get("text", "")
        detected_objects = analysis.get("objects", [])

        # 3. Build search query from analysis
        search_query = self._build_search_query(
            description=description,
            extracted_text=extracted_text,
            user_question=input_data.question,
        )

        # 4. Search related documents
        related_docs = []
        if search_query and self.embedding_service:
            query_embedding = await self.embedding_service.embed_text(search_query)
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=3,
                score_threshold=0.5,
            )

            for result in search_results:
                related_docs.append(
                    {
                        "title": result.get("metadata", {}).get("title", ""),
                        "content": result.get("content", "")[:200],
                        "score": result.get("score", 0.0),
                    }
                )

        # 5. Generate response
        response = await self._generate_response(
            description=description,
            extracted_text=extracted_text,
            related_docs=related_docs,
            user_question=input_data.question,
        )

        return ImageQueryOutput(
            description=description,
            response=response,
            extracted_text=extracted_text if extracted_text else None,
            detected_objects=detected_objects,
            related_documents=related_docs,
        )

    async def _analyze_image(self, image_b64: str, format: str) -> Dict[str, Any]:
        """Analyze image using Vision model."""
        mime_type = f"image/{format}"

        prompt = """Phân tích hình ảnh này và trả về JSON với các trường:
- description: Mô tả chi tiết nội dung hình ảnh (tiếng Việt)
- text: Văn bản được phát hiện trong hình (nếu có)
- objects: Danh sách các đối tượng chính được phát hiện
- context: Bối cảnh/chủ đề của hình ảnh

Nếu đây là tài liệu học viện, đơn từ, hoặc biểu mẫu, hãy trích xuất thông tin chi tiết."""

        # Check if LLM supports vision
        if hasattr(self.llm_service, "image_qa"):
            response = await self.llm_service.image_qa(
                prompt=prompt,
                image=image_b64,
                mime_type=mime_type,
            )
        else:
            # Fallback: describe that image analysis is not available
            return {
                "description": "Không thể phân tích hình ảnh. Dịch vụ Vision không khả dụng.",
                "text": "",
                "objects": [],
            }

        # Parse response
        try:
            import json

            # Try to extract JSON from response
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]

            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "description": response,
                "text": "",
                "objects": [],
            }

    def _build_search_query(
        self,
        description: str,
        extracted_text: str,
        user_question: Optional[str],
    ) -> str:
        """Build search query from image analysis."""
        parts = []

        if user_question:
            parts.append(user_question)

        if extracted_text:
            # Prioritize extracted text for documents/forms
            parts.append(extracted_text[:200])
        elif description:
            # Use description for general images
            parts.append(description[:200])

        return " ".join(parts)

    async def _generate_response(
        self,
        description: str,
        extracted_text: Optional[str],
        related_docs: List[Dict[str, Any]],
        user_question: Optional[str],
    ) -> str:
        """Generate contextual response."""
        # Build context
        context_parts = []

        if description:
            context_parts.append(f"Mô tả hình ảnh: {description}")

        if extracted_text:
            context_parts.append(f"Văn bản trong hình: {extracted_text}")

        if related_docs:
            docs_text = "\n".join(
                [f"- {doc['title']}: {doc['content']}" for doc in related_docs]
            )
            context_parts.append(f"Tài liệu liên quan:\n{docs_text}")

        context = "\n\n".join(context_parts)

        # Build prompt
        if user_question:
            prompt = f"""Bạn là trợ lý AI của Học viện PTIT.

{context}

Câu hỏi của người dùng về hình ảnh: {user_question}

Hãy trả lời câu hỏi dựa trên nội dung hình ảnh và tài liệu liên quan."""
        else:
            prompt = f"""Bạn là trợ lý AI của Học viện PTIT.

{context}

Hãy giải thích nội dung hình ảnh và cung cấp thông tin hữu ích nếu có tài liệu liên quan."""

        response = await self.llm_service.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=500,
        )

        return response.strip()
