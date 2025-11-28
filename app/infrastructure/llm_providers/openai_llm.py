"""OpenAI LLM Provider - Wrapper for existing implementation."""

# Import existing OpenAI provider
try:
    from app.infrastructure.llms.openai_llm import OpenAILLM as _OpenAILLMImpl
    OpenAILLM = _OpenAILLMImpl
except ImportError:
    # Fallback: define placeholder
    class OpenAILLM:
        """OpenAI LLM placeholder."""
        def __init__(self, *args, **kwargs):
            raise NotImplementedError("OpenAI LLM not available. Install dependencies or check import path.")

__all__ = ["OpenAILLM"]
