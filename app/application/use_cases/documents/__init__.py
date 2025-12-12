"""Document use cases."""

from .upload_document import (
    UploadDocumentUseCase,
    UploadDocumentInput,
    UploadDocumentOutput,
)
from .delete_document import (
    DeleteDocumentUseCase,
    DeleteDocumentInput,
    DeleteDocumentOutput,
)
from .list_documents import (
    ListDocumentsUseCase,
    ListDocumentsInput,
    ListDocumentsOutput,
)

__all__ = [
    "UploadDocumentUseCase",
    "UploadDocumentInput",
    "UploadDocumentOutput",
    "DeleteDocumentUseCase",
    "DeleteDocumentInput",
    "DeleteDocumentOutput",
    "ListDocumentsUseCase",
    "ListDocumentsInput",
    "ListDocumentsOutput",
]
