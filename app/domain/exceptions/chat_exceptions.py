"""Chat domain exceptions."""


class ChatDomainException(Exception):
    """Base exception for chat domain errors."""
    pass


class ChatSessionNotFoundException(ChatDomainException):
    """Raised when chat session is not found."""
    
    def __init__(self, session_id: str = None):
        if session_id:
            message = f"Chat session '{session_id}' not found"
        else:
            message = "Chat session not found"
        super().__init__(message)
        self.session_id = session_id


class ChatMessageNotFoundException(ChatDomainException):
    """Raised when chat message is not found."""
    
    def __init__(self, message_id: str = None, session_id: str = None):
        if message_id and session_id:
            message = f"Message '{message_id}' not found in session '{session_id}'"
        elif message_id:
            message = f"Message '{message_id}' not found"
        else:
            message = "Message not found"
        super().__init__(message)
        self.message_id = message_id
        self.session_id = session_id


class InvalidChatSessionException(ChatDomainException):
    """Raised when chat session data is invalid."""
    
    def __init__(self, reason: str = "Invalid chat session"):
        super().__init__(reason)


class ChatSessionAccessDeniedException(ChatDomainException):
    """Raised when user doesn't have access to chat session."""
    
    def __init__(self, session_id: str = None, user_id: str = None):
        if session_id and user_id:
            message = f"User '{user_id}' does not have access to session '{session_id}'"
        else:
            message = "Access to chat session denied"
        super().__init__(message)
        self.session_id = session_id
        self.user_id = user_id


class ChatSessionDeletedException(ChatDomainException):
    """Raised when attempting to access a deleted chat session."""
    
    def __init__(self, session_id: str = None):
        if session_id:
            message = f"Chat session '{session_id}' has been deleted"
        else:
            message = "Chat session has been deleted"
        super().__init__(message)
        self.session_id = session_id
