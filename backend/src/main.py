"""Main FastAPI application entry point."""

import os
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import v2_recommendations_router, v2_providers_router
from .api_v1 import router as v1_router


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="NYT Connections Puzzle Assistant API",
        description="REST API for puzzle assistance web application",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Configure CORS for local development
    origins = [
        "http://localhost:3000",  # React dev server
        "http://127.0.0.1:3000",
        "http://localhost:8000",  # FastAPI docs
        "http://127.0.0.1:8000",
    ]

    # Add CORS from environment if specified
    cors_origins = os.getenv("BACKEND_CORS_ORIGINS", "").split(",")
    if cors_origins and cors_origins[0]:
        origins.extend([origin.strip() for origin in cors_origins])

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["*"],
    )

    # Include API routes
    app.include_router(v1_router, prefix="", tags=["puzzle"])
    app.include_router(v2_recommendations_router, tags=["v2-recommendations"])
    app.include_router(v2_providers_router, tags=["v2-providers"])

    return app


# Create the application instance
app = create_app()


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint for health check."""
    return {"message": "NYT Connections Puzzle Assistant API", "status": "running"}


@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "nyt-connections-puzzle-assistant",
        "version": "1.0.0",
    }


if __name__ == "__main__":
    import uvicorn

    # Get configuration from environment
    host = os.getenv("BACKEND_HOST", "localhost")
    port = int(os.getenv("BACKEND_PORT", "8000"))
    log_level = os.getenv("BACKEND_LOG_LEVEL", "info")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        log_level=log_level,
        reload=True,  # Enable auto-reload for development
        reload_dirs=["src"],  # Watch for changes in src directory
    )
