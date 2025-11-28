"""Email value object with validation."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """
    Immutable email value object with validation.
    
    Ensures email addresses are valid according to basic RFC 5322 rules.
    """
    
    value: str
    
    def __post_init__(self):
        """Validate email format."""
        if not self._is_valid_email(self.value):
            raise ValueError(f"Invalid email address: {self.value}")
    
    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """
        Validate email using regex pattern.
        
        Basic validation - checks for:
        - Local part: alphanumeric, dots, underscores, hyphens
        - @ symbol
        - Domain: alphanumeric with dots
        - TLD: at least 2 characters
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def get_domain(self) -> str:
        """Extract domain from email."""
        return self.value.split('@')[1]
    
    def get_local_part(self) -> str:
        """Extract local part (before @) from email."""
        return self.value.split('@')[0]
    
    def is_from_domain(self, domain: str) -> bool:
        """Check if email is from specific domain."""
        return self.get_domain().lower() == domain.lower()
    
    def __str__(self) -> str:
        return self.value
    
    def __repr__(self) -> str:
        return f"Email('{self.value}')"
