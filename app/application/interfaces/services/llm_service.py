"""LLM service interface."""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator

from app.domain.enums.llm_mode import LLMMode


class ILLMService(ABC):
    """
    Interface for Large Language Model providers.
    
    Simple interface: generate and stream_generate with mode support.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt/question
            context: Optional context (RAG results, conversation history, etc.)
            mode: QA or REASONING (default: QA)
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Stream text generation (async generator).
        
        Args:
            prompt: User prompt/question
            context: Optional context
            mode: QA or REASONING (default: QA)
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks as they're generated
        """
        pass
