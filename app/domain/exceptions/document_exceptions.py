"""Document domain exceptions."""


class DocumentDomainException(Exception):
    """Base exception for document domain errors."""
    pass


class DocumentNotFoundException(DocumentDomainException):
    """Raised when document is not found."""
    
    def __init__(self, document_id: str = None, collection: str = None):
        if document_id and collection:
            message = f"Document '{document_id}' not found in collection '{collection}'"
        elif document_id:
            message = f"Document '{document_id}' not found"
        else:
            message = "Document not found"
        super().__init__(message)
        self.document_id = document_id
        self.collection = collection


class DocumentAlreadyExistsException(DocumentDomainException):
    """Raised when attempting to create a document that already exists."""
    
    def __init__(self, file_name: str = None, collection: str = None):
        if file_name and collection:
            message = f"Document '{file_name}' already exists in collection '{collection}'"
        elif file_name:
            message = f"Document '{file_name}' already exists"
        else:
            message = "Document already exists"
        super().__init__(message)
        self.file_name = file_name
        self.collection = collection


class InvalidDocumentException(DocumentDomainException):
    """Raised when document data is invalid."""
    
    def __init__(self, reason: str = "Invalid document"):
        super().__init__(reason)


class DocumentNotEmbeddedException(DocumentDomainException):
    """Raised when attempting to access embeddings for a document that hasn't been embedded."""
    
    def __init__(self, document_id: str = None):
        if document_id:
            message = f"Document '{document_id}' has not been embedded yet"
        else:
            message = "Document has not been embedded yet"
        super().__init__(message)
        self.document_id = document_id


class DocumentAccessDeniedException(DocumentDomainException):
    """Raised when user doesn't have access to document."""
    
    def __init__(self, document_id: str = None, user_id: str = None):
        if document_id and user_id:
            message = f"User '{user_id}' does not have access to document '{document_id}'"
        else:
            message = "Access to document denied"
        super().__init__(message)
        self.document_id = document_id
        self.user_id = user_id
