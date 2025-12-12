from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.infrastructure.persistence.mongodb.client import (
    get_mongodb_client,
    get_database,
)
from app.config.services import ServiceRegistry
from app.api.middleware import LoggingMiddleware
from app.api.v1 import chat_api_router, admin_api_router
from app.api.v1.admin.config import router as config_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle events."""
    # Startup
    try:
        db = await get_database()
        ServiceRegistry.initialize(db)
        print("✅ Application initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize application: {e}")
        raise e

    yield

    # Shutdown
    try:
        client = await get_mongodb_client()
        await client.disconnect()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"❌ Error during shutdown: {e}")


app = FastAPI(
    title="Ami Digital Assistant",
    description="Ami Digital Assistant from PTIT",
    version="1.0.0",
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
app.include_router(chat_api_router, prefix=api_v1)
app.include_router(admin_api_router, prefix=api_v1)
app.include_router(config_router, prefix=api_v1)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "version": "1.0.0",
        "architecture": "Clean Architecture",
    }
