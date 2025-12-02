"""
Anthropic Claude LLM provider - Simple implementation.
Config lấy từ settings.py
"""

import logging
from typing import Optional, AsyncIterator

from anthropic import (
    AsyncAnthropic,
    APIError,
    APITimeoutError,
    RateLimitError,
)

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class AnthropicLLMService(ILLMService):
    """Anthropic Claude LLM provider."""
    
    settings = Settings()

    def __init__(self, default_mode: LLMMode = LLMMode.QA):
        self.client = AsyncAnthropic(
            api_key=self.settings.anthropic_api_key,
            max_retries=3,
            timeout=60.0,
        )
        self._models = {
            LLMMode.QA: self.settings.anthropic_model_qa,
            LLMMode.REASONING: self.settings.anthropic_model_reasoning,
        }
        self._current_mode = default_mode
        logger.info(
            f"Initialized AnthropicLLMService - QA: {self.settings.anthropic_model_qa}, "
            f"Reasoning: {self.settings.anthropic_model_reasoning}"
        )

    def _get_model(self, mode: Optional[LLMMode] = None) -> str:
        """Get model name for the mode."""
        return self._models[mode or self._current_mode]

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> str:
        """Generate completion."""
        model = self._get_model(mode)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            system = None
            if context:
                system = f"Use the following context to answer:\n{context}"
            
            max_tokens = kwargs.pop("max_tokens", 4096)
            temperature = kwargs.pop("temperature", 0.7)
            
            logger.debug(f"Generating with model: {model}")
            
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
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion."""
        model = self._get_model(mode)
        
        try:
            messages = [{"role": "user", "content": prompt}]
            
            system = None
            if context:
                system = f"Use the following context to answer:\n{context}"
            
            max_tokens = kwargs.pop("max_tokens", 4096)
            temperature = kwargs.pop("temperature", 0.7)
            
            logger.debug(f"Streaming with model: {model}")
            
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