"""LLM provider implementations.

Available providers:
- OpenAILLMService: OpenAI GPT models
- AnthropicLLMService: Claude models
- GeminiLLMService: Google Gemini models
"""


def __getattr__(name):
    """Lazy import to avoid missing optional dependencies."""
    if name == "OpenAILLMService":
        from .openai_llm import OpenAILLMService

        return OpenAILLMService
    elif name == "AnthropicLLMService":
        from .anthropic_llm import AnthropicLLMService

        return AnthropicLLMService
    elif name == "GeminiLLMService":
        from .gemini_llm import GeminiLLMService

        return GeminiLLMService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "OpenAILLMService",
    "AnthropicLLMService",
    "GeminiLLMService",
]
