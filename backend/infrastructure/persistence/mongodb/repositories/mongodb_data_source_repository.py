"""MongoDB Data Source Repository implementation."""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from domain.entities.data_source import DataSource, SourceAuth, CrawlConfig
from domain.enums.data_source import (
    SourceStatus,
    DataCategory,
    DataType,
    SourceType,
)
from application.interfaces.repositories.data_source_repository import (
    IDataSourceRepository,
)


class MongoDBDataSourceRepository(IDataSourceRepository):
    """MongoDB implementation of DataSource Repository."""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db["data_sources"]

    async def create(self, source: DataSource) -> DataSource:
        """Create new data source."""
        doc = self._entity_to_doc(source)
        result = await self.collection.insert_one(doc)
        source.id = str(result.inserted_id)
        return source

    async def get_by_id(self, source_id: str) -> Optional[DataSource]:
        """Get data source by ID."""
        try:
            doc = await self.collection.find_one({"_id": ObjectId(source_id)})
        except Exception:
            return None

        if not doc:
            return None

        return self._doc_to_entity(doc)

    async def update(self, source: DataSource) -> DataSource:
        """Update data source."""
        doc = self._entity_to_doc(source)
        doc.pop("_id", None)  # Remove _id from update

        await self.collection.update_one({"_id": ObjectId(source.id)}, {"$set": doc})

        return source

    async def delete(self, source_id: str) -> bool:
        """Delete data source."""
        result = await self.collection.delete_one({"_id": ObjectId(source_id)})
        return result.deleted_count > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[SourceStatus] = None,
        category: Optional[DataCategory] = None,
        is_active: Optional[bool] = None,
    ) -> List[DataSource]:
        """List data sources with filters."""
        query = self._build_query(status, category, is_active)

        cursor = self.collection.find(query).sort("priority", 1).skip(skip).limit(limit)
        sources = []

        async for doc in cursor:
            sources.append(self._doc_to_entity(doc))

        return sources

    async def count(
        self,
        status: Optional[SourceStatus] = None,
        category: Optional[DataCategory] = None,
        is_active: Optional[bool] = None,
    ) -> int:
        """Count data sources with filters."""
        query = self._build_query(status, category, is_active)
        return await self.collection.count_documents(query)

    async def get_active_sources(self) -> List[DataSource]:
        """Get all active data sources for scheduling."""
        query = {"is_active": True, "status": {"$ne": SourceStatus.DISABLED.value}}

        cursor = self.collection.find(query).sort("priority", 1)
        sources = []

        async for doc in cursor:
            sources.append(self._doc_to_entity(doc))

        return sources

    async def get_by_url(self, base_url: str) -> Optional[DataSource]:
        """Get data source by base URL."""
        doc = await self.collection.find_one({"base_url": base_url})

        if not doc:
            return None

        return self._doc_to_entity(doc)

    async def update_crawl_stats(
        self,
        source_id: str,
        success: bool,
        docs_count: int = 0,
        error: Optional[str] = None,
    ) -> bool:
        """Update crawl statistics after job completion."""
        now = datetime.now()

        if success:
            update = {
                "$set": {
                    "last_crawl_at": now,
                    "last_success_at": now,
                    "error_count": 0,
                    "error_message": None,
                    "status": SourceStatus.ACTIVE.value,
                    "updated_at": now,
                },
                "$inc": {
                    "total_crawls": 1,
                    "total_documents": docs_count,
                },
            }
        else:
            update = {
                "$set": {
                    "last_crawl_at": now,
                    "error_message": error,
                    "updated_at": now,
                },
                "$inc": {
                    "total_crawls": 1,
                    "error_count": 1,
                },
            }

        result = await self.collection.update_one({"_id": ObjectId(source_id)}, update)

        # Check if need to pause due to errors
        if not success:
            source = await self.get_by_id(source_id)
            if source and source.error_count >= source.max_errors:
                await self.collection.update_one(
                    {"_id": ObjectId(source_id)},
                    {"$set": {"status": SourceStatus.ERROR.value, "is_active": False}},
                )

        return result.modified_count > 0

    def _build_query(
        self,
        status: Optional[SourceStatus] = None,
        category: Optional[DataCategory] = None,
        is_active: Optional[bool] = None,
    ) -> dict:
        """Build MongoDB query from filters."""
        query = {}
        if status:
            query["status"] = status.value
        if category:
            query["category"] = category.value
        if is_active is not None:
            query["is_active"] = is_active
        return query

    def _entity_to_doc(self, source: DataSource) -> dict:
        """Convert entity to MongoDB document."""
        doc = {
            "name": source.name,
            "base_url": source.base_url,
            "source_type": source.source_type.value,
            "category": source.category.value,
            "data_type": source.data_type.value,
            "collection": source.collection,
            "schedule_cron": source.schedule_cron,
            "is_active": source.is_active,
            "priority": source.priority,
            "status": source.status.value,
            "error_message": source.error_message,
            "error_count": source.error_count,
            "max_errors": source.max_errors,
            "total_crawls": source.total_crawls,
            "total_documents": source.total_documents,
            "last_crawl_at": source.last_crawl_at,
            "last_success_at": source.last_success_at,
            "description": source.description,
            "tags": source.tags,
            "metadata": source.metadata,
            "created_by": source.created_by,
            "created_at": source.created_at,
            "updated_at": source.updated_at,
        }

        # Auth config
        if source.auth:
            doc["auth"] = {
                "auth_type": source.auth.auth_type,
                "username": source.auth.username,
                "password": source.auth.password,
                "token": source.auth.token,
                "cookies": source.auth.cookies,
                "headers": source.auth.headers,
            }
        else:
            doc["auth"] = None

        # Crawl config
        if source.crawl_config:
            doc["crawl_config"] = {
                "list_selector": source.crawl_config.list_selector,
                "detail_selector": source.crawl_config.detail_selector,
                "title_selector": source.crawl_config.title_selector,
                "date_selector": source.crawl_config.date_selector,
                "max_depth": source.crawl_config.max_depth,
                "max_pages": source.crawl_config.max_pages,
                "rate_limit": source.crawl_config.rate_limit,
                "timeout_seconds": source.crawl_config.timeout_seconds,
                "min_content_length": source.crawl_config.min_content_length,
                "exclude_patterns": source.crawl_config.exclude_patterns,
            }
        else:
            doc["crawl_config"] = None

        if source.id:
            doc["_id"] = ObjectId(source.id)

        return doc

    def _doc_to_entity(self, doc: dict) -> DataSource:
        """Convert MongoDB document to entity."""
        # Parse auth
        auth = None
        if doc.get("auth"):
            auth_doc = doc["auth"]
            auth = SourceAuth(
                auth_type=auth_doc.get("auth_type", "none"),
                username=auth_doc.get("username"),
                password=auth_doc.get("password"),
                token=auth_doc.get("token"),
                cookies=auth_doc.get("cookies"),
                headers=auth_doc.get("headers"),
            )

        # Parse crawl config
        crawl_config = CrawlConfig()
        if doc.get("crawl_config"):
            cc = doc["crawl_config"]
            crawl_config = CrawlConfig(
                list_selector=cc.get("list_selector"),
                detail_selector=cc.get("detail_selector"),
                title_selector=cc.get("title_selector"),
                date_selector=cc.get("date_selector"),
                max_depth=cc.get("max_depth", 2),
                max_pages=cc.get("max_pages", 50),
                rate_limit=cc.get("rate_limit", 10),
                timeout_seconds=cc.get("timeout_seconds", 30),
                min_content_length=cc.get("min_content_length", 100),
                exclude_patterns=cc.get("exclude_patterns", []),
            )

        return DataSource(
            id=str(doc["_id"]),
            name=doc["name"],
            base_url=doc["base_url"],
            source_type=SourceType(doc.get("source_type", "web_crawl")),
            category=DataCategory(doc.get("category", "general")),
            data_type=DataType(doc.get("data_type", "realtime")),
            collection=doc.get("collection", "default"),
            schedule_cron=doc.get("schedule_cron", "0 */6 * * *"),
            is_active=doc.get("is_active", True),
            priority=doc.get("priority", 5),
            auth=auth,
            crawl_config=crawl_config,
            status=SourceStatus(doc.get("status", "active")),
            error_message=doc.get("error_message"),
            error_count=doc.get("error_count", 0),
            max_errors=doc.get("max_errors", 5),
            total_crawls=doc.get("total_crawls", 0),
            total_documents=doc.get("total_documents", 0),
            last_crawl_at=doc.get("last_crawl_at"),
            last_success_at=doc.get("last_success_at"),
            description=doc.get("description"),
            tags=doc.get("tags", []),
            metadata=doc.get("metadata", {}),
            created_by=doc.get("created_by"),
            created_at=doc.get("created_at", datetime.now()),
            updated_at=doc.get("updated_at", datetime.now()),
        )
