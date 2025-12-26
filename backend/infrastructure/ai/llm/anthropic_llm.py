"""
Anthropic Claude LLM provider - Simple implementation.
Config from centralized config module.
Supports Vision (Claude 3) for image QA.
"""

import base64
import logging
from typing import Optional, AsyncIterator, Union

from anthropic import (
    AsyncAnthropic,
    APIError,
    APITimeoutError,
    RateLimitError,
)

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config import anthropic_config
from app.config.ai import AnthropicConfig

logger = logging.getLogger(__name__)


class AnthropicLLMService(ILLMService):
    """Anthropic Claude LLM provider - wraps Anthropic API."""

    def __init__(
        self, config: AnthropicConfig = None, default_mode: LLMMode = LLMMode.QA
    ):
        """
        Initialize Anthropic LLM service.

        Args:
            config: Anthropic configuration. If None, uses global anthropic_config.
            default_mode: Default LLM mode (QA or REASONING).
        """
        self.config = config or anthropic_config
        self.client = AsyncAnthropic(
            api_key=self.config.api_key,
            max_retries=self.config.max_retries,
            timeout=self.config.timeout,
        )
        self._models = {
            LLMMode.QA: self.config.model_qa,
            LLMMode.REASONING: self.config.model_reasoning,
        }
        self._current_mode = default_mode
        logger.info(
            f"Anthropic initialized - QA: {self.config.model_qa}, "
            f"Reasoning: {self.config.model_reasoning}"
        )

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> str:
        """Generate completion."""
        model = self._models[mode or self._current_mode]

        try:
            messages = [{"role": "user", "content": prompt}]

            system = None
            if context:
                system = fcontext

            max_tokens = kwargs.pop("max_tokens", 4096)
            temperature = kwargs.pop("temperature", 0.7)

            logger.debug(f"Generating with {model}")

            response = await self.client.messages.create(
                model=model,
                messages=messages,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            result = response.content[0].text
            logger.debug(f"Generated: {len(result)} chars")
            return result

        except RateLimitError as e:
            logger.error(f"Rate limit: {e}")
            raise RuntimeError("Rate limit exceeded.")
        except APITimeoutError as e:
            logger.error(f"Timeout: {e}")
            raise RuntimeError("Request timeout.")
        except APIError as e:
            logger.error(f"API error: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise RuntimeError(f"Failed: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> AsyncIterator[str]:
        """Stream completion."""
        model = self._models[mode or self._current_mode]

        try:
            messages = [{"role": "user", "content": prompt}]

            system = None
            if context:
                system = fcontext

            max_tokens = kwargs.pop("max_tokens", 4096)
            temperature = kwargs.pop("temperature", 0.7)

            logger.debug(f"Streaming with {model}")

            async with self.client.messages.stream(
                model=model,
                messages=messages,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
            ) as stream:
                async for text in stream.text_stream:
                    yield text

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"[ERROR: {str(e)}]"

    async def image_qa(
        self,
        prompt: str,
        image: Union[bytes, str],
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> str:
        """
        Answer questions about an image using Claude Vision.

        Args:
            prompt: Question about the image
            image: Image as bytes, base64 string, or URL
            mode: QA or REASONING (default: QA)
            **kwargs: Additional generation parameters

        Returns:
            Answer about the image
        """
        model = self._models[mode or self._current_mode]

        try:
            # Prepare image for Anthropic format
            mime_type = kwargs.pop("mime_type", "image/jpeg")

            if isinstance(image, bytes):
                # Raw bytes - encode to base64
                image_b64 = base64.b64encode(image).decode("utf-8")
            elif isinstance(image, str):
                if image.startswith(("http://", "https://")):
                    # URL - Claude doesn't support URL directly, need to fetch
                    # For now, raise error - should be handled at higher level
                    raise ValueError(
                        "Anthropic doesn't support image URLs directly. Please provide bytes or base64."
                    )
                else:
                    # Assume base64 string
                    image_b64 = image
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")

            # Build message with image (Claude format)
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": mime_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            max_tokens = kwargs.pop("max_tokens", 4096)
            temperature = kwargs.pop("temperature", 0.7)

            logger.debug(f"Image QA with {model}")

            response = await self.client.messages.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            result = response.content[0].text
            logger.debug(f"Image QA response: {len(result)} chars")
            return result

        except RateLimitError as e:
            logger.error(f"Rate limit in image_qa: {e}")
            raise RuntimeError("Rate limit exceeded.")
        except APITimeoutError as e:
            logger.error(f"Timeout in image_qa: {e}")
            raise RuntimeError("Request timeout.")
        except APIError as e:
            logger.error(f"API error in image_qa: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in image_qa: {e}")
            raise RuntimeError(f"Failed to process image: {str(e)}")
