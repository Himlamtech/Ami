import asyncio
import logging
import time
from typing import Any, AsyncIterator

import rootutils
from openai import OpenAI

rootutils.setup_root(__file__, indicator=".env", pythonpath=True)

from app.core.config import Config

logger = logging.getLogger(__name__)


class OpenAILLM:
    """Simple OpenAI wrapper."""

    def __init__(
        self,
        config: Config = None,
        model: str = "gpt-4.1-nano",
        temperature: float = 0.5,
    ) -> None:
        if config is None:
            config = Config()
        self.config = config
        self.model = model
        self.temperature = temperature
        self._client = OpenAI(api_key=config.OPENAI_API_KEY)

    def generate(
        self,
        messages: list[dict[str, Any]],
        model_id: str = "gpt-4.1-nano",
        temperature: float = 0.5,
    ) -> str:
        """Get completion."""
        response = self._client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def stream_generate(
        self,
        messages: list[dict[str, Any]],
        model_id: str = "gpt-4.1-nano",
        temperature: float = 0.5,
    ) -> AsyncIterator[str]:
        """Get streaming completion."""
        response = self._client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=temperature,
            stream=True,
        )
        for chunk in response:
            yield chunk.choices[0].delta.content

    async def batch_generate(
        self,
        messages: list[list[dict[str, Any]]],
        model_id: str = "gpt-4.1-nano",
        temperature: float = 0.5,
    ) -> list[str]:
        """Get batch completion."""
        response = await asyncio.to_thread(
            self._client.chat.completions.create,
            model=model_id,
            messages=messages,
            temperature=temperature,
        )
        return response.choices[0].message.content

    def health_check(self):
        start_time = time.time()
        response = self.client.chat.completions.create(
            model=self.model, messages=[{"role": "user", "content": "Hello!"}]
        )
        end_time = time.time()
        return f"Time taken: {end_time - start_time} seconds, response: {response.choices[0].message.content}"


# llm = OpenAILLM()
# print(llm.health_check())
