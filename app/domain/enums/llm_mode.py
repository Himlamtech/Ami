"""LLM Mode enumeration."""

from enum import Enum


class LLMMode(str, Enum):
    """
    LLM operation modes.
    
    - QA: Quick Question-Answering mode (fast, lightweight models)
    - REASONING: Deep reasoning mode (powerful, thinking models)
    """
    
    QA = "qa"  # Hỏi Đáp - Quick responses
    REASONING = "reasoning"  # Suy Luận - Deep thinking
    
    @classmethod
    def from_string(cls, value: str) -> "LLMMode":
        """Convert string to LLMMode."""
        value = value.lower().strip()
        if value in ("qa", "hoi_dap", "hoidap", "question", "fast"):
            return cls.QA
        elif value in ("reasoning", "suy_luan", "suyluan", "thinking", "deep"):
            return cls.REASONING
        else:
            # Default to QA for unknown values
            return cls.QA


class LLMProvider(str, Enum):
    """
    Supported LLM providers.
    """
    
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    
    @classmethod
    def from_string(cls, value: str) -> "LLMProvider":
        """Convert string to LLMProvider."""
        value = value.lower().strip()
        if value in ("openai", "gpt"):
            return cls.OPENAI
        elif value in ("gemini", "google"):
            return cls.GEMINI
        elif value in ("anthropic", "claude"):
            return cls.ANTHROPIC
        else:
            return cls.OPENAI  # Default
