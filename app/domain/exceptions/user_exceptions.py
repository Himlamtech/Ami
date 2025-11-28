"""User domain exceptions."""


class UserDomainException(Exception):
    """Base exception for user domain errors."""
    pass


class UserNotFoundException(UserDomainException):
    """Raised when user is not found."""
    
    def __init__(self, user_id: str = None, username: str = None):
        if user_id:
            message = f"User with ID '{user_id}' not found"
        elif username:
            message = f"User with username '{username}' not found"
        else:
            message = "User not found"
        super().__init__(message)
        self.user_id = user_id
        self.username = username


class UserAlreadyExistsException(UserDomainException):
    """Raised when attempting to create a user that already exists."""
    
    def __init__(self, username: str = None, email: str = None):
        if username:
            message = f"User with username '{username}' already exists"
        elif email:
            message = f"User with email '{email}' already exists"
        else:
            message = "User already exists"
        super().__init__(message)
        self.username = username
        self.email = email


class InvalidCredentialsException(UserDomainException):
    """Raised when login credentials are invalid."""
    
    def __init__(self, message: str = "Invalid username or password"):
        super().__init__(message)


class UserNotActiveException(UserDomainException):
    """Raised when attempting to access an inactive user account."""
    
    def __init__(self, username: str = None):
        if username:
            message = f"User account '{username}' is not active"
        else:
            message = "User account is not active"
        super().__init__(message)
        self.username = username


class InsufficientPermissionsException(UserDomainException):
    """Raised when user lacks required permissions."""
    
    def __init__(self, resource: str = None, action: str = None):
        if resource and action:
            message = f"Insufficient permissions to {action} {resource}"
        elif resource:
            message = f"Insufficient permissions to access {resource}"
        else:
            message = "Insufficient permissions"
        super().__init__(message)
        self.resource = resource
        self.action = action
