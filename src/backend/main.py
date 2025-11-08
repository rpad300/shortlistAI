"""
Main FastAPI application entry point for CV Analysis Platform.

This module initializes the FastAPI app with all necessary middleware,
routers, and configuration for the CV analysis platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create FastAPI app instance
app = FastAPI(
    title="CV Analysis Platform API",
    description="AI-powered CV analysis for interviewers and candidates",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware configuration
# Allow frontend to communicate with backend during development and production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Restrict to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gzip compression for responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Rate limiting middleware
from middleware.rate_limit import get_rate_limiter

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests."""
    # Apply rate limiting only to public endpoints
    if request.url.path.startswith("/api/interviewer") or request.url.path.startswith("/api/candidate"):
        rate_limiter = get_rate_limiter()
        await rate_limiter.check_rate_limit(request)
    
    response = await call_next(request)
    return response


@app.get("/")
async def root():
    """
    Root endpoint to verify API is running.
    
    Returns basic information about the API and health status.
    """
    return {
        "status": "ok",
        "service": "CV Analysis Platform API",
        "version": "0.1.0",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Verifies that the API is responsive and can connect to critical services.
    """
    from database import check_database_connection
    
    db_healthy = await check_database_connection()
    
    return {
        "status": "healthy" if db_healthy else "degraded",
        "database": "connected" if db_healthy else "error",
        "supabase": "connected" if db_healthy else "error"
    }


# Import routers
from routers import interviewer, candidate, admin

# Register routers
app.include_router(interviewer.router, prefix="/api")
app.include_router(candidate.router, prefix="/api")
app.include_router(admin.router, prefix="/api")

# TODO: Add additional routers:
# - Admin AI management (prompts, providers, testing)
# - Admin translation management

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=debug
    )

