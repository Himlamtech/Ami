"""Thinking mode value object."""

from enum import Enum


class ThinkingMode(str, Enum):
    """
    Thinking modes mapping to LLM models.
    
    - FAST: gpt-4-1106-preview (fastest, most cost-effective)
    - BALANCE: gpt-4-0125-preview (balanced speed & quality)
    - THINKING: o4-mini (deep reasoning, slowest but most accurate)
    """
    
    FAST = "fast"
    BALANCE = "balance"
    THINKING = "thinking"
    
    def get_model_name(self) -> str:
        """Get the corresponding OpenAI model name."""
        model_mapping = {
            ThinkingMode.FAST: "gpt-4-1106-preview",
            ThinkingMode.BALANCE: "gpt-4-0125-preview",
            ThinkingMode.THINKING: "o4-mini",
        }
        return model_mapping[self]
    
    def is_reasoning_model(self) -> bool:
        """Check if this is a reasoning model (o4-mini)."""
        return self == ThinkingMode.THINKING
    
    @classmethod
    def from_string(cls, mode: str) -> "ThinkingMode":
        """Create ThinkingMode from string, with fallback to BALANCE."""
        try:
            return cls(mode.lower())
        except ValueError:
            return cls.BALANCE
