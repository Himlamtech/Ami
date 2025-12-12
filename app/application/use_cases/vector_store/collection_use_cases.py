"""Collection management use cases."""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from app.application.interfaces.services.vector_store_service import IVectorStoreService


# ===== List Collections =====
@dataclass
class ListCollectionsOutput:
    collections: List[str]


class ListCollectionsUseCase:
    """List all collections."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self) -> ListCollectionsOutput:
        collections = self.vector_store.list_collections()
        return ListCollectionsOutput(collections=collections)


# ===== Create Collection =====
@dataclass
class CreateCollectionInput:
    name: str
    vector_size: Optional[int] = None


@dataclass
class CreateCollectionOutput:
    success: bool
    name: str
    message: str


class CreateCollectionUseCase:
    """Create a new collection."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self, input_data: CreateCollectionInput) -> CreateCollectionOutput:
        # Check if already exists
        if self.vector_store.collection_exists(input_data.name):
            return CreateCollectionOutput(
                success=False,
                name=input_data.name,
                message=f"Collection '{input_data.name}' already exists",
            )

        success = self.vector_store.create_collection(
            collection_name=input_data.name, vector_size=input_data.vector_size
        )

        return CreateCollectionOutput(
            success=success,
            name=input_data.name,
            message=(
                "Collection created successfully"
                if success
                else "Failed to create collection"
            ),
        )


# ===== Delete Collection =====
@dataclass
class DeleteCollectionInput:
    name: str


@dataclass
class DeleteCollectionOutput:
    success: bool
    name: str
    message: str


class DeleteCollectionUseCase:
    """Delete a collection."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self, input_data: DeleteCollectionInput) -> DeleteCollectionOutput:
        # Check if exists
        if not self.vector_store.collection_exists(input_data.name):
            return DeleteCollectionOutput(
                success=False,
                name=input_data.name,
                message=f"Collection '{input_data.name}' not found",
            )

        success = self.vector_store.delete_collection(input_data.name)

        return DeleteCollectionOutput(
            success=success,
            name=input_data.name,
            message=(
                "Collection deleted successfully"
                if success
                else "Failed to delete collection"
            ),
        )


# ===== Get Collection Info =====
@dataclass
class GetCollectionInfoInput:
    name: str


@dataclass
class GetCollectionInfoOutput:
    name: str
    exists: bool
    info: Optional[Dict[str, Any]]


class GetCollectionInfoUseCase:
    """Get collection information."""

    def __init__(self, vector_store: IVectorStoreService):
        self.vector_store = vector_store

    def execute(self, input_data: GetCollectionInfoInput) -> GetCollectionInfoOutput:
        if not self.vector_store.collection_exists(input_data.name):
            return GetCollectionInfoOutput(
                name=input_data.name, exists=False, info=None
            )

        info = self.vector_store.get_collection_info(input_data.name)

        return GetCollectionInfoOutput(name=input_data.name, exists=True, info=info)
