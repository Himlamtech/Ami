"""
FastAPI application entry point.
Main application initialization and configuration.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.admin_routes import router as admin_router
from app.api.auth_routes import router as auth_router
from app.api.routes import router
from app.application.factory import ProviderFactory
from app.config.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    yield
    await ProviderFactory.cleanup()


app = FastAPI(
    title="AMI RAG System - PTIT Assistant",
    description=f"""
    Intelligent Chatbot system for PTIT using Retrieval-Augmented Generation (RAG).
    
    ## Features
    - **Question Answering**: RAG-powered Q&A with thinking modes
    - **Document Management**: Admin system for managing vector database
    - **Authentication**: Secure JWT-based authentication
    - **Vector Search**: Qdrant-powered semantic search
    - **Flexible Thinking**: Fast, Balance, and Thinking modes
    
    ## Tech Stack
    - **LLM**: OpenAI (GPT-4 variants + o4-mini)
    - **Embeddings**: HuggingFace (Vietnamese document embeddings)
    - **Vector DB**: Qdrant
    - **Database**: MongoDB (users, documents, metadata)
    - **Cache**: Redis
    
    ## API Structure
    - `/api/v1/auth/*` - Authentication endpoints
    - `/api/v1/generate/*` - Q&A with RAG support
    - `/api/v1/vectordb/*` - Vector database management
    - `/api/v1/config/*` - System configuration and health
    
    App Port: {settings.app_port}
    """,
    version="3.0.0",
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "authentication",
            "description": "User authentication and management (Admin only for registration)",
        },
        {
            "name": "generate",
            "description": "RAG-powered Q&A with thinking modes (fast/balance/thinking)",
        },
        {
            "name": "vectordb",
            "description": "Vector database CRUD operations for document management",
        },
        {
            "name": "config",
            "description": "System configuration, models, and health status",
        },
    ],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root endpoint with API overview."""
    return {
        "name": "AMI RAG System - PTIT Assistant",
        "version": "3.0.0",
        "description": "Intelligent Chatbot for PTIT using RAG",
        "app_port": settings.app_port,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": "/api/v1/config/health",
        },
        "features": [
            "Question Answering with RAG",
            "Three thinking modes (fast/balance/thinking)",
            "Admin document management",
            "JWT authentication",
            "Vietnamese text embeddings",
            "Qdrant vector search",
        ],
        "tech_stack": {
            "llm": "OpenAI (GPT-4 + o4-mini)",
            "embeddings": "HuggingFace (Vietnamese)",
            "vector_db": "Qdrant",
            "database": "MongoDB",
            "cache": "Redis",
        },
    }
