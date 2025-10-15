"""
Anthropic Claude LLM provider implementation.
Uses Anthropic's Claude models via their official SDK.
"""

import logging
from typing import Any, Dict, Optional

from anthropic import AsyncAnthropic

from app.config.settings import settings
from app.core.interfaces import ILLMProvider

logger = logging.getLogger(__name__)


class AnthropicLLM(ILLMProvider):
    """Anthropic Claude LLM provider with async support."""

    def __init__(
        self,
        api_key: str,
        model: str = settings.anthropic_model,
        max_tokens: int = 4096,
    ):
        self.client = AsyncAnthropic(api_key=api_key)
        self.model = model
        self.default_max_tokens = max_tokens
        logger.info(f"Initialized AnthropicLLM with model: {model}")

    async def generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """
        Generate text completion using Claude.

        Args:
            prompt: User prompt/question
            context: Optional context to include as system message
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response
        """
        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Handle context as system message
            system_message = None
            if context:
                system_message = f"Use the following context to answer:\n\n{context}"

            # Prepare kwargs
            max_tokens = kwargs.pop("max_tokens", self.default_max_tokens)
            temperature = kwargs.pop("temperature", 0.7)
            top_p = kwargs.pop("top_p", 1.0)

            # Stop sequences (Anthropic uses stop_sequences)
            stop_sequences = kwargs.pop("stop", None) or kwargs.pop(
                "stop_sequences", None
            )

            # Create message
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }

            if system_message:
                request_params["system"] = system_message

            if stop_sequences:
                request_params["stop_sequences"] = stop_sequences

            response = await self.client.messages.create(**request_params)

            # Extract text from response
            if response.content and len(response.content) > 0:
                result = response.content[0].text
                logger.debug(f"Generated response length: {len(result)} chars")
                return result

            logger.warning("Empty response from Anthropic API")
            return ""

        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise RuntimeError(f"Failed to generate with Anthropic: {str(e)}")

    async def stream_generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ):
        """
        Stream text completion from Claude.

        Args:
            prompt: User prompt/question
            context: Optional context to include as system message
            **kwargs: Additional parameters

        Yields:
            Text chunks as they arrive
        """
        try:
            # Build messages
            messages = [{"role": "user", "content": prompt}]

            # Handle context
            system_message = None
            if context:
                system_message = f"Use the following context to answer:\n\n{context}"

            # Prepare kwargs
            max_tokens = kwargs.pop("max_tokens", self.default_max_tokens)
            temperature = kwargs.pop("temperature", 0.7)
            top_p = kwargs.pop("top_p", 1.0)

            stop_sequences = kwargs.pop("stop", None) or kwargs.pop(
                "stop_sequences", None
            )

            # Create streaming message
            request_params = {
                "model": self.model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
            }

            if system_message:
                request_params["system"] = system_message

            if stop_sequences:
                request_params["stop_sequences"] = stop_sequences

            async with self.client.messages.stream(**request_params) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise RuntimeError(f"Failed to stream with Anthropic: {str(e)}")
