"""Entity to MongoDB model mappers.

These mappers handle conversion between domain entities (pure Python)
and MongoDB models (Pydantic with database-specific fields).
"""

from typing import Optional
from datetime import datetime
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
            title=model.title if hasattr(model, 'title') else model.filename,
            file_name=model.filename,
            content=model.content if hasattr(model, 'content') else None,
            collection=model.collection,
            metadata=model.metadata,
            tags=model.tags if hasattr(model, 'tags') else [],
            chunk_count=model.chunk_count,
            vector_ids=[],  # Not stored in MongoDB, managed separately
            file_path=model.file_path if hasattr(model, 'file_path') else None,
            file_size=model.file_size if hasattr(model, 'file_size') else None,
            mime_type=model.mime_type if hasattr(model, 'mime_type') else None,
            is_active=model.is_active,
            created_by=model.created_by if hasattr(model, 'created_by') else None,
            created_at=model.created_at,
            updated_at=model.updated_at if hasattr(model, 'updated_at') else model.created_at,
        )
    
    @staticmethod
    def to_model(entity: Document) -> DocumentInDB:
        """Convert domain entity to MongoDB model."""
        return DocumentInDB(
            id=entity.id or "",
            filename=entity.file_name,
            collection=entity.collection,
            metadata=entity.metadata,
            chunk_count=entity.chunk_count,
            is_active=entity.is_active,
            created_at=entity.created_at,
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
        from app.infrastructure.persistence.mongodb.models import ChatMessageRole as DBRole
        
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
