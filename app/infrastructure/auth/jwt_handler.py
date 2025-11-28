"""JWT token handler."""

from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import jwt
from app.config.settings import settings


class JWTHandler:
    """
    JWT token creation and validation.
    
    Handles encoding/decoding JWT tokens for authentication.
    """
    
    def __init__(
        self,
        secret_key: str = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = None,
    ):
        self.secret_key = secret_key or settings.jwt_secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = (
            access_token_expire_minutes or settings.jwt_access_token_expire_minutes
        )
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
    ) -> str:
        """
        Create JWT access token.
        
        Args:
            data: Payload data (e.g., {"sub": username, "role_ids": [...]})
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "iat": datetime.utcnow()})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Dict[str, Any]:
        """
        Decode and validate JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded payload
            
        Raises:
            jwt.InvalidTokenError: If token is invalid or expired
        """
        payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        return payload
    
    def verify_token(self, token: str) -> bool:
        """
        Verify if token is valid.
        
        Args:
            token: JWT token
            
        Returns:
            True if valid, False otherwise
        """
        try:
            self.decode_token(token)
            return True
        except jwt.InvalidTokenError:
            return False
