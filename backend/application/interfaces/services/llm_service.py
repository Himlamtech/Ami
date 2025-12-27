"""LLM service interface."""

from abc import ABC, abstractmethod
from typing import Optional, AsyncIterator, Union

from domain.enums.llm_mode import LLMMode


class ILLMService(ABC):
    """
    Interface for Large Language Model providers.

    Simple interface: generate, stream_generate, and image_qa with mode support.
    """

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs,
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
        **kwargs,
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

    async def image_qa(
        self,
        prompt: str,
        image: Union[bytes, str],
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> str:
        """
        Answer questions about an image (Vision/Multimodal).

        Args:
            prompt: Question about the image
            image: Image as bytes or base64 string or URL
            mode: QA or REASONING (default: QA)
            **kwargs: Additional generation parameters

        Returns:
            Answer about the image

        Raises:
            NotImplementedError: If provider doesn't support vision
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support image QA"
        )
