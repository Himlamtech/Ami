"""
MongoDB client for async operations.
Handles connection pooling and database operations for document and user management.
"""

import logging
from typing import Any, Dict, List, Optional

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, DuplicateKeyError

logger = logging.getLogger(__name__)


class MongoDBClient:
    """
    Async MongoDB client using Motor.
    Manages connection to MongoDB for document metadata and user management.
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 27017,
        user: str = "admin",
        password: str = "admin_password",
        database: str = "ami_db",
    ):
        """
        Initialize MongoDB client.

        Args:
            host: MongoDB host
            port: MongoDB port
            user: MongoDB username
            password: MongoDB password
            database: Database name
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database_name = database
        
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        
        logger.info(f"Initialized MongoDBClient (host={host}, port={port}, db={database})")

    async def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            # Build connection URL
            connection_url = f"mongodb://{self.user}:{self.password}@{self.host}:{self.port}"
            
            # Create Motor client
            self.client = AsyncIOMotorClient(
                connection_url,
                serverSelectionTimeoutMS=5000,
            )
            
            # Get database
            self.db = self.client[self.database_name]
            
            # Test connection
            await self.client.admin.command('ping')
            
            # Create indexes
            await self._create_indexes()
            
            logger.info(f"✓ Connected to MongoDB: {self.database_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise RuntimeError(f"MongoDB connection failed: {str(e)}")

    async def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("✓ MongoDB connection closed")

    async def _create_indexes(self) -> None:
        """Create necessary indexes for collections."""
        try:
            # Users collection indexes
            await self.db.users.create_index("username", unique=True)
            await self.db.users.create_index("email", unique=True)
            
            # Documents collection indexes
            await self.db.documents.create_index("file_name")
            await self.db.documents.create_index("is_active")
            await self.db.documents.create_index("created_at")
            await self.db.documents.create_index([("title", "text")])
            
            # Vector mappings collection indexes
            await self.db.vector_mappings.create_index("document_id")
            await self.db.vector_mappings.create_index("qdrant_point_id", unique=True)
            
            logger.info("✓ MongoDB indexes created")
            
        except Exception as e:
            logger.warning(f"Index creation warning: {e}")

    # User Management
    
    async def create_user(self, user_data: Dict[str, Any]) -> str:
        """
        Create a new user.
        
        Args:
            user_data: User information (username, email, hashed_password, role, etc.)
            
        Returns:
            User ID (string)
            
        Raises:
            DuplicateKeyError: If username or email already exists
        """
        try:
            result = await self.db.users.insert_one(user_data)
            logger.info(f"Created user: {user_data.get('username')}")
            return str(result.inserted_id)
        except DuplicateKeyError as e:
            logger.error(f"Duplicate user: {e}")
            raise ValueError("Username or email already exists")

    async def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        user = await self.db.users.find_one({"username": username})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        user = await self.db.users.find_one({"email": email})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        from bson import ObjectId
        user = await self.db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            user["_id"] = str(user["_id"])
        return user

    async def list_users(
        self, skip: int = 0, limit: int = 50, is_active: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """
        List users with pagination.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            is_active: Filter by active status (None = all)
            
        Returns:
            List of user dictionaries
        """
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        
        cursor = self.db.users.find(query).skip(skip).limit(limit)
        users = await cursor.to_list(length=limit)
        
        for user in users:
            user["_id"] = str(user["_id"])
            # Remove sensitive data
            user.pop("hashed_password", None)
        
        return users

    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update user information.
        
        Args:
            user_id: User ID
            update_data: Fields to update
            
        Returns:
            True if updated successfully
        """
        from bson import ObjectId
        result = await self.db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete_user(self, user_id: str) -> bool:
        """
        Soft delete user (set is_active=False).
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted successfully
        """
        return await self.update_user(user_id, {"is_active": False})

    # Document Metadata Management
    
    async def create_document(self, doc_data: Dict[str, Any]) -> str:
        """
        Create document metadata.
        
        Args:
            doc_data: Document information (title, file_name, metadata, etc.)
            
        Returns:
            Document ID (string)
        """
        result = await self.db.documents.insert_one(doc_data)
        logger.info(f"Created document: {doc_data.get('title')}")
        return str(result.inserted_id)

    async def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Get document by ID."""
        from bson import ObjectId
        doc = await self.db.documents.find_one({"_id": ObjectId(doc_id)})
        if doc:
            doc["_id"] = str(doc["_id"])
        return doc

    async def list_documents(
        self,
        skip: int = 0,
        limit: int = 50,
        is_active: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        List documents with pagination and filters.
        
        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            is_active: Filter by active status (None = all)
            search: Text search query
            
        Returns:
            List of document dictionaries
        """
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        if search:
            query["$text"] = {"$search": search}
        
        cursor = self.db.documents.find(query).skip(skip).limit(limit).sort("created_at", -1)
        docs = await cursor.to_list(length=limit)
        
        for doc in docs:
            doc["_id"] = str(doc["_id"])
        
        return docs

    async def count_documents(self, is_active: Optional[bool] = None) -> int:
        """Count documents."""
        query = {}
        if is_active is not None:
            query["is_active"] = is_active
        return await self.db.documents.count_documents(query)

    async def update_document(self, doc_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update document metadata.
        
        Args:
            doc_id: Document ID
            update_data: Fields to update
            
        Returns:
            True if updated successfully
        """
        from bson import ObjectId
        result = await self.db.documents.update_one(
            {"_id": ObjectId(doc_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0

    async def soft_delete_document(self, doc_id: str) -> bool:
        """
        Soft delete document (set is_active=False).
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if deleted successfully
        """
        return await self.update_document(doc_id, {"is_active": False})

    async def restore_document(self, doc_id: str) -> bool:
        """
        Restore soft-deleted document.
        
        Args:
            doc_id: Document ID
            
        Returns:
            True if restored successfully
        """
        return await self.update_document(doc_id, {"is_active": True})

    # Vector Mapping Management
    
    async def create_vector_mapping(
        self,
        document_id: str,
        qdrant_point_id: str,
        chunk_index: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create mapping between MongoDB document and Qdrant point.
        
        Args:
            document_id: MongoDB document ID
            qdrant_point_id: Qdrant point UUID
            chunk_index: Index of chunk
            metadata: Additional metadata
            
        Returns:
            Mapping ID (string)
        """
        mapping = {
            "document_id": document_id,
            "qdrant_point_id": qdrant_point_id,
            "chunk_index": chunk_index,
            "metadata": metadata or {},
        }
        result = await self.db.vector_mappings.insert_one(mapping)
        return str(result.inserted_id)

    async def get_mappings_by_document(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all vector mappings for a document."""
        cursor = self.db.vector_mappings.find({"document_id": document_id})
        mappings = await cursor.to_list(length=1000)
        
        for mapping in mappings:
            mapping["_id"] = str(mapping["_id"])
        
        return mappings

    async def delete_mappings_by_document(self, document_id: str) -> int:
        """Delete all vector mappings for a document."""
        result = await self.db.vector_mappings.delete_many({"document_id": document_id})
        return result.deleted_count

    async def health_check(self) -> bool:
        """Check MongoDB health."""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False

