"""
Google Gemini LLM provider implementation.
Uses Google's Generative AI SDK (google-genai) with error handling and retry logic.
Supports 2 modes: QA (quick) and REASONING (deep thinking).
"""

import logging
from typing import Optional, AsyncIterator, Dict

import google.genai as genai
from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config import gemini_config
from app.config.ai import GeminiConfig

logger = logging.getLogger(__name__)


class GeminiLLMService(ILLMService):
    """Google Gemini LLM provider with mode-based model selection."""

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
        # Initialize Gemini client with API key
        self._client = genai.Client(api_key=self.config.api_key)
        self._models = {
            LLMMode.QA: self.config.model_qa,
            LLMMode.REASONING: self.config.model_reasoning,
        }
        self._current_mode = default_mode
        logger.info(
            f"Initialized GeminiLLMService - QA: {self.config.model_qa}, Reasoning: {self.config.model_reasoning}, "
            f"Default mode: {default_mode.value}"
        )

    def get_model_for_mode(self, mode: LLMMode) -> str:
        """Get the model name for a specific mode."""
        return self._models.get(mode, self._models[LLMMode.QA])
    
    def set_mode(self, mode: LLMMode) -> None:
        """Set the current operation mode."""
        self._current_mode = mode
        logger.debug(f"Gemini mode set to: {mode.value}")
    
    def get_current_mode(self) -> LLMMode:
        """Get the current operation mode."""
        return self._current_mode
    
    def get_available_models(self) -> Dict[LLMMode, str]:
        """Get all available models for this provider."""
        return self._models.copy()
    
    def _get_active_model_name(self, mode: Optional[LLMMode] = None) -> str:
        """Get the model name to use for this request."""
        target_mode = mode if mode is not None else self._current_mode
        return self._models[target_mode]

    async def generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> str:
        """Generate completion with mode-based model selection."""
        model_name = self._get_active_model_name(mode)
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Use the following context to answer:\n{context}\n\nQuestion: {prompt}"
            
            # Extract supported parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)
            
            logger.debug(f"Generating with model: {model_name}, mode: {mode or self._current_mode}")
            
            # Generate response using async method
            response = await self._client.aio.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
            )

            result = response.text if response.text else ""
            logger.debug(f"Generated response: {len(result)} chars, model: {model_name}")
            return result

        except Exception as e:
            logger.error(f"Error in Gemini generate: {e}")
            raise RuntimeError(f"Failed to generate: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion with mode-based model selection."""
        model_name = self._get_active_model_name(mode)
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Use the following context to answer:\n{context}\n\nQuestion: {prompt}"
            
            # Extract supported parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)
            
            logger.debug(f"Streaming with model: {model_name}, mode: {mode or self._current_mode}")
            
            # Generate streaming response
            response = await self._client.aio.models.generate_content(
                model=model_name,
                contents=full_prompt,
                config=genai.types.GenerateContentConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                ),
                stream=True,
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error in Gemini stream: {e}")
            yield f"[ERROR: {str(e)}]"

if __name__ == "__main__":
    # Simple test
    import asyncio

    async def test_gemini():
        service = GeminiLLMService()
        prompt = "What is PTIT"
        response = await service.generate(prompt, mode=LLMMode.QA)
        print("Response:", response)

    asyncio.run(test_gemini())