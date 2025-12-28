"""Configuration routes for admin panel."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field
from config import app_config
from config.ai import (
    openai_config,
    anthropic_config,
    gemini_config,
    embedding_config,
    rag_config,
)


router = APIRouter(prefix="/admin/config", tags=["configuration"])


class ModelConfigRequest(BaseModel):
    """Request model for updating model configuration."""

    provider: Optional[str] = Field(
        None, description="LLM provider: openai, anthropic, gemini"
    )
    qa_model: Optional[str] = Field(None, description="Model for Q&A tasks")
    reasoning_model: Optional[str] = Field(
        None, description="Model for reasoning tasks"
    )
    temperature: Optional[float] = Field(
        None, ge=0, le=2, description="Temperature setting"
    )
    max_tokens: Optional[int] = Field(None, ge=100, le=128000, description="Max tokens")
    top_k: Optional[int] = Field(None, ge=1, le=20, description="RAG top_k")
    similarity_threshold: Optional[float] = Field(
        None, ge=0, le=1, description="RAG similarity threshold"
    )


class ProviderStatus(BaseModel):
    """Status of an LLM provider."""

    name: str
    configured: bool
    models: list[str]


@router.get("/info")
async def get_config_info():
    """Get public configuration information."""
    return {
        "app_name": "AMI RAG System",
        "version": "2.0.0-refactored",
        "environment": app_config.environment,
        "features": {
            "rag": True,
            "chat": True,
            "crawler": True,
            "images": False,
        },
    }


@router.get("/models")
async def get_model_config():
    """Get current AI model configuration."""
    # Check which providers are configured (have API keys)
    providers = [
        ProviderStatus(
            name="openai",
            configured=bool(openai_config.api_key),
            models=[
                "gpt-4o-mini",
                "gpt-4o",
                "gpt-4-turbo",
                "gpt-3.5-turbo",
                "o4-mini",
                "o3",
                "o1",
                "o1-mini",
            ],
        ),
        ProviderStatus(
            name="anthropic",
            configured=bool(anthropic_config.api_key),
            models=[
                "claude-3-5-haiku-20241022",
                "claude-sonnet-4-20250514",
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
            ],
        ),
        ProviderStatus(
            name="gemini",
            configured=bool(gemini_config.api_key),
            models=[
                "gemini-2.5-flash-lite-preview-09-2025",
                "gemini-1.5-flash",
                "gemini-1.5-pro",
                "gemini-3-pro-preview",
            ],
        ),
    ]

    # Determine current provider based on which one is configured
    current_provider = "openai"
    if gemini_config.api_key:
        current_provider = "gemini"
    elif anthropic_config.api_key:
        current_provider = "anthropic"
    elif openai_config.api_key:
        current_provider = "openai"

    # Get current model names based on provider
    if current_provider == "openai":
        qa_model = openai_config.model_qa
        reasoning_model = openai_config.model_reasoning
    elif current_provider == "anthropic":
        qa_model = anthropic_config.model_qa
        reasoning_model = anthropic_config.model_reasoning
    else:
        qa_model = gemini_config.model_qa
        reasoning_model = gemini_config.model_reasoning

    return {
        "config": {
            "provider": current_provider,
            "qaModel": qa_model,
            "reasoningModel": reasoning_model,
            "temperature": 0.7,  # Default, not stored in config currently
            "maxTokens": 2048,  # Default
            "topK": rag_config.top_k,
            "similarityThreshold": rag_config.similarity_threshold,
        },
        "providers": [p.model_dump() for p in providers],
        "embedding": {
            "model": embedding_config.model,
            "dimension": embedding_config.dimension,
            "batchSize": embedding_config.batch_size,
            "device": embedding_config.device,
        },
    }


@router.put("/models")
async def update_model_config(request: ModelConfigRequest):
    """
    Update AI model configuration.

    Note: This endpoint currently returns success but does not persist changes,
    as the configuration is loaded from environment variables at startup.
    To make changes persistent, update the .env file and restart the service.
    """
    # In a production system, this would update a database or config file
    # For now, we acknowledge the request but note that changes require restart
    return {
        "success": True,
        "message": "Configuration acknowledged. Note: To persist changes, update environment variables and restart the service.",
        "received": request.model_dump(exclude_none=True),
    }
