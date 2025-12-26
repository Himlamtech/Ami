"""
Google Gemini LLM provider - Simple, config-driven implementation.
Supports Vision (image QA) capabilities.
"""

import base64
import logging
from typing import Optional, AsyncIterator, Union

import google.genai as genai
from google.genai import types
from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config import gemini_config
from app.config.ai import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiLLMService(ILLMService):
    """Google Gemini LLM provider - wraps Google Generative AI SDK."""

    def __init__(
        self,
        config: GeminiConfig = None,
        default_mode: LLMMode = LLMMode.QA,
    ):
        """
        Initialize Gemini LLM provider.

        Args:
            config: Gemini configuration. If None, uses global gemini_config.
            default_mode: Default operation mode
        """
        self.config = config or gemini_config
        self._client = genai.Client(api_key=self.config.api_key)
        self._models = {
            LLMMode.QA: self.config.model_qa,
            LLMMode.REASONING: self.config.model_reasoning,
        }
        self._current_mode = default_mode
        logger.info(
            f"Gemini initialized - QA: {self.config.model_qa}, Reasoning: {self.config.model_reasoning}"
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

        Note: Context formatting should be done in Application layer.
        """
        model = self._models[mode or self._current_mode]

        try:
            # Simple prompt building - context is system message equivalent
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)

            logger.debug(f"Generating with {model}")

            response = await self._client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            result = response.text or ""
            logger.debug(f"Generated {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"Gemini error: {e}")
            raise RuntimeError(f"Generation failed: {str(e)}")

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
            full_prompt = f"{context}\n\n{prompt}" if context else prompt

            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)

            logger.debug(f"Streaming with {model}")

            response = await self._client.aio.models.generate_content(
                model=model,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Gemini stream error: {e}")
            yield f"[ERROR: {str(e)}]"

    async def image_qa(
        self,
        prompt: str,
        image: Union[bytes, str],
        mode: Optional[LLMMode] = None,
        **kwargs,
    ) -> str:
        """Answer questions about an image using Gemini Vision."""

        try:
            # Prepare image part
            if isinstance(image, bytes):
                # Raw bytes - encode to base64
                image_data = base64.b64encode(image).decode("utf-8")
                image_part = types.Part.from_bytes(
                    data=image, mime_type=kwargs.pop("mime_type", "image/jpeg")
                )
            elif isinstance(image, str):
                if image.startswith(("http://", "https://")):
                    # URL - use from_uri
                    image_part = types.Part.from_uri(
                        file_uri=image, mime_type=kwargs.pop("mime_type", "image/jpeg")
                    )
                else:
                    # Assume base64 string
                    image_bytes = base64.b64decode(image)
                    image_part = types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=kwargs.pop("mime_type", "image/jpeg"),
                    )
            else:
                raise ValueError(f"Unsupported image type: {type(image)}")

            # Build contents with image and text
            contents = [image_part, prompt]

            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)
            model = self._models[mode or self._current_mode]

            logger.debug(f"Image QA with {model}")

            response = await self._client.aio.models.generate_content(
                model=model,
                contents=contents,
                config=types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            result = response.text or ""
            logger.debug(f"Image QA: {len(result)} chars")
            return result

        except Exception as e:
            logger.error(f"Gemini image_qa error: {e}")
            raise RuntimeError(f"Image processing failed: {str(e)}")


if __name__ == "__main__":
    # Simple test
    import asyncio

    async def test_gemini():
        service = GeminiLLMService()
        prompt = "PTIT là gì? có bao nhiêu ngành, điểm ngành IT là bao nhiêu?"
        response = await service.generate(prompt, mode=LLMMode.QA)
        print("Response:", response)

    asyncio.run(test_gemini())
