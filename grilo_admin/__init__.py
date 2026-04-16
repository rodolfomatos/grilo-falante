"""
Grilo Falante Admin Back-office API.

Provides administrative functions for managing:
- User authentication and authorization
- Plugin management
- Repository/RAG management
- System monitoring
- Auto-learning configuration
"""

import logging
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from grilo_admin.auth import get_current_user, user_store
from grilo_admin.models import User
from grilo_admin.routers import users_router, system_router, plugins_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting Grilo Falante Admin API...")
    logger.info("Default admin credentials: admin@example.com / admin123")
    yield
    logger.info("Shutting down Grilo Falante Admin API...")


app = FastAPI(
    title="Grilo Falante Admin API",
    description="Administrative back-office for Grilo Falante Platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"},
    )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "grilo-admin-api",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Grilo Falante Admin API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Example protected route."""
    return {
        "message": f"Hello, {current_user.email}",
        "role": current_user.role.value,
    }


app.include_router(users_router, prefix="/auth")
app.include_router(system_router, prefix="/admin")
app.include_router(plugins_router, prefix="/admin")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
