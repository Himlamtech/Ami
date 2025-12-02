"""Admin Vector Store routes - Full management API."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, Dict, Any, List

from app.api.dependencies.auth import verify_admin_api_key
from app.infrastructure.factory import get_factory

# Use cases imports
from app.application.use_cases.vector_store import (
    # Health
    HealthCheckUseCase,
    # Collections
    ListCollectionsUseCase,
    CreateCollectionUseCase,
    DeleteCollectionUseCase,
    GetCollectionInfoUseCase,
    CreateCollectionInput,
    DeleteCollectionInput,
    GetCollectionInfoInput,
    # Documents
    ScrollDocumentsUseCase,
    GetDocumentUseCase,
    UpdateDocumentMetadataUseCase,
    DeleteDocumentsByFilterUseCase,
    ScrollDocumentsInput,
    GetDocumentInput,
    UpdateDocumentMetadataInput,
    DeleteDocumentsByFilterInput,
)

router = APIRouter(prefix="/admin/vectordb", tags=["admin-vector-database"])


# ===== Request/Response Schemas =====

class CreateCollectionRequest(BaseModel):
    name: str
    vector_size: Optional[int] = None


class UpdateMetadataRequest(BaseModel):
    metadata: Dict[str, Any]


class DeleteByFilterRequest(BaseModel):
    filter_conditions: Dict[str, Any]


class CollectionInfoResponse(BaseModel):
    name: str
    exists: bool
    info: Optional[Dict[str, Any]] = None


class ScrollResponse(BaseModel):
    documents: List[Dict[str, Any]]
    next_offset: Optional[str] = None
    total: int


class HealthResponse(BaseModel):
    healthy: bool
    message: str


# ===== Health Endpoint =====

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check vector store health."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        return HealthResponse(healthy=False, message="Vector store not configured")
    
    use_case = HealthCheckUseCase(vector_store)
    result = use_case.execute()
    
    return HealthResponse(healthy=result.healthy, message=result.message)


# ===== Collection Endpoints =====

@router.get("/collections", response_model=List[str])
async def list_collections(
    _: bool = Depends(verify_admin_api_key),
):
    """List all collections (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = ListCollectionsUseCase(vector_store)
    result = use_case.execute()
    
    return result.collections


@router.post("/collections")
async def create_collection(
    request: CreateCollectionRequest,
    _: bool = Depends(verify_admin_api_key),
):
    """Create a new collection (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = CreateCollectionUseCase(vector_store)
    result = use_case.execute(CreateCollectionInput(
        name=request.name,
        vector_size=request.vector_size
    ))
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return {"success": True, "name": result.name, "message": result.message}


@router.delete("/collections/{collection_name}")
async def delete_collection(
    collection_name: str,
    _: bool = Depends(verify_admin_api_key),
):
    """Delete a collection (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = DeleteCollectionUseCase(vector_store)
    result = use_case.execute(DeleteCollectionInput(name=collection_name))
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.message
        )
    
    return {"success": True, "name": result.name, "message": result.message}


@router.get("/collections/{collection_name}", response_model=CollectionInfoResponse)
async def get_collection_info(
    collection_name: str,
    _: bool = Depends(verify_admin_api_key),
):
    """Get collection information (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = GetCollectionInfoUseCase(vector_store)
    result = use_case.execute(GetCollectionInfoInput(name=collection_name))
    
    if not result.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Collection '{collection_name}' not found"
        )
    
    return CollectionInfoResponse(
        name=result.name,
        exists=result.exists,
        info=result.info
    )


# ===== Document Endpoints =====

@router.get("/collections/{collection_name}/documents", response_model=ScrollResponse)
async def scroll_documents(
    collection_name: str,
    limit: int = 20,
    offset: Optional[str] = None,
    with_vectors: bool = False,
    _: bool = Depends(verify_admin_api_key),
):
    """Scroll through documents in a collection (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = ScrollDocumentsUseCase(vector_store)
    result = use_case.execute(ScrollDocumentsInput(
        collection_name=collection_name,
        limit=limit,
        offset=offset,
        with_payload=True,
        with_vectors=with_vectors
    ))
    
    return ScrollResponse(
        documents=result.documents,
        next_offset=result.next_offset,
        total=result.total
    )


@router.get("/collections/{collection_name}/documents/{document_id}")
async def get_document(
    collection_name: str,
    document_id: str,
    _: bool = Depends(verify_admin_api_key),
):
    """Get a specific document by ID (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = GetDocumentUseCase(vector_store)
    result = use_case.execute(GetDocumentInput(
        document_id=document_id,
        collection_name=collection_name
    ))
    
    if not result.found:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{document_id}' not found in collection '{collection_name}'"
        )
    
    return result.document


@router.patch("/collections/{collection_name}/documents/{document_id}/metadata")
async def update_document_metadata(
    collection_name: str,
    document_id: str,
    request: UpdateMetadataRequest,
    _: bool = Depends(verify_admin_api_key),
):
    """Update document metadata (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = UpdateDocumentMetadataUseCase(vector_store)
    result = use_case.execute(UpdateDocumentMetadataInput(
        document_id=document_id,
        metadata=request.metadata,
        collection_name=collection_name
    ))
    
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND if "not found" in result.message.lower() else status.HTTP_400_BAD_REQUEST,
            detail=result.message
        )
    
    return {"success": True, "document_id": result.document_id, "message": result.message}


@router.post("/collections/{collection_name}/documents/delete-by-filter")
async def delete_documents_by_filter(
    collection_name: str,
    request: DeleteByFilterRequest,
    _: bool = Depends(verify_admin_api_key),
):
    """Delete documents matching filter (admin only)."""
    factory = get_factory()
    vector_store = factory.get_vector_store()
    
    if vector_store is None:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Vector store not available")
    
    use_case = DeleteDocumentsByFilterUseCase(vector_store)
    result = use_case.execute(DeleteDocumentsByFilterInput(
        filter_conditions=request.filter_conditions,
        collection_name=collection_name
    ))
    
    return {
        "success": result.success,
        "deleted_count": result.deleted_count,
        "message": result.message
    }
