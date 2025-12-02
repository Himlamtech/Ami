"""
OpenAI LLM provider - Simple implementation.
Config lấy từ settings.py
"""

import logging
from typing import Optional

from openai import APIError, APITimeoutError, AsyncOpenAI, RateLimitError

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config.settings import Settings

logger = logging.getLogger(__name__)


class OpenAILLMService(ILLMService):
    """OpenAI LLM provider."""
    
    settings = Settings()

    def __init__(self, default_mode: LLMMode = LLMMode.QA):
        self.client = AsyncOpenAI(
            api_key=self.settings.openai_api_key, 
            max_retries=3, 
            timeout=60.0
        )
        self._models = {
            LLMMode.QA: self.settings.openai_model_qa,
            LLMMode.REASONING: self.settings.openai_model_reasoning,
        }
        self._current_mode = default_mode
        logger.info(
            f"Initialized OpenAILLMService - QA: {self.settings.openai_model_qa}, "
            f"Reasoning: {self.settings.openai_model_reasoning}"
        )

    def _get_model(self, mode: Optional[LLMMode] = None) -> str:
        """Get model name for the mode."""
        return self._models[mode or self._current_mode]
    
    def _is_reasoning_model(self, model: str) -> bool:
        """Check if model is reasoning type (o1, o3, o4 series)."""
        return model.startswith(("o1", "o3", "o4"))

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
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Use the following context to answer:\n{context}",
                })
            messages.append({"role": "user", "content": prompt})

            # Reasoning models không hỗ trợ temperature
            if self._is_reasoning_model(model):
                kwargs.pop("temperature", None)
                kwargs.pop("top_p", None)
            
            logger.debug(f"Generating with model: {model}")

            response = await self.client.chat.completions.create(
                model=model, 
                messages=messages, 
                **kwargs
            )

            result = response.choices[0].message.content
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
    ):
        """Stream completion."""
        model = self._get_model(mode)
        
        try:
            messages = []
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Use the following context to answer:\n{context}",
                })
            messages.append({"role": "user", "content": prompt})

            if self._is_reasoning_model(model):
                kwargs.pop("temperature", None)
                kwargs.pop("top_p", None)
            
            logger.debug(f"Streaming with model: {model}")

            stream = await self.client.chat.completions.create(
                model=model, 
                messages=messages, 
                stream=True, 
                **kwargs
            )
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Stream error: {e}")
            yield f"[ERROR: {str(e)}]"


if __name__ == "__main__":
    import asyncio
    
    async def main():
        llm = OpenAILLMService()
        response = await llm.generate("Hello, how are you?")
        print("Response:", response)
    
    asyncio.run(main())
