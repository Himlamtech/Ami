"""
OpenAI LLM provider implementation.
Uses OpenAI's chat completion API with error handling and retry logic.
"""

import logging
from typing import Optional

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.config.settings import settings
from app.core.interfaces import ILLMProvider

logger = logging.getLogger(__name__)


class OpenAILLM(ILLMProvider):
    """OpenAI LLM provider with enhanced error handling."""

    def __init__(self, api_key: str, model: str = "gpt-4-0125-preview"):
        self.client = AsyncOpenAI(api_key=api_key, max_retries=3, timeout=60.0)
        self.model = model
        logger.info(f"Initialized OpenAILLM with model: {model}")

    async def generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate completion with error handling."""
        try:
            messages = []
            if context:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Use the following context to answer:\n{context}",
                    }
                )
            messages.append({"role": "user", "content": prompt})

            response = await self.client.chat.completions.create(
                model=self.model, messages=messages, **kwargs
            )

            result = response.choices[0].message.content
            logger.debug(
                f"Generated response: {len(result)} chars, usage: {response.usage}"
            )
            return result

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit exceeded: {e}")
            raise RuntimeError("Rate limit exceeded. Please try again later.")
        except APITimeoutError as e:
            logger.error(f"OpenAI API timeout: {e}")
            raise RuntimeError("Request timeout. Please try again.")
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in OpenAI generate: {e}")
            raise RuntimeError(f"Failed to generate: {str(e)}")

    async def stream_generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ):
        """Stream completion with error handling."""
        try:
            messages = []
            if context:
                messages.append(
                    {
                        "role": "system",
                        "content": f"Use the following context to answer:\n{context}",
                    }
                )
            messages.append({"role": "user", "content": prompt})

            stream = await self.client.chat.completions.create(
                model=self.model, messages=messages, stream=True, **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except RateLimitError as e:
            logger.error(f"OpenAI rate limit in stream: {e}")
            yield f"[ERROR: Rate limit exceeded]"
        except APITimeoutError as e:
            logger.error(f"OpenAI timeout in stream: {e}")
            yield f"[ERROR: Request timeout]"
        except Exception as e:
            logger.error(f"Error in OpenAI stream: {e}")
            yield f"[ERROR: {str(e)}]"
