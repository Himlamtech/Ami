"""
Google Gemini LLM provider implementation.
Uses Google's Generative AI SDK with error handling and retry logic.
Supports 2 modes: QA (quick) and REASONING (deep thinking).
"""

import logging
from typing import Optional, AsyncIterator, Dict

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from app.domain.enums.llm_mode import LLMMode
from app.application.interfaces.services.llm_service import ILLMService
from app.config.settings import Settings
logger = logging.getLogger(__name__)


class GeminiLLMService(ILLMService):
    """Google Gemini LLM provider with mode-based model selection."""
    settings = Settings()
    def __init__(
        self,
        default_mode: LLMMode = LLMMode.QA,
    ):
        """
        Initialize Gemini LLM provider.
        
        Args:
            api_key: Google API key
            model_qa: Model for Q&A mode (fast, lightweight)
            model_reasoning: Model for Reasoning mode (powerful, thinking)
            default_mode: Default operation mode
        """
        genai.configure(api_key=self.settings.gemini_api_key)
        self._models = {
            LLMMode.QA: self.settings.gemini_model_qa,
            LLMMode.REASONING: self.settings.gemini_model_reasoning,
        }
        self._model_instances = {
            LLMMode.QA: genai.GenerativeModel(self.settings.gemini_model_qa),
            LLMMode.REASONING: genai.GenerativeModel(self.settings.gemini_model_reasoning),
        }
        self._current_mode = default_mode
        logger.info(
            f"Initialized GeminiLLMService - QA: {self.settings.gemini_model_qa}, Reasoning: {self.settings.gemini_model_reasoning}, "
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
    
    def _get_active_model(self, mode: Optional[LLMMode] = None):
        """Get the model instance to use for this request."""
        target_mode = mode if mode is not None else self._current_mode
        return self._model_instances[target_mode]
    
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
        model = self._get_active_model(mode)
        model_name = self._get_active_model_name(mode)
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Use the following context to answer:\n{context}\n\nQuestion: {prompt}"
            
            # Extract supported parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)
            
            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            logger.debug(f"Generating with model: {model_name}, mode: {mode or self._current_mode}")
            
            # Generate response
            response = await model.generate_content_async(
                full_prompt,
                generation_config=generation_config,
            )

            result = response.text
            logger.debug(f"Generated response: {len(result)} chars, model: {model_name}")
            return result

        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini rate limit exceeded: {e}")
            raise RuntimeError("Rate limit exceeded. Please try again later.")
        except google_exceptions.DeadlineExceeded as e:
            logger.error(f"Gemini API timeout: {e}")
            raise RuntimeError("Request timeout. Please try again.")
        except google_exceptions.GoogleAPIError as e:
            logger.error(f"Gemini API error: {e}")
            raise RuntimeError(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in Gemini generate: {e}")
            raise RuntimeError(f"Failed to generate: {str(e)}")

    async def stream_generate(
        self,
        prompt: str,
        context: Optional[str] = None,
        mode: Optional[LLMMode] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream completion with mode-based model selection."""
        model = self._get_active_model(mode)
        model_name = self._get_active_model_name(mode)
        
        try:
            # Build full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Use the following context to answer:\n{context}\n\nQuestion: {prompt}"
            
            # Extract supported parameters
            temperature = kwargs.pop("temperature", 0.7)
            max_tokens = kwargs.pop("max_tokens", 4096)
            
            # Configure generation
            generation_config = genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            logger.debug(f"Streaming with model: {model_name}, mode: {mode or self._current_mode}")
            
            # Generate streaming response
            response = await model.generate_content_async(
                full_prompt,
                generation_config=generation_config,
                stream=True,
            )
            
            async for chunk in response:
                if chunk.text:
                    yield chunk.text

        except google_exceptions.ResourceExhausted as e:
            logger.error(f"Gemini rate limit in stream: {e}")
            yield "[ERROR: Rate limit exceeded]"
        except google_exceptions.DeadlineExceeded as e:
            logger.error(f"Gemini timeout in stream: {e}")
            yield "[ERROR: Request timeout]"
        except Exception as e:
            logger.error(f"Error in Gemini stream: {e}")
            yield f"[ERROR: {str(e)}]"