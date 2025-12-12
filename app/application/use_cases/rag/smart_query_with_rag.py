"""Query with smart artifact response use case."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.domain.value_objects.rag_config import RAGConfig
from app.domain.value_objects.generation_config import GenerationConfig
from app.domain.value_objects.chat_response import (
    ResponseIntent,
    SourceType,
    SourceReference,
    ArtifactReference,
    RichChatResponse,
)
from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.services.llm_service import ILLMService
from app.application.interfaces.repositories.document_repository import (
    IDocumentRepository,
)


# Keywords for artifact/file request detection (Vietnamese)
ARTIFACT_KEYWORDS = [
    # Form/template requests
    "mẫu đơn",
    "mẫu biểu",
    "tải mẫu",
    "xin mẫu",
    "cho mẫu",
    "form",
    "đơn xin",
    "biểu mẫu",
    "file mẫu",
    "template",
    # Download requests
    "tải file",
    "download",
    "tải về",
    "xin file",
    "cho file",
    "lấy file",
    "tải xuống",
    "file",
    "tài liệu",
    # Document requests
    "quy trình",
    "hướng dẫn làm",
    "mẫu giấy",
    "giấy tờ",
    # Specific forms
    "đơn nghỉ học",
    "đơn xin vắng",
    "đơn đăng ký",
    "giấy xác nhận",
]

# Keywords for form filling intent
FILLABLE_KEYWORDS = [
    "điền",
    "điền sẵn",
    "điền giúp",
    "điền thông tin",
    "fill",
    "tự động điền",
    "điền form",
]


@dataclass
class SmartQueryInput:
    """Input for smart query with artifact support."""

    query: str
    session_id: Optional[str] = None
    user_info: Optional[Dict[str, Any]] = None  # For form auto-fill
    collection: Optional[str] = "ami"
    rag_config: Optional[RAGConfig] = None
    generation_config: Optional[GenerationConfig] = None
    system_prompt: Optional[str] = None


class SmartQueryWithRAGUseCase:
    """
    Use Case: Smart Query with Artifact Response.

    Business Rules:
    1. Detect user intent from query
    2. If file/form request detected:
       - Search for relevant documents with artifacts
       - Return artifact download links
    3. If fillable form request:
       - Find form template
       - Include fill fields for frontend
    4. Always provide helpful answer + context

    Single Responsibility: Smart RAG with artifact delivery
    """

    DEFAULT_SYSTEM_PROMPT = """Bạn là AMI - trợ lý thông minh của Học viện Công nghệ Bưu chính Viễn thông (PTIT).
Nhiệm vụ: Hỗ trợ sinh viên, giảng viên và người quan tâm tìm hiểu về PTIT.

Quy tắc trả lời:
1. Trả lời ngắn gọn, chính xác dựa trên nguồn tin cung cấp
2. Nếu có file/mẫu đơn liên quan, thông báo cho người dùng biết
3. Nếu không chắc chắn, nói rõ và hướng dẫn liên hệ phòng ban phù hợp
4. Sử dụng tiếng Việt tự nhiên, thân thiện"""

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store_service: IVectorStoreService,
        llm_service: ILLMService,
        document_repository: IDocumentRepository,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store_service
        self.llm_service = llm_service
        self.document_repo = document_repository

    async def execute(self, input_data: SmartQueryInput) -> RichChatResponse:
        """
        Execute smart query with artifact detection.

        Args:
            input_data: Query and configuration

        Returns:
            RichChatResponse with content and artifacts
        """
        import time

        start_time = time.time()

        # Use defaults
        rag_config = input_data.rag_config or RAGConfig()
        gen_config = input_data.generation_config or GenerationConfig.balanced()

        # 1. Detect intent
        intent = self._detect_intent(input_data.query)
        wants_fillable = self._wants_fillable_form(input_data.query)

        # 2. Perform RAG retrieval
        sources: List[SourceReference] = []
        artifacts: List[ArtifactReference] = []
        context = ""

        if rag_config.enabled:
            # Generate query embedding
            query_embedding = await self.embedding_service.embed_text(input_data.query)

            # Search vector store
            search_results = await self.vector_store.search(
                query_embedding=query_embedding,
                top_k=rag_config.top_k,
                collection=input_data.collection,
                metadata_filter=rag_config.metadata_filter,
                score_threshold=rag_config.similarity_threshold,
            )

            # Build sources and context
            context, sources = await self._process_search_results(search_results)

            # 3. If artifact intent, fetch artifacts from source documents
            if intent in [ResponseIntent.FILE_REQUEST, ResponseIntent.FORM_REQUEST]:
                artifacts = await self._fetch_artifacts(
                    search_results, wants_fillable=wants_fillable
                )

        # 4. Build prompt with artifact context
        full_prompt = self._build_prompt(
            query=input_data.query,
            context=context,
            has_artifacts=len(artifacts) > 0,
            system_prompt=input_data.system_prompt or self.DEFAULT_SYSTEM_PROMPT,
        )

        # 5. Generate answer
        answer = await self.llm_service.generate(
            prompt=full_prompt,
            temperature=gen_config.temperature,
            max_tokens=gen_config.max_tokens,
            top_p=gen_config.top_p,
        )

        # Calculate processing time
        processing_time = (time.time() - start_time) * 1000

        # 6. Build rich response
        response = RichChatResponse(
            content=answer,
            intent=intent,
            artifacts=artifacts,
            sources=sources,
            model_used=getattr(self.llm_service, "model_name", ""),
            processing_time_ms=processing_time,
        )

        return response

    def _detect_intent(self, query: str) -> ResponseIntent:
        """Detect user intent from query."""
        query_lower = query.lower()

        # Check for file/form request keywords
        for keyword in ARTIFACT_KEYWORDS:
            if keyword in query_lower:
                # More specific: form or file?
                if any(
                    k in query_lower for k in ["mẫu đơn", "form", "đơn xin", "biểu mẫu"]
                ):
                    return ResponseIntent.FORM_REQUEST
                return ResponseIntent.FILE_REQUEST

        # Check for procedure/guide request
        if any(
            k in query_lower for k in ["quy trình", "cách làm", "hướng dẫn", "thủ tục"]
        ):
            return ResponseIntent.PROCEDURE_GUIDE

        # Check for contact info
        if any(
            k in query_lower for k in ["liên hệ", "số điện thoại", "email", "địa chỉ"]
        ):
            return ResponseIntent.CONTACT_INFO

        # Check for navigation
        if any(k in query_lower for k in ["đường đi", "chỉ đường", "ở đâu", "vị trí"]):
            return ResponseIntent.NAVIGATION

        return ResponseIntent.GENERAL_ANSWER

    def _wants_fillable_form(self, query: str) -> bool:
        """Check if user wants a pre-filled form."""
        query_lower = query.lower()
        return any(k in query_lower for k in FILLABLE_KEYWORDS)

    async def _process_search_results(
        self, search_results: List[Dict[str, Any]]
    ) -> tuple[str, List[SourceReference]]:
        """Process search results into context and sources."""
        context_parts = []
        sources = []

        for i, result in enumerate(search_results, 1):
            content = result.get("content", "")
            score = result.get("score", 0.0)
            doc_id = result.get("document_id", "")
            title = result.get("metadata", {}).get("title", f"Source {i}")

            context_parts.append(f"[{i}] {content}")

            sources.append(
                SourceReference(
                    source_type=SourceType.DOCUMENT,
                    document_id=doc_id,
                    title=title,
                    chunk_text=content[:200] + "..." if len(content) > 200 else content,
                    relevance_score=score,
                )
            )

        context = "\n\n".join(context_parts)
        return context, sources

    async def _fetch_artifacts(
        self, search_results: List[Dict[str, Any]], wants_fillable: bool = False
    ) -> List[ArtifactReference]:
        """Fetch artifacts from source documents."""
        artifacts = []
        seen_doc_ids = set()

        for result in search_results:
            doc_id = result.get("document_id", "")
            if not doc_id or doc_id in seen_doc_ids:
                continue

            seen_doc_ids.add(doc_id)

            # Fetch full document
            document = await self.document_repo.get_by_id(doc_id)
            if not document or not document.has_artifacts():
                continue

            # Add artifacts from document
            for idx, artifact in enumerate(document.artifacts):
                # If wants fillable, prioritize fillable forms
                if wants_fillable and not artifact.is_fillable:
                    continue

                artifact_ref = ArtifactReference(
                    artifact_id=f"{doc_id}_artifact_{idx}",
                    document_id=doc_id,
                    file_name=artifact.file_name,
                    artifact_type=artifact.artifact_type.value,
                    download_url=artifact.url,
                    preview_url=artifact.preview_url,
                    size_bytes=artifact.size_bytes,
                    is_fillable=artifact.is_fillable,
                    fill_fields=artifact.fill_fields,
                )
                artifacts.append(artifact_ref)

        return artifacts

    def _build_prompt(
        self,
        query: str,
        context: str,
        has_artifacts: bool,
        system_prompt: str,
    ) -> str:
        """Build full prompt for LLM."""
        parts = [f"System: {system_prompt}"]

        if context:
            parts.append(f"\nThông tin tham khảo:\n{context}")

        if has_artifacts:
            parts.append(
                "\n(Lưu ý: Có file/mẫu đơn liên quan sẽ được hiển thị cho người dùng)"
            )

        parts.append(f"\nCâu hỏi: {query}")
        parts.append("\nTrả lời:")

        return "\n".join(parts)
