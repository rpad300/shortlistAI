"""
Admin API router - Using Supabase Auth.

Handles admin authentication and data management using Supabase native authentication.
Admin users are managed in Supabase Auth with role in user_metadata.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


# =============================================================================
# Models
# =============================================================================

class AdminLogin(BaseModel):
    """Admin login request."""
    email: EmailStr
    password: str


class AdminLoginResponse(BaseModel):
    """Admin login response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: dict


class AdminUser(BaseModel):
    """Admin user information."""
    id: str
    email: str
    role: str
    authenticated: bool


# =============================================================================
# Auth Helpers
# =============================================================================

async def get_current_admin(authorization: Optional[str] = Header(None)):
    """
    Dependency to verify admin authentication using Supabase Auth.
    
    Validates Bearer token and verifies admin role in user_metadata.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        from database import get_supabase_client
        client = get_supabase_client()
        
        # Verify token with Supabase Auth
        user_response = client.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
                headers={"WWW-Authenticate": "Bearer"}
            )
        
        user = user_response.user
        user_metadata = user.user_metadata or {}
        
        # Verify admin role
        user_role = user_metadata.get("role", "")
        if user_role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        return {
            "id": user.id,
            "email": user.email,
            "role": user_role,
            "user_metadata": user_metadata
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


async def require_super_admin(current_admin=Depends(get_current_admin)):
    """Verify super admin role."""
    if current_admin.get("role") != "super_admin":
        raise HTTPException(
            status_code=403,
            detail="Super admin access required"
        )
    return current_admin


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/login", response_model=AdminLoginResponse)
async def admin_login(credentials: AdminLogin, request: Request):
    """
    Admin login using Supabase Auth.
    
    Authenticates admin users stored in Supabase Auth with role in user_metadata.
    """
    from database import get_supabase_client
    
    try:
        client = get_supabase_client()
        client_ip = request.client.host if request.client else "unknown"
        
        logger.info(f"Admin login attempt - {credentials.email} - IP: {client_ip}")
        
        # Authenticate with Supabase Auth
        auth_response = client.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password
        })
        
        if not auth_response or not auth_response.user:
            logger.warning(f"Admin login failed - {credentials.email}")
            raise HTTPException(
                status_code=401,
                detail="Invalid credentials"
            )
        
        user = auth_response.user
        user_metadata = user.user_metadata or {}
        user_role = user_metadata.get("role", "")
        
        # Verify admin role
        if user_role not in ["admin", "super_admin"]:
            logger.warning(f"Non-admin login attempt - {credentials.email}")
            raise HTTPException(
                status_code=403,
                detail="Admin access required"
            )
        
        if not auth_response.session:
            raise HTTPException(
                status_code=500,
                detail="Failed to create session"
            )
        
        logger.info(f"✅ Admin logged in - {user.email} - Role: {user_role}")
        
        return AdminLoginResponse(
            access_token=auth_response.session.access_token,
            token_type="bearer",
            expires_in=auth_response.session.expires_in or 3600,
            user={
                "id": user.id,
                "email": user.email,
                "role": user_role,
                "name": f"{user_metadata.get('first_name', '')} {user_metadata.get('last_name', '')}".strip()
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Admin login error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )


@router.get("/me")
async def get_current_admin_info(admin=Depends(get_current_admin)):
    """Get current admin user information."""
    return {
        "id": admin["id"],
        "email": admin["email"],
        "role": admin["role"],
        "authenticated": True
    }


@router.get("/dashboard/stats")
async def get_dashboard_stats(admin=Depends(get_current_admin)):
    """Get basic dashboard statistics."""
    from services.database import (
        get_candidate_service,
        get_analysis_service
    )
    
    try:
        # TODO: Implement actual statistics
        return JSONResponse({
            "total_candidates": 0,
            "total_companies": 0,
            "total_analyses": 0,
            "message": "Stats coming soon"
        })
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@router.get("/dashboard/detailed-stats")
async def get_detailed_stats(admin=Depends(get_current_admin)):
    """Get detailed dashboard statistics."""
    try:
        return JSONResponse({
            "overview": {
                "total_candidates": 0,
                "total_companies": 0,
                "total_interviewers": 0,
                "total_job_postings": 0,
                "total_analyses": 0,
                "total_cvs": 0
            },
            "activity": {
                "analyses_this_month": 0,
                "new_candidates_this_month": 0,
                "new_companies_this_month": 0,
                "new_job_postings_this_month": 0
            },
            "ai_usage": {
                "total_api_calls": 0,
                "cost_this_month": 0,
                "average_response_time": 0,
                "success_rate": 0
            },
            "providers": {
                "gemini": {"calls": 0, "cost": 0},
                "openai": {"calls": 0, "cost": 0},
                "claude": {"calls": 0, "cost": 0},
                "kimi": {"calls": 0, "cost": 0},
                "minimax": {"calls": 0, "cost": 0}
            },
            "languages": {
                "en": 0,
                "pt": 0,
                "fr": 0,
                "es": 0
            }
        })
    except Exception as e:
        logger.error(f"Error getting detailed stats: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving statistics")


@router.get("/candidates")
async def list_candidates(
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """List all candidates (Admin only)."""
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
        raise HTTPException(status_code=500, detail="Error retrieving candidates")


@router.get("/candidates/{candidate_id}")
async def get_candidate_details(
    candidate_id: str,
    admin=Depends(get_current_admin)
):
    """Get candidate details with CVs and analyses."""
    from services.database import get_candidate_service
    
    try:
        candidate_service = get_candidate_service()
        candidate = await candidate_service.get_by_id(candidate_id)
        
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        cvs = await candidate_service.get_cvs_by_candidate(candidate_id)
        analyses = await candidate_service.get_analyses_by_candidate(candidate_id)
        
        return JSONResponse({
            "candidate": candidate,
            "cvs": cvs,
            "analyses": analyses,
            "stats": {
                "total_cvs": len(cvs),
                "total_analyses": len(analyses)
            }
        })
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate details: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving candidate")


@router.get("/analyses")
async def list_analyses(
    mode: Optional[str] = None,
    provider: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """List all analyses with optional filtering."""
    from services.database import get_analysis_service
    
    try:
        analysis_service = get_analysis_service()
        analyses = await analysis_service.list_all(
            mode=mode,
            provider=provider,
            limit=limit,
            offset=offset
        )
        
        return JSONResponse({
            "total": len(analyses),
            "limit": limit,
            "offset": offset,
            "filters": {"mode": mode, "provider": provider},
            "analyses": analyses
        })
    except Exception as e:
        logger.error(f"Error listing analyses: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analyses")


@router.get("/analyses/{analysis_id}")
async def get_analysis_details(
    analysis_id: str,
    admin=Depends(get_current_admin)
):
    """Get detailed analysis information."""
    from services.database import get_analysis_service
    
    try:
        analysis_service = get_analysis_service()
        analysis = await analysis_service.get_by_id(analysis_id)
        
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return JSONResponse({"analysis": analysis})
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting analysis: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving analysis")


@router.get("/companies")
async def list_companies(
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """List all companies."""
    from services.database import get_company_service
    
    try:
        company_service = get_company_service()
        companies = await company_service.list_all(limit=limit, offset=offset)
        
        return JSONResponse({
            "total": len(companies),
            "limit": limit,
            "offset": offset,
            "companies": companies
        })
    except Exception as e:
        logger.error(f"Error listing companies: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving companies")


@router.get("/interviewers")
async def list_interviewers(
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """List all interviewers."""
    from services.database import get_interviewer_service
    
    try:
        interviewer_service = get_interviewer_service()
        interviewers = await interviewer_service.list_all(limit=limit, offset=offset)
        
        return JSONResponse({
            "total": len(interviewers),
            "limit": limit,
            "offset": offset,
            "interviewers": interviewers
        })
    except Exception as e:
        logger.error(f"Error listing interviewers: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving interviewers")


@router.get("/job-postings")
async def list_job_postings(
    limit: int = 50,
    offset: int = 0,
    admin=Depends(get_current_admin)
):
    """List all job postings."""
    from services.database import get_job_posting_service
    
    try:
        job_posting_service = get_job_posting_service()
        job_postings = await job_posting_service.list_all(limit=limit, offset=offset)
        
        return JSONResponse({
            "total": len(job_postings),
            "limit": limit,
            "offset": offset,
            "job_postings": job_postings
        })
    except Exception as e:
        logger.error(f"Error listing job postings: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving job postings")
