"""Multimodal use cases: Voice, Image, TTS."""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


# ===== Voice Query =====

@dataclass
class VoiceQueryInput:
    """Input for voice query."""
    audio_bytes: bytes
    audio_format: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "vi"


@dataclass
class VoiceQueryOutput:
    """Output from voice query."""
    transcription: str
    response: str
    sources: List[dict]
    confidence: float
    duration_seconds: float
    session_id: Optional[str]


class VoiceQueryUseCase:
    """Process voice query through STT + RAG."""

    def __init__(self, stt_service, embedding_service, vector_store, llm_service):
        self.stt_service = stt_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service

    async def execute(self, input_data: VoiceQueryInput) -> VoiceQueryOutput:
        """Execute voice query."""
        import time
        start_time = time.time()

        # 1. STT: Convert audio to text
        transcription_result = await self.stt_service.transcribe(
            audio_bytes=input_data.audio_bytes,
            audio_format=input_data.audio_format,
            language=input_data.language,
        )
        
        transcription = transcription_result.get("text", "")
        confidence = transcription_result.get("confidence", 0.0)

        if not transcription:
            return VoiceQueryOutput(
                transcription="",
                response="Không thể nhận diện giọng nói. Vui lòng thử lại.",
                sources=[],
                confidence=0.0,
                duration_seconds=time.time() - start_time,
                session_id=input_data.session_id,
            )

        # 2. RAG: Search and generate response
        try:
            # Search for relevant documents
            query_embedding = await self.embedding_service.embed_query(transcription)
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=3,
                collection="default",
            )

            # Build context from sources
            context = "\n\n".join([
                f"Nguồn {i+1}: {result.get('text', '')}"
                for i, result in enumerate(search_results)
            ])

            # Generate response
            prompt = f"""Dựa vào ngữ cảnh sau, hãy trả lời câu hỏi.

Ngữ cảnh:
{context}

Câu hỏi: {transcription}

Trả lời bằng tiếng Việt, ngắn gọn và chính xác."""

            response = await self.llm_service.generate(prompt)

            sources = [
                {
                    "title": result.get("metadata", {}).get("title", "Unknown"),
                    "score": result.get("score", 0.0),
                    "text": result.get("text", "")[:200],
                }
                for result in search_results
            ]

        except Exception as e:
            response = f"Đã xảy ra lỗi khi xử lý: {str(e)}"
            sources = []

        duration = time.time() - start_time

        return VoiceQueryOutput(
            transcription=transcription,
            response=response,
            sources=sources,
            confidence=confidence,
            duration_seconds=duration,
            session_id=input_data.session_id,
        )


# ===== Image Query =====

@dataclass
class ImageQueryInput:
    """Input for image query."""
    image_bytes: bytes
    image_format: str
    question: Optional[str] = None
    session_id: Optional[str] = None


@dataclass
class ImageQueryOutput:
    """Output from image query."""
    description: str
    response: str
    extracted_text: Optional[str]
    detected_objects: List[str]
    related_documents: List[dict]


class ImageQueryUseCase:
    """Process image query with Vision + RAG."""

    def __init__(self, llm_service, embedding_service, vector_store, image_service):
        self.llm_service = llm_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.image_service = image_service

    async def execute(self, input_data: ImageQueryInput) -> ImageQueryOutput:
        """Execute image query."""
        try:
            # 1. Vision: Analyze image
            vision_service = self.image_service
            
            if input_data.question:
                # Answer specific question about image
                description = await vision_service.answer_question_about_image(
                    image_bytes=input_data.image_bytes,
                    question=input_data.question,
                )
                response = description
            else:
                # General analysis
                analysis = await vision_service.analyze_image(
                    image_bytes=input_data.image_bytes,
                )
                description = analysis["description"]
                response = description

            # Extract text and objects
            extracted_text = await vision_service.extract_text(input_data.image_bytes)
            
            # Get detected objects from description
            detected_objects = []
            if "đối tượng" in description.lower() or "object" in description.lower():
                # Parse objects from description
                lines = description.split("\n")
                for line in lines:
                    if any(kw in line.lower() for kw in ["đối tượng", "object", "-", "•"]):
                        obj = line.strip().lstrip("-*•123456789. ")
                        if obj and len(obj) < 50:
                            detected_objects.append(obj)

            # 2. RAG: Find related documents based on image content
            related_documents = []
            if extracted_text or description:
                try:
                    search_query = extracted_text if extracted_text else description[:500]
                    query_embedding = await self.embedding_service.embed_query(search_query)
                    
                    search_results = await self.vector_store.search(
                        query_embedding=query_embedding,
                        top_k=3,
                        collection="default",
                    )
                    
                    related_documents = [
                        {
                            "title": result.get("metadata", {}).get("title", "Unknown"),
                            "score": result.get("score", 0.0),
                            "snippet": result.get("text", "")[:200],
                        }
                        for result in search_results
                    ]
                except Exception:
                    pass  # RAG is optional for image query

            return ImageQueryOutput(
                description=description,
                response=response,
                extracted_text=extracted_text,
                detected_objects=detected_objects[:10],
                related_documents=related_documents,
            )

        except Exception as e:
            # Fallback response
            return ImageQueryOutput(
                description=f"Không thể phân tích hình ảnh: {str(e)}",
                response="Xin lỗi, tôi không thể xử lý hình ảnh này. Vui lòng thử lại hoặc mô tả nội dung hình ảnh.",
                extracted_text=None,
                detected_objects=[],
                related_documents=[],
            )


__all__ = [
    "VoiceQueryUseCase",
    "VoiceQueryInput",
    "VoiceQueryOutput",
    "ImageQueryUseCase",
    "ImageQueryInput",
    "ImageQueryOutput",
]
