"""Vector Store Use Cases - Admin operations."""

from .collection_use_cases import (
    ListCollectionsUseCase,
    ListCollectionsOutput,
    CreateCollectionUseCase,
    CreateCollectionInput,
    CreateCollectionOutput,
    DeleteCollectionUseCase,
    DeleteCollectionInput,
    DeleteCollectionOutput,
    GetCollectionInfoUseCase,
    GetCollectionInfoInput,
    GetCollectionInfoOutput,
)

from .document_use_cases import (
    ScrollDocumentsUseCase,
    ScrollDocumentsInput,
    ScrollDocumentsOutput,
    GetDocumentUseCase,
    GetDocumentInput,
    GetDocumentOutput,
    UpdateDocumentMetadataUseCase,
    UpdateDocumentMetadataInput,
    UpdateDocumentMetadataOutput,
    DeleteDocumentsByFilterUseCase,
    DeleteDocumentsByFilterInput,
    DeleteDocumentsByFilterOutput,
)

from .health_use_case import HealthCheckUseCase, HealthCheckOutput

__all__ = [
    # Health
    "HealthCheckUseCase",
    "HealthCheckOutput",
    # Collection
    "ListCollectionsUseCase",
    "ListCollectionsOutput",
    "CreateCollectionUseCase",
    "CreateCollectionInput",
    "CreateCollectionOutput",
    "DeleteCollectionUseCase",
    "DeleteCollectionInput",
    "DeleteCollectionOutput",
    "GetCollectionInfoUseCase",
    "GetCollectionInfoInput",
    "GetCollectionInfoOutput",
    # Document
    "ScrollDocumentsUseCase",
    "ScrollDocumentsInput",
    "ScrollDocumentsOutput",
    "GetDocumentUseCase",
    "GetDocumentInput",
    "GetDocumentOutput",
    "UpdateDocumentMetadataUseCase",
    "UpdateDocumentMetadataInput",
    "UpdateDocumentMetadataOutput",
    "DeleteDocumentsByFilterUseCase",
    "DeleteDocumentsByFilterInput",
    "DeleteDocumentsByFilterOutput",
]
