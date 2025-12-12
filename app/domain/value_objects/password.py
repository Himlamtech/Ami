"""Password value object with validation rules."""

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    """
    Immutable password value object with validation rules.

    Enforces password strength requirements:
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character (optional, configurable)
    """

    value: str
    require_special_char: bool = False

    def __post_init__(self):
        """Validate password strength."""
        errors = self._validate()
        if errors:
            raise ValueError(f"Password validation failed: {', '.join(errors)}")

    def _validate(self) -> list:
        """Validate password and return list of errors."""
        errors = []

        if len(self.value) < 8:
            errors.append("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", self.value):
            errors.append("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", self.value):
            errors.append("Password must contain at least one lowercase letter")

        if not re.search(r"\d", self.value):
            errors.append("Password must contain at least one digit")

        if self.require_special_char and not re.search(
            r'[!@#$%^&*(),.?":{}|<>]', self.value
        ):
            errors.append("Password must contain at least one special character")

        return errors

    def get_strength(self) -> str:
        """
        Calculate password strength.

        Returns: 'weak', 'medium', 'strong', or 'very_strong'
        """
        score = 0

        # Length score
        if len(self.value) >= 12:
            score += 2
        elif len(self.value) >= 10:
            score += 1

        # Character variety
        if re.search(r"[A-Z]", self.value):
            score += 1
        if re.search(r"[a-z]", self.value):
            score += 1
        if re.search(r"\d", self.value):
            score += 1
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', self.value):
            score += 1

        # Multiple occurrences
        if len(re.findall(r"\d", self.value)) >= 2:
            score += 1
        if len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', self.value)) >= 2:
            score += 1

        # Classify strength
        if score >= 7:
            return "very_strong"
        elif score >= 5:
            return "strong"
        elif score >= 3:
            return "medium"
        else:
            return "weak"

    def is_strong(self) -> bool:
        """Check if password is strong or very strong."""
        return self.get_strength() in ("strong", "very_strong")

    def __str__(self) -> str:
        """Return masked password."""
        return "********"

    def __repr__(self) -> str:
        return "Password(********)"
