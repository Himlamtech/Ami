"""
Google Gemini LLM provider implementation.
Uses Google's Generative AI API with error handling.
"""

import logging
from typing import Optional

import google.generativeai as genai
from google.generativeai.types import BlockedPromptException

from app.config.settings import settings
from app.core.interfaces import ILLMProvider

logger = logging.getLogger(__name__)


class GeminiLLM(ILLMProvider):
    """Google Gemini LLM provider with enhanced error handling."""

    def __init__(self, api_key: str, model: str = settings.gemini_model):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)
        self.model_name = model
        logger.info(f"Initialized GeminiLLM with model: {model}")

    async def generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ) -> str:
        """Generate completion with error handling."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

            # Extract Gemini-specific kwargs
            generation_config = {}
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs.pop("temperature")
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs.pop("max_tokens")
            if "top_p" in kwargs:
                generation_config["top_p"] = kwargs.pop("top_p")

            response = await self.model.generate_content_async(
                full_prompt,
                generation_config=generation_config if generation_config else None,
            )

            result = response.text
            logger.debug(f"Generated response: {len(result)} chars")
            return result

        except BlockedPromptException as e:
            logger.error(f"Gemini blocked prompt: {e}")
            raise RuntimeError("Content was blocked by safety filters.")
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"Failed to generate with Gemini: {str(e)}")

    async def stream_generate(
        self, prompt: str, context: Optional[str] = None, **kwargs
    ):
        """Stream completion with error handling."""
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuestion: {prompt}"

            # Extract Gemini-specific kwargs
            generation_config = {}
            if "temperature" in kwargs:
                generation_config["temperature"] = kwargs.pop("temperature")
            if "max_tokens" in kwargs:
                generation_config["max_output_tokens"] = kwargs.pop("max_tokens")

            response = await self.model.generate_content_async(
                full_prompt,
                stream=True,
                generation_config=generation_config if generation_config else None,
            )

            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except BlockedPromptException as e:
            logger.error(f"Gemini blocked prompt in stream: {e}")
            yield "[ERROR: Content blocked by safety filters]"
        except Exception as e:
            logger.error(f"Error in Gemini stream: {e}")
            yield f"[ERROR: {str(e)}]"
