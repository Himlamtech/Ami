import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging

from infrastructure.persistence.mongodb.client import (
    get_mongodb_client,
    get_database,
)
from config.services import ServiceRegistry
from api.middleware import LoggingMiddleware, admin_only_middleware
from api.v1 import chat_api_router, admin_api_router, auth_api_router
from api.v1.admin.config import router as config_router
from application.use_cases.monitor_targets.monitor_scheduler import (
    register_monitor_targets_job,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        db = await get_database()
        ServiceRegistry.initialize(db)
        await register_monitor_targets_job()
        logger.info("✅ Application initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {e}")
        raise

    yield

    # Shutdown
    try:
        scheduler = ServiceRegistry.get_scheduler()
        await scheduler.shutdown()
        logger.info("✅ Scheduler shutdown complete")
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")

    try:
        client = await get_mongodb_client()
        await client.disconnect()
        logger.info("✅ Database connection closed")
    except Exception as e:
        logger.error(f"❌ Error closing database: {e}")


app = FastAPI(
    title="AMI - PTIT Intelligent Assistant",
    description="RAG-Powered Chatbot System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
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


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = f"req_{uuid.uuid4()}"
    return JSONResponse(
        status_code=422,
        content={
            "error": "Validation error",
            "details": exc.errors(),
            "request_id": request_id,
        },
    )


# Routes
API_V1 = "/api/v1"
app.include_router(chat_api_router, prefix=API_V1, tags=["chat"])
app.include_router(auth_api_router, prefix=API_V1, tags=["auth"])
app.include_router(admin_api_router, prefix=API_V1, tags=["admin"])
app.include_router(config_router, prefix=API_V1, tags=["admin-config"])


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Ami Backend"}


@app.get("/health/admin")
async def admin_health_check():
    return {"status": "ok", "service": "Admin Backend"}
