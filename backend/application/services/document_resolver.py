"""DocumentResolver service responsible for summary, similarity search, and LLM triage."""

import json
import logging
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.application.interfaces.services.embedding_service import IEmbeddingService
from app.application.interfaces.services.vector_store_service import IVectorStoreService
from app.application.interfaces.services.llm_service import ILLMService
from app.domain.enums.data_source import UpdateDetectionType
from app.domain.enums.llm_mode import LLMMode

logger = logging.getLogger(__name__)


@dataclass
class CandidateDocument:
    id: Optional[str]
    title: Optional[str]
    summary: str
    score: float
    source_url: Optional[str]


@dataclass
class ResolutionResult:
    action: UpdateDetectionType
    reason: Optional[str]
    updated_id: Optional[str]
    summary: str
    candidates: List[CandidateDocument]


class DocumentResolver:
    """Resolve whether crawled content is new, update, or low-value."""

    def __init__(
        self,
        embedding_service: IEmbeddingService,
        vector_store: IVectorStoreService,
        llm_service: ILLMService,
    ):
        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.llm = llm_service

    async def resolve(
        self,
        *,
        title: str,
        content: str,
        collection: str,
        source_url: str,
        category: str,
        max_candidates: int = 5,
    ) -> ResolutionResult:
        summary = await self._summarize(content)
        candidates = await self._search_similar(
            title, summary, collection, max_candidates
        )
        raw_action, reason, updated_id = await self._classify(
            title, summary, candidates
        )
        action_enum = self._map_action(raw_action)

        return ResolutionResult(
            action=action_enum,
            reason=reason,
            updated_id=updated_id,
            summary=summary,
            candidates=candidates,
        )

    async def _summarize(self, content: str) -> str:
        prompt = (
            "Tóm tắt thông báo sau trong <=80 từ để dùng cho hệ thống triage.\n"
            "Chỉ trả lời phần tóm tắt tiếng Việt, không thêm giải thích.\n\n"
            f"{content[:4000]}"
        )
        try:
            summary = (await self.llm.generate(prompt, mode=LLMMode.QA)).strip()
            return summary or content[:500]
        except Exception as e:
            logger.warning("LLM summary failed: %s", e)
            return content[:500]

    async def _search_similar(
        self, title: str, summary: str, collection: str, max_candidates: int
    ) -> List[CandidateDocument]:
        combined = f"Tiêu đề: {title}\nTóm tắt: {summary}"
        try:
            query_vector = await self.embedding_service.embed_text(combined)
            results = await self.vector_store.search(
                query_embedding=query_vector,
                top_k=max_candidates,
                collection=collection,
            )
        except Exception as e:
            logger.warning("Vector search failed: %s", e)
            return []

        candidates: List[CandidateDocument] = []
        for item in results:
            metadata = item.get("metadata", {}) or {}
            candidates.append(
                CandidateDocument(
                    id=metadata.get("document_id") or metadata.get("doc_id"),
                    title=metadata.get("title") or metadata.get("file_name"),
                    summary=metadata.get("summary")
                    or (item.get("content") or "")[:400],
                    score=float(item.get("score", 0.0)),
                    source_url=metadata.get("source_url"),
                )
            )
        return candidates

    async def _classify(
        self, title: str, summary: str, candidates: List[CandidateDocument]
    ) -> (int, Optional[str], Optional[str]):
        candidate_lines = []
        for idx, cand in enumerate(candidates, start=1):
            candidate_lines.append(
                f"{idx}. id={cand.id}; score={cand.score:.3f}; title={cand.title}; "
                f"source={cand.source_url}; summary={cand.summary}"
            )
        candidate_block = (
            "\n".join(candidate_lines)
            if candidate_lines
            else "Không có dữ liệu gần nhất."
        )

        prompt = (
            "Bạn là hệ thống phân loại thông báo PTIT.\n"
            "Quy tắc:\n"
            "- action=1 nếu nội dung mới và hữu ích.\n"
            "- action=0 nếu giá trị thấp/không liên quan.\n"
            "- action=2 nếu đây là bản cập nhật của một nội dung cũ (ghi rõ updated_id nếu biết).\n\n"
            f"Thông báo mới:\nTiêu đề: {title}\nTóm tắt: {summary}\n\n"
            f"Các thông báo gần nhất:\n{candidate_block}\n\n"
            'Chỉ trả về JSON: {"action":1|0|2,"reason":"...", "updated_id":"id|null"}'
        )

        raw_action = 1
        reason = None
        updated_id = None

        try:
            raw_response = await self.llm.generate(prompt, mode=LLMMode.REASONING)
            parsed = self._parse_json(raw_response)
            raw_action = int(parsed.get("action", 1))
            reason = parsed.get("reason")
            updated_id = parsed.get("updated_id")
        except Exception as e:
            logger.warning("LLM classification failed: %s", e)

        return (
            raw_action,
            reason,
            updated_id if updated_id not in ("", "null") else None,
        )

    @staticmethod
    def _parse_json(raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except Exception:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(0))
                except Exception:
                    return {}
        return {}

    @staticmethod
    def _map_action(raw_action: int) -> UpdateDetectionType:
        if raw_action == 2:
            return UpdateDetectionType.UPDATE
        if raw_action == 0:
            return UpdateDetectionType.UNRELATED
        return UpdateDetectionType.NEW
