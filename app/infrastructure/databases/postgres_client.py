"""
PostgreSQL database client with pgvector support.
Uses asyncpg for high-performance async operations.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional, Tuple

import asyncpg

logger = logging.getLogger(__name__)


class PostgresClient:
    """
    Async PostgreSQL client with connection pooling and pgvector support.
    Implements async context manager for automatic connection management.
    """

    def __init__(
        self,
        host: str,
        port: int,
        user: str,
        password: str,
        database: str,
        min_pool_size: int = 5,
        max_pool_size: int = 20,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.min_pool_size = min_pool_size
        self.max_pool_size = max_pool_size
        self._pool: Optional[asyncpg.Pool] = None

    async def connect(self) -> None:
        """Initialize connection pool."""
        try:
            self._pool = await asyncpg.create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60,
            )
            logger.info(
                f"PostgreSQL pool created: {self.database}@{self.host}:{self.port}"
            )

            # Verify pgvector extension
            await self.verify_pgvector()

        except Exception as e:
            logger.error(f"Failed to create PostgreSQL pool: {e}")
            raise

    async def disconnect(self) -> None:
        """Close connection pool."""
        if self._pool:
            await self._pool.close()
            logger.info("PostgreSQL pool closed")

    async def verify_pgvector(self) -> bool:
        """Verify pgvector extension is installed."""
        try:
            result = await self.fetch_one(
                "SELECT extname FROM pg_extension WHERE extname = 'vector'"
            )
            if result:
                logger.info("✓ pgvector extension verified")
                return True
            else:
                logger.warning("⚠ pgvector extension not found")
                return False
        except Exception as e:
            logger.error(f"Error verifying pgvector: {e}")
            return False

    @asynccontextmanager
    async def acquire(self):
        """Acquire a connection from the pool."""
        if not self._pool:
            raise RuntimeError("Connection pool not initialized. Call connect() first.")

        async with self._pool.acquire() as connection:
            yield connection

    async def execute(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> str:
        """
        Execute a query and return status.

        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds

        Returns:
            Query execution status
        """
        async with self.acquire() as conn:
            return await conn.execute(query, *args, timeout=timeout)

    async def fetch_one(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Fetch a single row as dictionary.

        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds

        Returns:
            Row as dictionary or None
        """
        async with self.acquire() as conn:
            row = await conn.fetchrow(query, *args, timeout=timeout)
            return dict(row) if row else None

    async def fetch_many(
        self, query: str, *args: Any, timeout: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch multiple rows as list of dictionaries.

        Args:
            query: SQL query
            *args: Query parameters
            timeout: Query timeout in seconds

        Returns:
            List of rows as dictionaries
        """
        async with self.acquire() as conn:
            rows = await conn.fetch(query, *args, timeout=timeout)
            return [dict(row) for row in rows]

    async def fetch_val(
        self, query: str, *args: Any, column: int = 0, timeout: Optional[float] = None
    ) -> Any:
        """
        Fetch a single value from a query.

        Args:
            query: SQL query
            *args: Query parameters
            column: Column index to return
            timeout: Query timeout in seconds

        Returns:
            Single value
        """
        async with self.acquire() as conn:
            return await conn.fetchval(query, *args, column=column, timeout=timeout)

    async def execute_many(
        self, query: str, args_list: List[Tuple], timeout: Optional[float] = None
    ) -> None:
        """
        Execute a query with multiple parameter sets.

        Args:
            query: SQL query
            args_list: List of parameter tuples
            timeout: Query timeout in seconds
        """
        async with self.acquire() as conn:
            await conn.executemany(query, args_list, timeout=timeout)

    async def transaction(self):
        """Get a transaction context."""
        if not self._pool:
            raise RuntimeError("Connection pool not initialized")

        conn = await self._pool.acquire()
        try:
            async with conn.transaction():
                yield conn
        finally:
            await self._pool.release(conn)

    # Vector-specific methods

    async def search_similar_vectors(
        self,
        embedding: List[float],
        table: str = "embeddings",
        limit: int = 5,
        threshold: float = 0.7,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search for similar vectors using cosine similarity.

        Args:
            embedding: Query embedding vector
            table: Table name containing embeddings
            limit: Maximum number of results
            threshold: Minimum similarity threshold
            filters: Additional WHERE clause filters

        Returns:
            List of similar items with scores
        """
        # Convert embedding to pgvector format
        embedding_str = f"[{','.join(map(str, embedding))}]"

        where_clause = ""
        params = [embedding_str, limit]

        if filters:
            conditions = []
            for i, (key, value) in enumerate(filters.items(), start=3):
                conditions.append(f"{key} = ${i}")
                params.append(value)
            if conditions:
                where_clause = "AND " + " AND ".join(conditions)

        query = f"""
            SELECT 
                e.*,
                c.content,
                c.metadata as chunk_metadata,
                d.title,
                d.file_name,
                1 - (e.embedding <=> $1::vector) as similarity_score
            FROM {table} e
            JOIN chunks c ON e.chunk_id = c.id
            JOIN documents d ON c.document_id = d.id
            WHERE 1 - (e.embedding <=> $1::vector) >= {threshold}
            {where_clause}
            ORDER BY e.embedding <=> $1::vector
            LIMIT $2
        """

        return await self.fetch_many(query, *params)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
