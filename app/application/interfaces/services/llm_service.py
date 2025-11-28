"""LLM service interface."""

from abc import ABC, abstractmethod
from typing import Optional


class ILLMService(ABC):
    """
    Interface for Large Language Model providers.
    
    Renamed from ILLMProvider for consistency.
    """
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Generate text completion.
        
        Args:
            prompt: User prompt/question
            context: Optional context (RAG results, conversation history, etc.)
            **kwargs: Additional generation parameters (temperature, max_tokens, etc.)
            
        Returns:
            Generated text
        """
        pass
    
    @abstractmethod
    async def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ):
        """
        Stream text generation (async generator).
        
        Args:
            prompt: User prompt/question
            context: Optional context
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks as they're generated
        """
        pass
