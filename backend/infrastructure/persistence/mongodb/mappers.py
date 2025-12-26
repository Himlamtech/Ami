"""Entity to MongoDB model mappers.

These mappers handle conversion between domain entities (pure Python)
and MongoDB models (Pydantic with database-specific fields).
"""

from app.domain.entities.document import Document
from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage
from app.infrastructure.persistence.mongodb.models import (
    DocumentInDB,
    ChatSessionInDB,
    ChatMessageInDB,
)


class DocumentMapper:
    """Mapper for Document entity ↔ MongoDB model."""

    @staticmethod
    def to_entity(model: DocumentInDB) -> Document:
        """Convert MongoDB model to domain entity."""
        return Document(
            id=model.id,
            title=model.title,
            file_name=model.file_name,
            source=model.metadata.get("source"),
            content=model.content,
            collection=model.collection,
            metadata=model.metadata,
            tags=model.tags,
            chunk_count=model.chunk_count,
            vector_ids=model.vector_ids,
            file_path=None,
            file_size=None,
            mime_type=None,
            is_active=model.is_active,
            created_by=model.created_by,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: Document) -> DocumentInDB:
        """Convert domain entity to MongoDB model."""
        metadata = dict(entity.metadata or {})
        if entity.source:
            metadata.setdefault("source", entity.source)

        return DocumentInDB(
            id=entity.id or "",
            title=entity.title,
            file_name=entity.file_name or entity.title,
            content=entity.content,
            collection=entity.collection,
            metadata=metadata,
            tags=entity.tags,
            chunk_count=entity.chunk_count,
            vector_ids=entity.vector_ids,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            created_by=entity.created_by,
        )


class ChatSessionMapper:
    """Mapper for ChatSession entity ↔ MongoDB model."""

    @staticmethod
    def to_entity(model: ChatSessionInDB) -> ChatSession:
        """Convert MongoDB model to domain entity."""
        return ChatSession(
            id=model.id,
            user_id=model.user_id,
            title=model.title,
            summary=model.summary,
            metadata=model.metadata,
            tags=model.tags,
            is_archived=model.is_archived,
            is_deleted=model.is_deleted,
            message_count=model.message_count,
            last_message_at=model.last_message_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    @staticmethod
    def to_model(entity: ChatSession) -> ChatSessionInDB:
        """Convert domain entity to MongoDB model."""
        return ChatSessionInDB(
            id=entity.id or "",
            user_id=entity.user_id,
            title=entity.title,
            summary=entity.summary,
            metadata=entity.metadata,
            tags=entity.tags,
            is_archived=entity.is_archived,
            is_deleted=entity.is_deleted,
            message_count=entity.message_count,
            last_message_at=entity.last_message_at,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class ChatMessageMapper:
    """Mapper for ChatMessage entity ↔ MongoDB model."""

    @staticmethod
    def to_entity(model: ChatMessageInDB) -> ChatMessage:
        """Convert MongoDB model to domain entity."""
        from app.domain.enums.chat_message_role import ChatMessageRole

        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=ChatMessageRole(model.role.value),
            content=model.content,
            attachments=model.attachments,
            metadata=model.metadata,
            is_deleted=model.is_deleted,
            created_at=model.created_at,
            edited_at=model.edited_at,
        )

    @staticmethod
    def to_model(entity: ChatMessage) -> ChatMessageInDB:
        """Convert domain entity to MongoDB model."""
        from app.infrastructure.persistence.mongodb.models import (
            ChatMessageRole as DBRole,
        )

        return ChatMessageInDB(
            id=entity.id or "",
            session_id=entity.session_id,
            role=DBRole(entity.role.value),
            content=entity.content,
            attachments=entity.attachments,
            metadata=entity.metadata,
            is_deleted=entity.is_deleted,
            created_at=entity.created_at,
            edited_at=entity.edited_at,
        )
