"""
API router for Admin authentication and management endpoints.

Handles admin login, dashboard access, and administrative operations.
"""

from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = "your-secret-key-here"  # TODO: Load from config
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24


# =============================================================================
# Models
# =============================================================================

class AdminLogin(BaseModel):
    """Admin login request."""
    username: str
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# =============================================================================
# Auth Helpers
# =============================================================================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Create JWT access token.
    
    Args:
        data: Data to encode in token
        expires_delta: Optional custom expiration time
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """
    Verify and decode JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token data or None if invalid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None


async def get_current_admin(authorization: Optional[str] = Header(None)):
    """
    Dependency to verify admin authentication.
    
    Args:
        authorization: Authorization header with Bearer token
        
    Returns:
        Admin user data
        
    Raises:
        HTTPException if not authenticated
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return payload


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(credentials: AdminLogin):
    """
    Admin login endpoint.
    
    Validates credentials and returns JWT token.
    For MVP: Uses simple username/password check.
    In production: Use proper user management system.
    """
    # Simple authentication (MVP)
    # TODO: Use database with proper user management
    if credentials.username != "admin":
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Verify password
    from config import settings
    if not pwd_context.verify(credentials.password, settings.admin_password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": credentials.username, "role": "admin"}
    )
    
    logger.info(f"Admin logged in: {credentials.username}")
    
    return AdminLoginResponse(
        access_token=access_token,
        expires_in=ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@router.get("/me")
async def get_current_admin_info(admin=Depends(get_current_admin)):
    """
    Get current admin user information.
    
    Protected endpoint that requires valid JWT token.
    """
    return {
        "username": admin.get("sub"),
        "role": admin.get("role"),
        "authenticated": True
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(admin=Depends(get_current_admin)):
    """
    Get dashboard statistics for admin.
    
    Returns overview of platform usage and data.
    """
    from services.database import (
        get_candidate_service,
        get_analysis_service
    )
    
    try:
        # TODO: Implement proper statistics queries
        # For now, return placeholder data
        
        return JSONResponse({
            "total_candidates": 0,  # TODO: Count from database
            "total_companies": 0,
            "total_analyses": 0,
            "analyses_this_month": 0,
            "ai_providers_active": 0,
            "message": "Dashboard stats (placeholder)"
        })
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving dashboard statistics"
        )


@router.get("/candidates")
async def list_candidates(
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """
    List all candidates (Admin only).
    
    Returns paginated list of candidates with their data.
    """
    from services.database import get_candidate_service
    
    try:
        candidate_service = get_candidate_service()
        candidates = await candidate_service.list_all(limit=limit, offset=offset)
        
        return JSONResponse({
            "total": len(candidates),
            "limit": limit,
            "offset": offset,
            "candidates": candidates
        })
        
    except Exception as e:
        logger.error(f"Error listing candidates: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving candidates"
        )

