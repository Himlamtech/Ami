"""LLM generation configuration value object."""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class GenerationConfig:
    """
    Immutable configuration for LLM generation.

    Value object that encapsulates LLM generation parameters.
    """

    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: Optional[tuple] = None  # Use tuple for immutability

    def __post_init__(self):
        """Validate generation configuration."""
        if not 0.0 <= self.temperature <= 2.0:
            raise ValueError("temperature must be between 0.0 and 2.0")

        if self.max_tokens is not None and not 1 <= self.max_tokens <= 100000:
            raise ValueError("max_tokens must be between 1 and 100000")

        if not 0.0 <= self.top_p <= 1.0:
            raise ValueError("top_p must be between 0.0 and 1.0")

        if not -2.0 <= self.frequency_penalty <= 2.0:
            raise ValueError("frequency_penalty must be between -2.0 and 2.0")

        if not -2.0 <= self.presence_penalty <= 2.0:
            raise ValueError("presence_penalty must be between -2.0 and 2.0")

    def is_deterministic(self) -> bool:
        """Check if using deterministic generation (low temperature)."""
        return self.temperature < 0.3

    def is_creative(self) -> bool:
        """Check if using creative generation (high temperature)."""
        return self.temperature > 1.0

    @classmethod
    def deterministic(cls) -> "GenerationConfig":
        """Create deterministic config (low temperature)."""
        return cls(temperature=0.0, top_p=1.0)

    @classmethod
    def balanced(cls) -> "GenerationConfig":
        """Create balanced config."""
        return cls(temperature=0.7, top_p=1.0)

    @classmethod
    def creative(cls) -> "GenerationConfig":
        """Create creative config (high temperature)."""
        return cls(temperature=1.2, top_p=0.95)

    @classmethod
    def concise(cls, max_words: int = 100) -> "GenerationConfig":
        """Create concise config with token limit."""
        # Rough estimate: 1 word ≈ 1.3 tokens
        max_tokens = int(max_words * 1.3)
        return cls(temperature=0.5, max_tokens=max_tokens)
