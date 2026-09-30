from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any
from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.logging import setup_logging, logger
from app.core.redis import init_redis, close_redis
from app.integrations.tigergraph.client import tigergraph_client
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """App lifespan context manager for startup and shutdown events."""
    setup_logging()
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    
    # Initialize Redis connection
    await init_redis()
    
    yield
    
    # Cleanup Redis connection
    await close_redis()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

# CORS Middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )

# Health endpoint requirement
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
async def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify backend service state."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }

# Dedicated TigerGraph health check endpoint
@app.get("/health/tigergraph", status_code=status.HTTP_200_OK, tags=["Health"])
async def tigergraph_health_check() -> Dict[str, Any]:
    """Lightweight connectivity health check for TigerGraph service."""
    is_healthy = tigergraph_client.check_health()
    if not is_healthy:
        return {
            "status": "unhealthy",
            "service": "TigerGraph",
            "graph": settings.TIGERGRAPH_GRAPH,
            "host": settings.TIGERGRAPH_HOST,
        }
    return {
        "status": "healthy",
        "service": "TigerGraph",
        "graph": settings.TIGERGRAPH_GRAPH,
        "host": settings.TIGERGRAPH_HOST,
    }

# Include API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)
