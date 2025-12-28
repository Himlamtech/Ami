"""Smart Query routes with streaming support."""

import asyncio
import uuid
from fastapi import APIRouter, HTTPException, status, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from typing import AsyncIterator, Optional
import json
import logging

from api.schemas.smart_query_dto import (
    SmartQueryRequest,
    SmartQueryResponse,
    SmartQueryMetadata,
    ArtifactDTO,
    SourceReferenceDTO,
    ResponseIntentDTO,
    SourceTypeDTO,
    ArtifactDownloadResponse,
)
from application.use_cases.rag import SmartQueryWithRAGUseCase, SmartQueryInput
from application.use_cases.personalization import (
    ExtractProfileMemoryUseCase,
    ProfileMemoryExtractionInput,
)
from application.use_cases.chat import (
    CreateSessionUseCase,
    CreateSessionInput,
    SendMessageUseCase,
    SendMessageInput,
)
from application.services.conversation_context_service import (
    ConversationContextService,
)
from application.services.personalization_service import PersonalizationService
from api.dependencies.auth import get_user_id
from domain.value_objects.rag_config import RAGConfig
from domain.value_objects.generation_config import GenerationConfig
from domain.enums.llm_mode import LLMMode
from domain.enums.chat_message_role import ChatMessageRole
from config.services import ServiceRegistry
from config import qdrant_config


router = APIRouter(prefix="/smart-query", tags=["smart-query"])
logger = logging.getLogger(__name__)


def _build_profile_context(profile) -> str:
    if not profile:
        return ""
    progress = profile.get_academic_progress()
    parts = []
    if profile.name:
        parts.append(f"Họ tên: {profile.name}")
    if profile.student_id:
        parts.append(f"Mã sinh viên: {profile.student_id}")
    if profile.major:
        parts.append(f"Ngành: {profile.major}")
    if profile.class_name:
        parts.append(f"Lớp: {profile.class_name}")
    if profile.faculty:
        parts.append(f"Khoa/Viện: {profile.faculty}")
    if progress.get("current_year"):
        parts.append(f"Năm học: {progress['current_year']}")
    if progress.get("current_semester"):
        parts.append(f"Học kỳ: {progress['current_semester']}")
    return " | ".join(parts)


@router.post("", response_model=SmartQueryResponse)
async def smart_query(
    request: SmartQueryRequest,
    background_tasks: BackgroundTasks,
    x_user_id: str = Depends(get_user_id),
):
    """Smart query with artifact detection and rich response (non-streaming)."""
    request_id = f"req_{uuid.uuid4()}"
    session_id = request.session_id or f"session_{uuid.uuid4()}"
    response_message_id = f"msg_{uuid.uuid4()}"
    try:
        embedding_service = ServiceRegistry.get_embedding()
        vector_store = ServiceRegistry.get_vector_store()
        llm_service = ServiceRegistry.get_llm()
        document_repo = ServiceRegistry.get_document_repository()
        chat_repo = ServiceRegistry.get_chat_repository()

        if not all(
            [embedding_service, vector_store, llm_service, document_repo, chat_repo]
        ):
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        context_service = ConversationContextService(chat_repo)
        conversation_context = ""
        if session_id:
            try:
                context_window = await context_service.build_context_window(
                    session_id, max_messages=6
                )
                conversation_context = context_window.get_context_string()
            except Exception as exc:  # pragma: no cover - best effort context
                logger.warning(
                    "Failed to build conversation context for session %s: %s",
                    session_id,
                    exc,
                )

        profile_repo = ServiceRegistry.get_student_profile_repository()
        profile = None
        personalized_prompt = ""
        if x_user_id and x_user_id != "anonymous" and profile_repo:
            try:
                profile = await profile_repo.get_or_create(x_user_id)
                personalization = await PersonalizationService(
                    profile_repo
                ).get_personalized_context(x_user_id)
                if personalization.prompt_additions:
                    personalized_prompt = personalization.prompt_additions
            except Exception as exc:
                logger.warning("Failed to load profile for %s: %s", x_user_id, exc)

        user_context = _build_profile_context(profile)
        system_prompt = SmartQueryWithRAGUseCase.DEFAULT_SYSTEM_PROMPT
        if user_context:
            system_prompt += f"\n\nNgữ cảnh người dùng: {user_context}"
        if personalized_prompt:
            system_prompt += f"\n{personalized_prompt}"

        user_info = dict(request.user_info or {})
        if profile and "user_id" not in user_info:
            user_info["user_id"] = x_user_id
            if profile.name:
                user_info.setdefault("name", profile.name)
            if profile.student_id:
                user_info.setdefault("student_id", profile.student_id)
            if profile.class_name:
                user_info.setdefault("class_name", profile.class_name)
            if profile.faculty:
                user_info.setdefault("faculty", profile.faculty)
            if profile.major:
                user_info.setdefault("major", profile.major)
            if profile.email:
                user_info.setdefault("email", profile.email)

        use_case = SmartQueryWithRAGUseCase(
            embedding_service=embedding_service,  # type: ignore
            vector_store_service=vector_store,  # type: ignore
            llm_service=llm_service,  # type: ignore
            document_repository=document_repo,
        )

        input_data = SmartQueryInput(
            query=request.query,
            session_id=session_id,
            user_info=user_info or None,
            collection=request.collection,
            rag_config=RAGConfig(
                enabled=request.enable_rag,
                top_k=request.top_k,
                similarity_threshold=request.similarity_threshold,
                include_sources=True,
            ),
            generation_config=GenerationConfig(
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            ),
            conversation_context=conversation_context,
        )

        result = await use_case.execute(input_data)

        artifacts = [
            ArtifactDTO(
                artifact_id=a.artifact_id,
                document_id=a.document_id,
                file_name=a.file_name,
                artifact_type=a.artifact_type,
                download_url=f"/api/v1/files/{a.document_id}/download/{a.artifact_id}",
                preview_url=a.preview_url,
                size_bytes=a.size_bytes,
                size_display=a.size_display,
                is_fillable=a.is_fillable,
                fill_fields=a.fill_fields,
            )
            for a in result.artifacts
        ]

        sources = [
            SourceReferenceDTO(
                source_type=SourceTypeDTO(s.source_type.value),
                document_id=s.document_id,
                title=s.title,
                url=s.url,
                chunk_text=s.chunk_text,
                relevance_score=s.relevance_score,
            )
            for s in result.sources
        ]

        response = SmartQueryResponse(
            session_id=session_id,
            message_id=response_message_id,
            request_id=request_id,
            content=result.content,
            intent=ResponseIntentDTO(result.intent.value),
            artifacts=artifacts,
            sources=sources,
            metadata=SmartQueryMetadata(
                model_used=result.model_used,
                processing_time_ms=result.processing_time_ms,
                tokens_used=result.tokens_used,
                sources_count=len(sources),
                artifacts_count=len(artifacts),
                has_fillable_form=result.has_fillable_form(),
            ),
            created_at=result.created_at,
        )
        user_id = (user_info or {}).get("user_id")
        persisted_session_id = session_id
        assistant_message_id = None
        if user_id:
            persisted_session_id, _, assistant_message_id = await _persist_chat_history(
                user_id=user_id,
                session_id=session_id,
                user_message=request.query,
                assistant_message=result.content,
                request_id=request_id,
            )
            response.session_id = persisted_session_id
            if assistant_message_id:
                response.message_id = assistant_message_id

        if user_id or persisted_session_id:
            background_tasks.add_task(
                _run_profile_memory_extraction,
                user_id=user_id,
                session_id=persisted_session_id,
                user_message=request.query,
                assistant_message=result.content,
                conversation_history=[],
            )

        return response

    except HTTPException as exc:
        detail = exc.detail
        if isinstance(detail, dict):
            detail = {
                **detail,
                "request_id": request_id,
                "session_id": session_id,
                "message_id": response_message_id,
            }
        else:
            detail = {
                "error": detail,
                "request_id": request_id,
                "session_id": session_id,
                "message_id": response_message_id,
            }
        raise HTTPException(status_code=exc.status_code, detail=detail)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": f"Smart query failed: {str(e)}",
                "request_id": request_id,
                "session_id": session_id,
                "message_id": response_message_id,
            },
        )


@router.post("/stream")
async def smart_query_stream(
    request: SmartQueryRequest,
    x_user_id: str = Depends(get_user_id),
):
    """Smart query with streaming response (Server-Sent Events)."""

    async def event_generator() -> AsyncIterator[str]:
        assistant_chunks: list[str] = []
        request_id = f"req_{uuid.uuid4()}"
        session_id = request.session_id or f"session_{uuid.uuid4()}"
        response_message_id = f"msg_{uuid.uuid4()}"
        meta_payload = {
            "session_id": session_id,
            "message_id": response_message_id,
            "request_id": request_id,
        }
        yield f"data: {json.dumps({'meta': meta_payload})}\n\n"
        try:
            embedding_service = ServiceRegistry.get_embedding()
            vector_store = ServiceRegistry.get_vector_store()
            llm_service = ServiceRegistry.get_llm()
            document_repo = ServiceRegistry.get_document_repository()
            chat_repo = ServiceRegistry.get_chat_repository()

            if not all(
                [embedding_service, vector_store, llm_service, document_repo, chat_repo]
            ):
                yield (
                    "data: "
                    + json.dumps(
                        {
                            "error": "Required services not available",
                            "request_id": request_id,
                        }
                    )
                    + "\n\n"
                )
                return

            context_service = ConversationContextService(chat_repo)
            conversation_context = ""
            if session_id:
                try:
                    context_window = await context_service.build_context_window(
                        session_id, max_messages=6
                    )
                    conversation_context = context_window.get_context_string()
                except Exception as exc:  # pragma: no cover - best effort context
                    logger.warning(
                        "Failed to build conversation context for session %s: %s",
                        session_id,
                        exc,
                    )

            profile_repo = ServiceRegistry.get_student_profile_repository()
            profile = None
            personalized_prompt = ""
            if x_user_id and x_user_id != "anonymous" and profile_repo:
                try:
                    profile = await profile_repo.get_or_create(x_user_id)
                    personalization = await PersonalizationService(
                        profile_repo
                    ).get_personalized_context(x_user_id)
                    if personalization.prompt_additions:
                        personalized_prompt = personalization.prompt_additions
                except Exception as exc:
                    logger.warning("Failed to load profile for %s: %s", x_user_id, exc)

            user_context = _build_profile_context(profile)
            system_prompt = SmartQueryWithRAGUseCase.DEFAULT_SYSTEM_PROMPT
            if user_context:
                system_prompt += f"\n\nNgữ cảnh người dùng: {user_context}"
            if personalized_prompt:
                system_prompt += f"\n{personalized_prompt}"

            user_info = dict(request.user_info or {})
            if profile and "user_id" not in user_info:
                user_info["user_id"] = x_user_id
                if profile.name:
                    user_info.setdefault("name", profile.name)
                if profile.student_id:
                    user_info.setdefault("student_id", profile.student_id)
                if profile.class_name:
                    user_info.setdefault("class_name", profile.class_name)
                if profile.faculty:
                    user_info.setdefault("faculty", profile.faculty)
                if profile.major:
                    user_info.setdefault("major", profile.major)
                if profile.email:
                    user_info.setdefault("email", profile.email)

            # Step 1: RAG retrieval (same as non-streaming)
            input_data = SmartQueryInput(
                query=request.query,
                session_id=session_id,
                user_info=user_info or None,
                collection=request.collection or qdrant_config.collection_name,
                rag_config=RAGConfig(
                    enabled=request.enable_rag,
                    top_k=request.top_k,
                    similarity_threshold=request.similarity_threshold,
                    include_sources=True,
                ),
                generation_config=GenerationConfig(
                    temperature=request.temperature,
                    max_tokens=request.max_tokens,
                ),
                conversation_context=conversation_context,
            )

            # Get embedding and search
            query_embedding = await embedding_service.embed_text(request.query)
            search_results = await vector_store.search(
                query_embedding=query_embedding,
                top_k=input_data.rag_config.top_k,
                collection=input_data.collection or qdrant_config.collection_name,
                score_threshold=input_data.rag_config.similarity_threshold,
            )

            # Build context and sources
            use_case = SmartQueryWithRAGUseCase(
                embedding_service=embedding_service,
                vector_store_service=vector_store,
                llm_service=llm_service,
                document_repository=document_repo,
            )

            context, sources = await use_case._process_search_results(search_results)
            intent = use_case._detect_intent(request.query)

            # Send sources first
            sources_data = [
                {
                    "source_type": s.source_type.value,
                    "document_id": s.document_id,
                    "title": s.title,
                    "relevance_score": s.relevance_score,
                }
                for s in sources
            ]
            yield f"data: {json.dumps({'sources': sources_data})}\n\n"

            # Fetch artifacts if needed
            artifacts = []
            if intent in ["file_request", "form_request"]:
                wants_fillable = use_case._wants_fillable_form(request.query)
                artifacts = await use_case._fetch_artifacts(
                    search_results, wants_fillable
                )

                # Send artifacts
                artifacts_data = [
                    {
                        "artifact_id": a.artifact_id,
                        "file_name": a.file_name,
                        "artifact_type": a.artifact_type,
                        "download_url": f"/api/v1/files/{a.document_id}/download/{a.artifact_id}",
                    }
                    for a in artifacts
                ]
                yield f"data: {json.dumps({'artifacts': artifacts_data})}\n\n"

            # Build prompt
            full_prompt = use_case._build_prompt(
                query=request.query,
                context=context,
                has_artifacts=len(artifacts) > 0,
                system_prompt=system_prompt,
                conversation_context=conversation_context,
            )

            # Stream generation
            async for chunk in llm_service.stream_generate(
                prompt=full_prompt,
                temperature=input_data.generation_config.temperature,
                max_tokens=input_data.generation_config.max_tokens,
            ):
                # Send each content chunk
                assistant_chunks.append(chunk)
                yield f"data: {json.dumps({'content': chunk})}\n\n"

            # Send completion signal
            user_id = (user_info or {}).get("user_id")
            persisted_session_id = session_id
            assistant_message_id = None
            if user_id:
                persisted_session_id, _, assistant_message_id = (
                    await _persist_chat_history(
                        user_id=user_id,
                        session_id=session_id,
                        user_message=request.query,
                        assistant_message="".join(assistant_chunks),
                        request_id=request_id,
                    )
                )

            if assistant_message_id:
                meta_payload = {
                    "session_id": persisted_session_id,
                    "message_id": assistant_message_id,
                    "request_id": request_id,
                }
                yield f"data: {json.dumps({'meta': meta_payload})}\n\n"

            if user_id or persisted_session_id:
                await _run_profile_memory_extraction(
                    user_id=user_id,
                    session_id=persisted_session_id,
                    user_message=request.query,
                    assistant_message="".join(assistant_chunks),
                    conversation_history=[],
                )
            yield "data: [DONE]\n\n"

        except Exception as e:
            yield (
                "data: "
                + json.dumps({"error": str(e), "request_id": request_id})
                + "\n\n"
            )

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/files/{document_id}/download/{artifact_id}")
async def download_artifact(document_id: str, artifact_id: str):
    """Download a specific artifact from a document."""
    try:
        document_repo = ServiceRegistry.get_document_repository()
        storage = ServiceRegistry.get_storage()

        if not document_repo or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        document = await document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        artifact = None
        for idx, a in enumerate(document.artifacts):
            if artifact_id == f"{document_id}_artifact_{idx}":
                artifact = a
                break

        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_id} not found",
            )

        download_url = await storage.generate_presigned_url(
            bucket="data",
            key=artifact.url,
            expires_in=3600,
        )

        return ArtifactDownloadResponse(
            download_url=download_url,
            file_name=artifact.file_name,
            mime_type=artifact.mime_type,
            size_bytes=artifact.size_bytes,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Download failed: {str(e)}",
        )


@router.get("/files/{document_id}/preview/{artifact_id}")
async def preview_artifact(document_id: str, artifact_id: str):
    """Get preview URL for an artifact."""
    try:
        document_repo = ServiceRegistry.get_document_repository()
        storage = ServiceRegistry.get_storage()

        if not document_repo or not storage:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Required services not available",
            )

        document = await document_repo.get_by_id(document_id)
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found",
            )

        artifact = None
        for idx, a in enumerate(document.artifacts):
            if artifact_id == f"{document_id}_artifact_{idx}":
                artifact = a
                break

        if not artifact:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Artifact {artifact_id} not found",
            )

        if not artifact.is_previewable():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {artifact.mime_type} is not previewable",
            )

        if artifact.preview_url:
            preview_url = artifact.preview_url
        else:
            preview_url = await storage.generate_presigned_url(
                bucket="data",
                key=artifact.url,
                expires_in=3600,
            )

        return {
            "preview_url": preview_url,
            "file_name": artifact.file_name,
            "mime_type": artifact.mime_type,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Preview failed: {str(e)}",
        )


async def _run_profile_memory_extraction(
    user_id: Optional[str],
    session_id: Optional[str],
    user_message: str,
    assistant_message: str,
    conversation_history: list,
) -> None:
    try:
        profile_repo = ServiceRegistry.get_student_profile_repository()
        chat_repo = ServiceRegistry.get_chat_repository()
        llm_service = ServiceRegistry.get_llm(mode=LLMMode.QA)
        if not profile_repo:
            return
        use_case = ExtractProfileMemoryUseCase(
            profile_repository=profile_repo,
            llm_service=llm_service,
            chat_repository=chat_repo,
        )
        await use_case.execute(
            ProfileMemoryExtractionInput(
                user_id=user_id,
                session_id=session_id,
                user_message=user_message,
                assistant_message=assistant_message,
                conversation_history=conversation_history or [],
            )
        )
    except Exception as exc:
        logger.warning("Profile memory extraction failed: %s", exc)


async def _persist_chat_history(
    user_id: str,
    session_id: str,
    user_message: str,
    assistant_message: str,
    request_id: str,
) -> tuple[str, Optional[str], Optional[str]]:
    try:
        chat_repo = ServiceRegistry.get_chat_repository()
        if not chat_repo:
            return session_id, None, None

        # Only persist if there's at least one message to save
        if not user_message and not assistant_message:
            return session_id, None, None

        resolved_session_id = session_id
        if resolved_session_id:
            session = await chat_repo.get_session_by_id(resolved_session_id)
        else:
            session = None

        # Only create session if we actually have messages to save
        if not session:
            create_use_case = CreateSessionUseCase(chat_repo)
            created = await create_use_case.execute(
                CreateSessionInput(
                    user_id=user_id,
                    session_id=resolved_session_id or None,
                    title="New Conversation",
                )
            )
            resolved_session_id = created.session.id

        send_use_case = SendMessageUseCase(chat_repo)
        user_message_id = None
        assistant_message_id = None
        if user_message:
            result = await send_use_case.execute(
                SendMessageInput(
                    session_id=resolved_session_id,
                    role=ChatMessageRole.USER,
                    content=user_message,
                    metadata={"source": "smart_query", "request_id": request_id},
                )
            )
            user_message_id = result.message.id
        if assistant_message:
            result = await send_use_case.execute(
                SendMessageInput(
                    session_id=resolved_session_id,
                    role=ChatMessageRole.ASSISTANT,
                    content=assistant_message,
                    metadata={"source": "smart_query", "request_id": request_id},
                )
            )
            assistant_message_id = result.message.id

        return resolved_session_id, user_message_id, assistant_message_id
    except Exception as exc:
        logger.warning("Chat persistence failed: %s", exc)
        return session_id, None, None


__all__ = ["router"]
