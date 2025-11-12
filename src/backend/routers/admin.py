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
    """Get detailed dashboard statistics with real data from database."""
    from services.database import (
        get_candidate_service,
        get_company_service,
        get_interviewer_service,
        get_job_posting_service,
        get_analysis_service,
        get_cv_service
    )
    
    try:
        # Get all services
        candidate_service = get_candidate_service()
        company_service = get_company_service()
        interviewer_service = get_interviewer_service()
        job_posting_service = get_job_posting_service()
        analysis_service = get_analysis_service()
        cv_service = get_cv_service()
        
        # Count totals
        total_candidates = await candidate_service.count_all()
        total_companies = await company_service.count_all()
        total_interviewers = await interviewer_service.count_all()
        total_job_postings = await job_posting_service.count_all()
        total_analyses = await analysis_service.count_all()
        total_cvs = await cv_service.count_all()
        
        # Count recent activity (last 30 days)
        new_candidates = await candidate_service.count_recent(30)
        new_companies = await company_service.count_recent(30)
        new_job_postings = await job_posting_service.count_recent(30)
        new_analyses = await analysis_service.count_recent(30)
        
        # Get provider distribution
        provider_counts = await analysis_service.count_by_provider()
        providers = {
            "gemini": {"calls": provider_counts.get("gemini", 0), "cost": 0},
            "openai": {"calls": provider_counts.get("openai", 0), "cost": 0},
            "claude": {"calls": provider_counts.get("claude", 0), "cost": 0},
            "kimi": {"calls": provider_counts.get("kimi", 0), "cost": 0},
            "minimax": {"calls": provider_counts.get("minimax", 0), "cost": 0}
        }
        
        # Get language distribution
        language_counts = await analysis_service.count_by_language()
        
        return JSONResponse({
            "overview": {
                "total_candidates": total_candidates,
                "total_companies": total_companies,
                "total_interviewers": total_interviewers,
                "total_job_postings": total_job_postings,
                "total_analyses": total_analyses,
                "total_cvs": total_cvs
            },
            "activity": {
                "analyses_this_month": new_analyses,
                "new_candidates_this_month": new_candidates,
                "new_companies_this_month": new_companies,
                "new_job_postings_this_month": new_job_postings
            },
            "ai_usage": {
                "total_api_calls": total_analyses,
                "cost_this_month": 0,  # TODO: Implement cost tracking
                "average_response_time": 0,  # TODO: Implement timing tracking
                "success_rate": 100 if total_analyses > 0 else 0
            },
            "providers": providers,
            "languages": language_counts
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


# =============================================================================
# Admin User Management
# =============================================================================

class CreateUserRequest(BaseModel):
    """Request to create new admin user."""
    email: EmailStr
    password: str
    email_confirm: bool = True
    user_metadata: dict


@router.post("/create-user")
async def create_admin_user(
    user_data: CreateUserRequest,
    admin=Depends(require_super_admin)
):
    """Create new admin user via Supabase Auth (super admin only)."""
    from database import get_supabase_client
    
    try:
        client = get_supabase_client()
        
        # Verify role in metadata
        role = user_data.user_metadata.get("role", "")
        if role not in ["admin", "super_admin"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid role. Must be 'admin' or 'super_admin'"
            )
        
        # Create user via Supabase Auth Admin API
        response = client.auth.admin.create_user({
            "email": user_data.email,
            "password": user_data.password,
            "email_confirm": user_data.email_confirm,
            "user_metadata": user_data.user_metadata
        })
        
        if not response or not response.user:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )
        
        logger.info(f"Admin user created: {response.user.email} - Role: {role}")
        
        return JSONResponse({
            "message": "Admin user created successfully",
            "user": {
                "id": response.user.id,
                "email": response.user.email,
                "role": role
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error creating admin user: {str(e)}"
        )


@router.get("/list-users")
async def list_admin_users(
    admin=Depends(require_super_admin)
):
    """List all admin users from Supabase Auth (super admin only)."""
    from database import get_supabase_client
    
    try:
        client = get_supabase_client()
        
        # List all users from Supabase Auth
        response = client.auth.admin.list_users()
        
        # Filter users with admin roles
        admin_users = []
        for user in response:
            user_metadata = user.user_metadata or {}
            role = user_metadata.get("role", "")
            if role in ["admin", "super_admin"]:
                admin_users.append({
                    "id": user.id,
                    "email": user.email,
                    "role": role,
                    "is_active": not user.banned_until,
                    "created_at": user.created_at,
                    "last_sign_in_at": user.last_sign_in_at,
                    "first_name": user_metadata.get("first_name"),
                    "last_name": user_metadata.get("last_name")
                })
        
        return JSONResponse({
            "total": len(admin_users),
            "admins": admin_users
        })
        
    except Exception as e:
        logger.error(f"Error listing admin users: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving admin users"
        )


@router.delete("/delete-user/{user_id}")
async def delete_admin_user(
    user_id: str,
    admin=Depends(require_super_admin)
):
    """Delete admin user from Supabase Auth (super admin only)."""
    from database import get_supabase_client
    
    try:
        # Prevent deleting yourself
        if user_id == admin["id"]:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete your own account"
            )
        
        client = get_supabase_client()
        
        # Delete user via Supabase Auth Admin API
        client.auth.admin.delete_user(user_id)
        
        logger.info(f"Admin user deleted: {user_id}")
        
        return JSONResponse({
            "message": "Admin user deleted successfully"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting admin user: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error deleting admin user"
        )
