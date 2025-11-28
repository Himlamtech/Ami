from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.infrastructure.db.mongodb.client import get_mongodb_client, get_database
from app.infrastructure.factory import initialize_factory
from app.presentation.api.middleware import LoggingMiddleware
from app.presentation.api.routes import (
    auth_router,
    chat_router,
    generate_router,
    vectordb_router,
    image_router,
    admin_router,
    crawler_router,
    config_router,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Startup
    try:
        db = await get_database()
        initialize_factory(db)
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        raise e
    
    yield
    
    # Shutdown
    try:
        client = await get_mongodb_client()
        client.close()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")

app = FastAPI(
    title="AMI RAG System",
    description="Advanced RAG System with Clean Architecture",
    version="2.0.0",
    lifespan=lifespan,
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)

# Routes
api_v1 = "/api/v1"
app.include_router(auth_router, prefix=api_v1)
app.include_router(chat_router, prefix=api_v1)
app.include_router(generate_router, prefix=api_v1)
app.include_router(vectordb_router, prefix=api_v1)
app.include_router(image_router, prefix=api_v1)
app.include_router(admin_router, prefix=api_v1)
app.include_router(crawler_router, prefix=api_v1)
app.include_router(config_router, prefix=api_v1)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "2.0.0",
        "architecture": "Clean Architecture",
    }
