"""MongoDB Chat Repository implementation."""

from typing import Optional, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId


def _coerce_object_id(value: str):
    try:
        return ObjectId(value)
    except Exception:
        return None


from app.domain.entities.chat_session import ChatSession
from app.domain.entities.chat_message import ChatMessage
from app.application.interfaces.repositories.chat_repository import IChatRepository
from app.infrastructure.persistence.mongodb.mappers import (
    ChatSessionMapper,
    ChatMessageMapper,
)
from app.infrastructure.persistence.mongodb.models import (
    ChatSessionInDB,
    ChatMessageInDB,
)


class MongoDBChatRepository(IChatRepository):
    """MongoDB implementation of Chat Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.sessions_collection = db["chat_sessions"]
        self.messages_collection = db["chat_messages"]

    # ===== Session Methods =====

    async def create_session(self, session: ChatSession) -> ChatSession:
        """Create new chat session."""
        session_model = ChatSessionMapper.to_model(session)
        session_dict = session_model.dict(by_alias=True, exclude={"id"})
        if session.id:
            session_dict["_id"] = session.id

        result = await self.sessions_collection.insert_one(session_dict)
        session.id = str(result.inserted_id)
        return session

    async def get_session_by_id(self, session_id: str) -> Optional[ChatSession]:
        """Get chat session by ID."""
        doc = await self.sessions_collection.find_one({"_id": session_id})
        if not doc:
            obj_id = _coerce_object_id(session_id)
            if obj_id is not None:
                doc = await self.sessions_collection.find_one({"_id": obj_id})

        if not doc:
            return None

        doc["id"] = str(doc.pop("_id"))
        session_model = ChatSessionInDB(**doc)
        return ChatSessionMapper.to_entity(session_model)

    async def update_session(self, session: ChatSession) -> ChatSession:
        """Update chat session."""
        session_model = ChatSessionMapper.to_model(session)
        session_dict = session_model.dict(by_alias=True, exclude={"id"})

        result = await self.sessions_collection.update_one(
            {"_id": session.id}, {"$set": session_dict}
        )
        if result.matched_count == 0:
            obj_id = _coerce_object_id(session.id)
            if obj_id is not None:
                await self.sessions_collection.update_one(
                    {"_id": obj_id}, {"$set": session_dict}
                )

        return session

    async def delete_session(self, session_id: str) -> bool:
        """Delete chat session (soft delete)."""
        result = await self.sessions_collection.update_one(
            {"_id": session_id}, {"$set": {"is_deleted": True}}
        )
        if result.modified_count > 0:
            return True

        obj_id = _coerce_object_id(session_id)
        if obj_id is None:
            return False
        result = await self.sessions_collection.update_one(
            {"_id": obj_id}, {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    async def list_sessions_by_user(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
        include_archived: bool = False,
    ) -> List[ChatSession]:
        """List sessions by user."""
        query = {"user_id": user_id, "is_deleted": False}
        if not include_archived:
            query["is_archived"] = False

        cursor = (
            self.sessions_collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        sessions = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            session_model = ChatSessionInDB(**doc)
            sessions.append(ChatSessionMapper.to_entity(session_model))

        return sessions

    async def count_sessions_by_user(
        self,
        user_id: str,
        include_archived: bool = False,
    ) -> int:
        """Count sessions by user."""
        query = {"user_id": user_id, "is_deleted": False}
        if not include_archived:
            query["is_archived"] = False

        return await self.sessions_collection.count_documents(query)

    # ===== Message Methods =====

    async def create_message(self, message: ChatMessage) -> ChatMessage:
        """Create new chat message."""
        message_model = ChatMessageMapper.to_model(message)
        message_dict = message_model.dict(by_alias=True, exclude={"id"})

        result = await self.messages_collection.insert_one(message_dict)
        message.id = str(result.inserted_id)
        return message

    async def get_message_by_id(self, message_id: str) -> Optional[ChatMessage]:
        """Get message by ID."""
        try:
            doc = await self.messages_collection.find_one({"_id": ObjectId(message_id)})
        except:
            return None

        if not doc:
            return None

        doc["id"] = str(doc.pop("_id"))
        message_model = ChatMessageInDB(**doc)
        return ChatMessageMapper.to_entity(message_model)

    async def update_message(self, message: ChatMessage) -> ChatMessage:
        """Update message."""
        message_model = ChatMessageMapper.to_model(message)
        message_dict = message_model.dict(by_alias=True, exclude={"id"})

        await self.messages_collection.update_one(
            {"_id": ObjectId(message.id)}, {"$set": message_dict}
        )

        return message

    async def delete_message(self, message_id: str) -> bool:
        """Delete message (soft delete)."""
        result = await self.messages_collection.update_one(
            {"_id": ObjectId(message_id)}, {"$set": {"is_deleted": True}}
        )
        return result.modified_count > 0

    async def list_messages_by_session(
        self,
        session_id: str,
        skip: int = 0,
        limit: int = 100,
        include_deleted: bool = False,
    ) -> List[ChatMessage]:
        """List messages by session."""
        query = {"session_id": session_id}
        if not include_deleted:
            query["is_deleted"] = False

        cursor = (
            self.messages_collection.find(query)
            .sort("created_at", 1)
            .skip(skip)
            .limit(limit)
        )
        messages = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            message_model = ChatMessageInDB(**doc)
            messages.append(ChatMessageMapper.to_entity(message_model))

        return messages

    async def count_messages_by_session(
        self,
        session_id: str,
        include_deleted: bool = False,
    ) -> int:
        """Count messages in session."""
        query = {"session_id": session_id}
        if not include_deleted:
            query["is_deleted"] = False

        return await self.messages_collection.count_documents(query)

    async def get_recent_messages(
        self,
        session_id: str,
        limit: int = 10,
    ) -> List[ChatMessage]:
        """Get recent messages from session."""
        cursor = (
            self.messages_collection.find(
                {"session_id": session_id, "is_deleted": False}
            )
            .sort("created_at", -1)
            .limit(limit)
        )

        messages = []
        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            message_model = ChatMessageInDB(**doc)
            messages.append(ChatMessageMapper.to_entity(message_model))

        return messages

    # ===== Admin Methods =====

    async def find_all_sessions(
        self,
        user_id: Optional[str] = None,
        date_from=None,
        date_to=None,
        is_archived: Optional[bool] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[ChatSession]:
        """Find all sessions with admin filters."""
        query = {"is_deleted": False}

        if user_id:
            query["user_id"] = user_id
        if is_archived is not None:
            query["is_archived"] = is_archived
        if date_from:
            query["created_at"] = {"$gte": date_from}
        if date_to:
            if "created_at" in query:
                query["created_at"]["$lte"] = date_to
            else:
                query["created_at"] = {"$lte": date_to}

        cursor = (
            self.sessions_collection.find(query)
            .sort("updated_at", -1)
            .skip(skip)
            .limit(limit)
        )
        sessions = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            session_model = ChatSessionInDB(**doc)
            sessions.append(ChatSessionMapper.to_entity(session_model))

        return sessions

    async def count_all_sessions(
        self,
        user_id: Optional[str] = None,
        date_from=None,
        date_to=None,
        is_archived: Optional[bool] = None,
    ) -> int:
        """Count all sessions with admin filters."""
        query = {"is_deleted": False}

        if user_id:
            query["user_id"] = user_id
        if is_archived is not None:
            query["is_archived"] = is_archived
        if date_from:
            query["created_at"] = {"$gte": date_from}
        if date_to:
            if "created_at" in query:
                query["created_at"]["$lte"] = date_to
            else:
                query["created_at"] = {"$lte": date_to}

        return await self.sessions_collection.count_documents(query)

    async def archive_session(self, session_id: str) -> bool:
        """Archive a session."""
        result = await self.sessions_collection.update_one(
            {"_id": ObjectId(session_id)}, {"$set": {"is_archived": True}}
        )
        return result.modified_count > 0

    async def restore_session(self, session_id: str) -> bool:
        """Restore an archived session."""
        result = await self.sessions_collection.update_one(
            {"_id": ObjectId(session_id)}, {"$set": {"is_archived": False}}
        )
        return result.modified_count > 0

    async def hard_delete_session(self, session_id: str) -> bool:
        """Hard delete session and messages."""
        # Delete messages
        await self.messages_collection.delete_many({"session_id": session_id})
        # Delete session
        result = await self.sessions_collection.delete_one(
            {"_id": ObjectId(session_id)}
        )
        return result.deleted_count > 0

    async def find_by_user_id(
        self,
        user_id: str,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ChatSession]:
        """Alias for list_sessions_by_user for admin routes consistency."""
        return await self.list_sessions_by_user(
            user_id, skip=skip, limit=limit, include_archived=True
        )

    async def count_by_user_id(self, user_id: str) -> int:
        """Alias for count_sessions_by_user for admin routes consistency."""
        return await self.count_sessions_by_user(user_id, include_archived=True)

    async def find_recent(
        self,
        date_from=None,
        limit: int = 100,
    ) -> List[ChatSession]:
        """Find recent sessions."""
        query = {"is_deleted": False}
        if date_from:
            query["created_at"] = {"$gte": date_from}

        cursor = (
            self.sessions_collection.find(query).sort("updated_at", -1).limit(limit)
        )
        sessions = []

        async for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            session_model = ChatSessionInDB(**doc)
            sessions.append(ChatSessionMapper.to_entity(session_model))

        return sessions
