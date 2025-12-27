"""
OpenAI LLM provider - Simple, config-driven implementation.
Supports Vision (GPT-4 Vision) for image QA.
"""

import base64
import logging
from typing import Optional, Union

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config import openai_config
from app.config.ai import OpenAIConfig

logger = logging.getLogger(__name__)


class OpenAILLMService(ILLMService):
    """OpenAI LLM provider - wraps OpenAI API."""

    def __init__(self, config: OpenAIConfig = None, default_mode: LLMMode = LLMMode.QA):
        """
        Initialize OpenAI LLM service.

        Args:
            config: OpenAI configuration. If None, uses global openai_config.
            default_mode: Default LLM mode (QA or REASONING).
        """
        self.config = config or openai_config
        self.client = AsyncOpenAI(
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
            f"OpenAI initialized - QA: {self.config.model_qa}, Reasoning: {self.config.model_reasoning}"
        )

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> str:
        """
        Generate completion.

        Note: Context formatting should be done in Application layer (Use Cases).
        This method accepts pre-formatted prompt or separate context.
        """
        model = self._models[mode or self._current_mode]

        try:
            # Build messages - simple passthrough
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            kwargs.setdefault("max_tokens", 4096)

            logger.debug(f"Generating with {model}")

            response = await self.client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )

            result = response.choices[0].message.content
            logger.debug(f"Generated {len(result)} chars")
            return result

        except RateLimitError as e:
            logger.error(f"Rate limit: {e}")
            raise RuntimeError("Rate limit exceeded")
        except APITimeoutError as e:
            logger.error(f"Timeout: {e}")
            raise RuntimeError("Request timeout")
        except APIError as e:
            logger.error(f"API error: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error: {e}")
            raise RuntimeError(f"Generation failed: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs,
    ):
        """Stream completion."""
        model = self._models[mode or self._current_mode]

        try:
            messages = []
            if context:
                messages.append({"role": "system", "content": context})
            messages.append({"role": "user", "content": prompt})

            kwargs.setdefault("max_tokens", 4096)

            logger.debug(f"Streaming with {model}")

            stream = await self.client.chat.completions.create(
                model=model, messages=messages, stream=True, **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

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
        Answer questions about an image using GPT-4 Vision.

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
            # Prepare image URL for OpenAI format
            if isinstance(image, bytes):
                # Raw bytes - encode to base64
                image_b64 = base64.b64encode(image).decode("utf-8")
                mime_type = kwargs.pop("mime_type", "image/jpeg")
                image_url = f"data:{mime_type};base64,{image_b64}"
            elif isinstance(image, str):
                if image.startswith(("http://", "https://")):
                    # Already a URL
                    image_url = image
                else:
                    # Assume base64 string
                    mime_type = kwargs.pop("mime_type", "image/jpeg")
                    image_url = f"data:{mime_type};base64,{image}"
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")

            # Build message with image
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": image_url}},
                        {"type": "text", "text": prompt},
                    ],
                }
            ]

            kwargs.setdefault("max_tokens", 4096)

            logger.debug(f"Image QA with {model}")

            response = await self.client.chat.completions.create(
                model=model, messages=messages, **kwargs
            )

            result = response.choices[0].message.content
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

    async def generate_image(
        self,
        prompt: str,
        size: str = "1024x1024",
        style: str = "natural",
        **kwargs,
    ) -> bytes:
        """
        Generate image using DALL-E.

        Args:
            prompt: Image description prompt
            size: Image size ("1024x1024", "1792x1024", "1024x1792")
            style: Image style ("natural" or "vivid")
            **kwargs: Additional generation parameters

        Returns:
            Image bytes (PNG format)
        """
        try:
            logger.debug(f"Generating image with DALL-E: {prompt[:50]}...")

            # Use DALL-E 3 for higher quality
            response = await self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="standard",
                style=style,
                n=1,
            )

            # Get image URL
            image_url = response.data[0].url
            
            # Download image bytes
            import httpx
            async with httpx.AsyncClient() as client:
                resp = await client.get(image_url)
                if resp.status_code != 200:
                    raise RuntimeError(f"Failed to download image: HTTP {resp.status_code}")
                image_bytes = resp.content
            
            logger.debug(f"Generated image: {len(image_bytes)} bytes")
            return image_bytes

        except RateLimitError as e:
            logger.error(f"Rate limit in generate_image: {e}")
            raise RuntimeError("Rate limit exceeded.")
        except APITimeoutError as e:
            logger.error(f"Timeout in generate_image: {e}")
            raise RuntimeError("Request timeout.")
        except APIError as e:
            logger.error(f"API error in generate_image: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Error in generate_image: {e}")
            raise RuntimeError(f"Failed to generate image: {str(e)}")


if __name__ == "__main__":
    import asyncio

    async def main():
        llm = OpenAILLMService()
        response = await llm.generate(
            "What is PTIT? How many majors does it have, and what is the score for the IT major?"
        )
        print("Response:", response)

    asyncio.run(main())
