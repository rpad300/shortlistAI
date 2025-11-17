"""
Main FastAPI application entry point for CV Analysis Platform.

This module initializes the FastAPI app with all necessary middleware,
routers, and configuration for the CV analysis platform.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging to show ALL levels including DEBUG and INFO
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)

# Force all loggers to INFO level
for logger_name in ['services.ai_analysis', 'services.ai.gemini_provider', 'services.ai.manager']:
    logging.getLogger(logger_name).setLevel(logging.INFO)

# Get logger for this module
logger = logging.getLogger(__name__)

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

# Rate limiting middleware
from middleware.rate_limit import get_rate_limiter

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Apply rate limiting to requests."""
    # Exclude endpoints that need frequent requests or large uploads from rate limiting
    excluded_paths = [
        "/api/interviewer/step5/progress/",  # Polling endpoint (called every 3 seconds)
        "/api/interviewer/step6/progress/",  # Polling endpoint (called every 3 seconds)
        "/api/interviewer/step5",  # File upload endpoint
        "/api/candidate/step3",  # File upload endpoint
        "/api/interviewer/step2",  # Job posting upload
        "/api/candidate/step2",  # Job posting upload
        "/api/interviewer/step8/report/",  # PDF download
        "/api/candidate/step6/download/",  # PDF download
    ]
    
    # Check if this path should be excluded
    should_exclude = any(request.url.path.startswith(path) for path in excluded_paths)
    
    # Apply rate limiting only to public endpoints that are not excluded
    if (request.url.path.startswith("/api/interviewer") or request.url.path.startswith("/api/candidate")) and not should_exclude:
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


@app.get("/api/stats/total-analyses")
async def get_total_analyses():
    """
    Public endpoint to get the total number of analyses performed.
    
    This endpoint is used to display social proof on the homepage
    without exposing sensitive data about individual analyses.
    
    Returns:
        JSON with total_analyses count
    """
    try:
        from services.database.analysis_service import get_analysis_service
        
        analysis_service = get_analysis_service()
        total = await analysis_service.count_all()
        
        logger.info(f"Total analyses count: {total}")
        
        response = JSONResponse({
            "total_analyses": total,
            "status": "success"
        })
        # Add CORS headers explicitly
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response
    except Exception as e:
        logger.error(f"Error getting total analyses count: {e}", exc_info=True)
        # Return 0 on error to avoid breaking the frontend
        response = JSONResponse({
            "total_analyses": 0,
            "status": "error"
        })
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response


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
from routers import interviewer, candidate, admin, enrichment, prompts, chatbot, profiles

# Register routers
app.include_router(interviewer.router, prefix="/api")
app.include_router(candidate.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")  # Chatbot CV Preparation flow
app.include_router(profiles.router, prefix="/api")
app.include_router(enrichment.router)
app.include_router(admin.router, prefix="/api")
app.include_router(prompts.router)  # Admin prompts management

# TODO: Add additional routers:
# - Admin translation management

if __name__ == "__main__":
    import uvicorn
    import sys
    
    port = int(os.getenv("APP_PORT", 8000))
    debug = os.getenv("APP_DEBUG", "False").lower() == "true"
    
    # Configure reload settings for Windows compatibility
    # Limit reload to specific directories to reduce issues with multiprocessing on Windows
    reload_config = {
        "reload": debug,
    }
    
    if debug:
        # Limit reload to backend directory only to reduce false positives
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        reload_config["reload_dirs"] = [backend_dir]
        reload_config["reload_includes"] = ["*.py"]
        # Exclude common files that change frequently but don't need reload
        reload_config["reload_excludes"] = ["*.pyc", "__pycache__", "*.log"]
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        **reload_config
    )

