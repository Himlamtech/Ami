"""Voice Query use case - STT + RAG pipeline."""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any

from application.interfaces.services.stt_service import ISTTService
from application.interfaces.services.vector_store_service import IVectorStoreService
from application.interfaces.services.embedding_service import IEmbeddingService
from application.interfaces.services.llm_service import ILLMService
from application.interfaces.repositories.chat_repository import IChatRepository
from domain.entities.chat_message import ChatMessage


@dataclass
class VoiceQueryInput:
    """Input for voice query."""

    audio_bytes: bytes
    audio_format: str = "wav"
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    language: str = "vi"


@dataclass
class VoiceQueryOutput:
    """Output from voice query."""

    transcription: str
    response: str
    sources: List[Dict[str, Any]]
    confidence: float
    duration_seconds: float

    # Session tracking
    session_id: Optional[str] = None
    message_id: Optional[str] = None


class VoiceQueryUseCase:
    """
    Use Case: Process voice query through STT and RAG.

    Pipeline:
    1. Transcribe audio to text (STT)
    2. Search relevant documents (RAG)
    3. Generate response (LLM)
    4. Save to chat history (optional)

    Single Responsibility: Voice-to-response pipeline
    """

    def __init__(
        self,
        stt_service: ISTTService,
        embedding_service: Optional[IEmbeddingService],
        vector_store: IVectorStoreService,
        llm_service: ILLMService,
        chat_repository: Optional[IChatRepository] = None,
    ):
        self.stt_service = stt_service
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm_service = llm_service
        self.chat_repo = chat_repository

    async def execute(self, input_data: VoiceQueryInput) -> VoiceQueryOutput:
        """
        Process voice query.

        Args:
            input_data: Voice query parameters

        Returns:
            VoiceQueryOutput with transcription and response
        """
        # 1. Transcribe audio to text
        transcription_result = await self.stt_service.transcribe(
            audio_data=input_data.audio_bytes,
            language=input_data.language,
        )

        transcription = transcription_result.get("text", "").strip()
        confidence = transcription_result.get("confidence", 0.0)
        duration = transcription_result.get("duration", 0.0)

        # Check if transcription is empty
        if not transcription:
            return VoiceQueryOutput(
                transcription="",
                response="Xin lỗi, tôi không nghe rõ. Vui lòng thử lại.",
                sources=[],
                confidence=0.0,
                duration_seconds=duration,
            )

        # 2. Search relevant documents (via embeddings)
        search_results = []
        if self.embedding_service:
            query_embedding = await self.embedding_service.embed_text(transcription)
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=5,
                score_threshold=0.5,
            )

        # 3. Build context from search results
        context_parts = []
        sources = []

        for result in search_results:
            context_parts.append(result.get("content", ""))
            sources.append(
                {
                    "title": result.get("metadata", {}).get("title", "Unknown"),
                    "score": result.get("score", 0.0),
                }
            )

        context = "\n\n".join(context_parts)

        # 4. Generate response
        response = await self._generate_response(transcription, context)

        # 5. Save to chat history (if session provided)
        message_id = None
        if self.chat_repo and input_data.session_id:
            user_msg = ChatMessage(
                id="",
                session_id=input_data.session_id,
                role=MessageRole.USER,
                content=transcription,
                metadata={"source": "voice", "duration": duration},
            )
            saved_user_msg = await self.chat_repo.add_message(user_msg)

            assistant_msg = ChatMessage(
                id="",
                session_id=input_data.session_id,
                role=MessageRole.ASSISTANT,
                content=response,
                metadata={"sources": [s["title"] for s in sources]},
            )
            saved_assistant_msg = await self.chat_repo.add_message(assistant_msg)
            message_id = saved_assistant_msg.id

        return VoiceQueryOutput(
            transcription=transcription,
            response=response,
            sources=sources,
            confidence=confidence,
            duration_seconds=duration,
            session_id=input_data.session_id,
            message_id=message_id,
        )

    async def _generate_response(self, query: str, context: str) -> str:
        """Generate response using LLM."""
        if not context:
            # No relevant context found
            prompt = f"""Bạn là trợ lý AI của Học viện Công nghệ Bưu chính Viễn thông (PTIT).
Người dùng hỏi qua giọng nói: "{query}"

Hiện tại không tìm thấy thông tin liên quan trong cơ sở dữ liệu.
Hãy trả lời lịch sự và đề nghị người dùng hỏi rõ hơn hoặc liên hệ phòng ban phù hợp."""
        else:
            prompt = f"""Bạn là trợ lý AI của Học viện Công nghệ Bưu chính Viễn thông (PTIT).

Thông tin tham khảo:
{context}

Câu hỏi (từ giọng nói): {query}

Hãy trả lời ngắn gọn, rõ ràng, phù hợp với ngữ cảnh hội thoại bằng giọng nói."""

        response = await self.llm_service.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=300,  # Shorter for voice responses
        )

        return response.strip()
