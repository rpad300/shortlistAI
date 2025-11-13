"""
Admin API router - Using Supabase Auth.

Handles admin authentication and data management using Supabase native authentication.
Admin users are managed in Supabase Auth with role in user_metadata.
"""

from fastapi import APIRouter, HTTPException, Depends, Header, Request, Body
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


@router.get("/settings/default-ai-provider")
async def get_default_ai_provider(admin=Depends(get_current_admin)):
    """Get the default AI provider fallback chain."""
    from database import get_supabase_client
    import json
    
    try:
        client = get_supabase_client()
        result = client.table("app_settings").select("*").eq("setting_key", "default_ai_provider").execute()
        
        if result.data and len(result.data) > 0:
            setting_value = result.data[0]["setting_value"]
            # Try to parse as JSON (new format)
            try:
                fallback_chain = json.loads(setting_value) if isinstance(setting_value, str) else setting_value
                if isinstance(fallback_chain, list):
                    return JSONResponse({
                        "fallback_chain": fallback_chain,
                        "description": result.data[0].get("description", "")
                    })
            except (json.JSONDecodeError, TypeError):
                # Old format (single provider string)
                return JSONResponse({
                    "fallback_chain": [
                        {"provider": setting_value, "model": None, "order": 1}
                    ],
                    "description": result.data[0].get("description", "")
                })
        
        # Return default if not set
        return JSONResponse({
            "fallback_chain": [
                {"provider": "gemini", "model": None, "order": 1}
            ],
            "description": "Default AI provider (not configured)"
        })
    except Exception as e:
        logger.error(f"Error getting default AI provider: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving default AI provider")


@router.put("/settings/default-ai-provider")
async def update_default_ai_provider(
    fallback_chain: list = Body(...),
    admin=Depends(get_current_admin)
):
    """Update the default AI provider fallback chain.
    
    Expected format:
    [
        {"provider": "gemini", "model": "gemini-2.5-flash-lite", "order": 1},
        {"provider": "kimi", "model": "kimi-k2-0905", "order": 2},
        ...
    ]
    """
    from database import get_supabase_client
    import json
    
    # Validate fallback chain
    if not isinstance(fallback_chain, list) or len(fallback_chain) == 0:
        raise HTTPException(
            status_code=400,
            detail="fallback_chain must be a non-empty array"
        )
    
    valid_providers = ["gemini", "openai", "claude", "kimi", "minimax"]
    
    for i, item in enumerate(fallback_chain):
        if not isinstance(item, dict):
            raise HTTPException(
                status_code=400,
                detail=f"Item {i} must be an object with provider, model, and order"
            )
        
        provider = item.get("provider")
        if provider not in valid_providers:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider '{provider}' at position {i}. Must be one of: {', '.join(valid_providers)}"
            )
        
        if "order" not in item:
            item["order"] = i + 1
    
    # Sort by order
    fallback_chain = sorted(fallback_chain, key=lambda x: x.get("order", 999))
    
    try:
        client = get_supabase_client()
        
        # Check if setting exists
        existing = client.table("app_settings").select("*").eq("setting_key", "default_ai_provider").execute()
        
        logger.info(f"Checking existing setting: found {len(existing.data) if existing.data else 0} record(s)")
        
        # Store as JSON string
        setting_data = {
            "setting_key": "default_ai_provider",
            "setting_value": json.dumps(fallback_chain),
            "description": f"AI provider fallback chain with {len(fallback_chain)} provider(s)"
        }
        
        if existing.data and len(existing.data) > 0:
            # Update existing - remove setting_key from update data to avoid conflict
            update_data = {
                "setting_value": json.dumps(fallback_chain),
                "description": f"AI provider fallback chain with {len(fallback_chain)} provider(s)"
            }
            logger.info("Updating existing setting")
            result = client.table("app_settings").update(update_data).eq("setting_key", "default_ai_provider").execute()
        else:
            # Insert new
            logger.info("Inserting new setting")
            result = client.table("app_settings").insert(setting_data).execute()
        
        logger.info(f"Default AI provider fallback chain updated by {admin['email']}: {json.dumps(fallback_chain)}")
        
        return JSONResponse({
            "success": True,
            "fallback_chain": fallback_chain,
            "message": f"Fallback chain updated with {len(fallback_chain)} provider(s)"
        })
    except Exception as e:
        logger.error(f"Error updating default AI provider: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating default AI provider: {str(e)}")


@router.get("/settings/available-providers")
async def get_available_providers(admin=Depends(get_current_admin)):
    """Get list of available AI providers based on configured API keys."""
    from config import settings
    
    available = []
    
    if settings.gemini_api_key:
        available.append({"name": "gemini", "display_name": "Google Gemini"})
    if settings.openai_api_key:
        available.append({"name": "openai", "display_name": "OpenAI"})
    if settings.anthropic_api_key:
        available.append({"name": "claude", "display_name": "Anthropic Claude"})
    if settings.kimi_api_key:
        available.append({"name": "kimi", "display_name": "Kimi K2"})
    if settings.minimax_api_key:
        available.append({"name": "minimax", "display_name": "MiniMax"})
    
    return JSONResponse({
        "providers": available,
        "total": len(available)
    })


@router.get("/settings/providers/{provider_name}/models")
async def list_provider_models(
    provider_name: str,
    admin=Depends(get_current_admin)
):
    """List available models for a specific provider with their token limits."""
    from services.ai.model_limits import get_max_output_tokens, get_context_window
    from config import settings
    import httpx
    
    models = []
    
    try:
        if provider_name == "gemini" and settings.gemini_api_key:
            import google.generativeai as genai
            genai.configure(api_key=settings.gemini_api_key)
            for model in genai.list_models():
                supported_methods = getattr(model, "supported_generation_methods", []) or []
                if "generateContent" in supported_methods:
                    model_id = model.name  # Keep full ID with "models/" prefix
                    display_name = model.name.replace("models/", "").replace("-", " ").title()
                    max_tokens = get_max_output_tokens(model_id)
                    context_window = get_context_window(model_id)
                    models.append({
                        "id": model_id,
                        "name": model_id.replace("models/", ""),
                        "display_name": display_name,
                        "max_output_tokens": max_tokens,
                        "context_window": context_window
                    })
        
        elif provider_name == "openai" and settings.openai_api_key:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.openai_api_key)
            response = await client.models.list()
            for model in response.data:
                if "gpt" in model.id.lower():
                    max_tokens = get_max_output_tokens(model.id)
                    context_window = get_context_window(model.id)
                    models.append({
                        "id": model.id,
                        "name": model.id,
                        "display_name": model.id.replace("-", " ").title(),
                        "max_output_tokens": max_tokens,
                        "context_window": context_window
                    })
        
        elif provider_name == "kimi" and settings.kimi_api_key:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://kimi-k2.ai/api/v1/models",
                    headers={
                        "Authorization": f"Bearer {settings.kimi_api_key}",
                        "Content-Type": "application/json"
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    for model in data.get("data", []):
                        model_id = model.get("id", "")
                        max_tokens = get_max_output_tokens(model_id)
                        context_window = get_context_window(model_id)
                        models.append({
                            "id": model_id,
                            "name": model_id,
                            "display_name": model_id.replace("-", " ").title(),
                            "max_output_tokens": max_tokens,
                            "context_window": context_window
                        })
        
        elif provider_name == "claude" and settings.anthropic_api_key:
            # Claude models are fixed list
            claude_models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-opus-20240229",
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307",
            ]
            for model_id in claude_models:
                max_tokens = get_max_output_tokens(model_id)
                context_window = get_context_window(model_id)
                models.append({
                    "id": model_id,
                    "name": model_id,
                    "display_name": model_id.replace("-", " ").title(),
                    "max_output_tokens": max_tokens,
                    "context_window": context_window
                })
        
        elif provider_name == "minimax" and settings.minimax_api_key:
            # MiniMax models are fixed list
            minimax_models = [
                "abab6.5-chat",
                "abab6.5s-chat",
            ]
            for model_id in minimax_models:
                max_tokens = get_max_output_tokens(model_id)
                context_window = get_context_window(model_id)
                models.append({
                    "id": model_id,
                    "name": model_id,
                    "display_name": model_id.replace(".", " ").replace("-", " ").title(),
                    "max_output_tokens": max_tokens,
                    "context_window": context_window
                })
        
        return JSONResponse({
            "provider": provider_name,
            "models": models,
            "total": len(models)
        })
        
    except Exception as e:
        logger.error(f"Error listing models for {provider_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error listing models for {provider_name}: {str(e)}"
        )


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
