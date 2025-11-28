"""Password hashing utilities."""

from passlib.context import CryptContext


class PasswordHasher:
    """
    Password hashing and verification using bcrypt.
    
    Provides secure password hashing for user authentication.
    """
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def hash(self, password: str) -> str:
        """
        Hash a plain password.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        return self.pwd_context.hash(password)
    
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password
            hashed_password: Hashed password from database
            
        Returns:
            True if password matches, False otherwise
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def needs_update(self, hashed_password: str) -> bool:
        """
        Check if password hash needs update (deprecated algorithm).
        
        Args:
            hashed_password: Current hashed password
            
        Returns:
            True if hash should be updated
        """
        return self.pwd_context.needs_update(hashed_password)
