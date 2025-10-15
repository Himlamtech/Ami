"""
FastAPI application entry point.
Main application initialization and configuration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import router
from app.application.factory import ProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    yield
    await ProviderFactory.cleanup()


app = FastAPI(
    title="RAG System API",
    description="""
    Comprehensive RAG system with multiple providers and extensive configuration options.
    
    ## Features
    - Multiple LLM providers (OpenAI, Gemini, Grok)
    - Multiple embedding providers (OpenAI, HuggingFace)
    - Multiple vector stores (pgvector, Chroma)
    - Thinking modes (Chain-of-Thought, Step-by-Step, Reasoning)
    - Document collections and metadata filtering
    - Streaming responses
    - Fine-grained generation control
    
    ## API Structure
    - `/api/v1/generate/*` - Generation endpoints with full control
    - `/api/v1/vectordb/*` - Vector database management
    - `/api/v1/config/*` - System configuration and status
    """,
    version="2.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "generate",
            "description": "LLM generation with RAG support. Control model, thinking mode, temperature, and more.",
        },
        {
            "name": "vectordb",
            "description": "Vector database operations. Upload, search, list, and delete documents with collections.",
        },
        {
            "name": "config",
            "description": "System configuration, available models, and health status.",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API overview."""
    return {
        "name": "RAG System API",
        "version": "2.0.0",
        "description": "Comprehensive RAG system with multiple providers",
        "endpoints": {"docs": "/docs", "redoc": "/redoc", "openapi": "/openapi.json"},
        "features": [
            "Multiple LLM providers",
            "Thinking modes",
            "Document collections",
            "Streaming responses",
            "Metadata filtering",
        ],
    }
