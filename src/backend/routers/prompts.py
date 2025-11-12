"""
Admin API endpoints for AI Prompt management.

This router provides CRUD operations for managing AI prompts
through the Admin interface.
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Header
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from services.database.prompt_service import get_prompt_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/admin/prompts", tags=["Admin - Prompts"])


# ============================================================================
# Auth Helper
# ============================================================================

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
            "username": user_metadata.get("username", user.email)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token verification error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


# ============================================================================
# Request/Response Models
# ============================================================================

class PromptCreate(BaseModel):
    """Request model for creating a new prompt."""
    prompt_key: str = Field(..., description="Unique identifier for the prompt")
    name: str = Field(..., description="Human-readable name")
    content: str = Field(..., description="The prompt template")
    category: str = Field(default="general", description="Prompt category")
    description: Optional[str] = Field(None, description="Description of the prompt")
    variables: Optional[List[str]] = Field(default=[], description="Variable names used in the prompt")
    language: str = Field(default="en", description="Language code")
    model_preferences: Optional[Dict[str, Any]] = Field(default={}, description="AI model preferences")
    is_active: bool = Field(default=True, description="Is this prompt active?")
    is_default: bool = Field(default=True, description="Is this the default version?")
    admin_notes: Optional[str] = Field(None, description="Notes for admins")


class PromptUpdate(BaseModel):
    """Request model for updating a prompt."""
    content: Optional[str] = Field(None, description="New prompt content")
    name: Optional[str] = Field(None, description="New name")
    description: Optional[str] = Field(None, description="New description")
    variables: Optional[List[str]] = Field(None, description="New variables")
    model_preferences: Optional[Dict[str, Any]] = Field(None, description="New model preferences")
    is_active: Optional[bool] = Field(None, description="New active status")
    is_default: Optional[bool] = Field(None, description="New default status")
    admin_notes: Optional[str] = Field(None, description="New admin notes")
    change_description: Optional[str] = Field(None, description="Description of changes")
    create_new_version: bool = Field(default=True, description="Create a new version?")


class PromptResponse(BaseModel):
    """Response model for a prompt."""
    id: str
    prompt_key: str
    name: str
    content: str
    category: str
    description: Optional[str]
    variables: List[str]
    language: str
    model_preferences: Dict[str, Any]
    version: int
    is_active: bool
    is_default: bool
    usage_count: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    updated_by: Optional[str]
    admin_notes: Optional[str]


class PromptListResponse(BaseModel):
    """Response model for list of prompts."""
    prompts: List[Dict[str, Any]]
    total: int


class PromptStatsResponse(BaseModel):
    """Response model for prompt statistics."""
    total: int
    active: int
    inactive: int
    by_category: Dict[str, int]
    most_used: List[Dict[str, Any]]


class VersionResponse(BaseModel):
    """Response model for a prompt version."""
    id: str
    prompt_id: str
    version: int
    content: str
    variables: List[str]
    model_preferences: Dict[str, Any]
    change_description: Optional[str]
    created_at: datetime
    created_by: Optional[str]


# ============================================================================
# Endpoints
# ============================================================================

@router.get("/", response_model=PromptListResponse)
async def list_prompts(
    category: Optional[str] = None,
    is_active: Optional[bool] = None,
    language: Optional[str] = None,
    admin: dict = Depends(get_current_admin)
):
    """
    Get all prompts with optional filtering.
    
    - **category**: Filter by category
    - **is_active**: Filter by active status
    - **language**: Filter by language code
    
    Returns list of all prompts matching the filters.
    """
    try:
        service = get_prompt_service()
        prompts = await service.get_all_prompts(
            category=category,
            is_active=is_active,
            language=language
        )
        
        return {
            "prompts": prompts,
            "total": len(prompts)
        }
        
    except Exception as e:
        logger.error(f"Error listing prompts: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prompts")


@router.get("/stats", response_model=PromptStatsResponse)
async def get_prompt_stats(admin: dict = Depends(get_current_admin)):
    """
    Get statistics about prompts.
    
    Returns:
    - Total count
    - Active/inactive counts
    - Counts by category
    - Most used prompts
    """
    try:
        service = get_prompt_service()
        stats = await service.get_prompt_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting prompt stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get prompt statistics")


@router.get("/{prompt_id}")
async def get_prompt(
    prompt_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Get a single prompt by ID.
    
    Returns the full prompt details including all metadata.
    """
    try:
        service = get_prompt_service()
        prompt = await service.get_prompt_by_id(prompt_id)
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt not found")
        
        return prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prompt")


@router.post("/", status_code=201)
async def create_prompt(
    prompt: PromptCreate,
    admin: dict = Depends(get_current_admin)
):
    """
    Create a new prompt.
    
    The prompt_key must be unique. This creates version 1 of the prompt.
    """
    try:
        service = get_prompt_service()
        
        # Check if prompt_key already exists
        existing = await service.get_prompt_by_key(prompt.prompt_key, prompt.language)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Prompt with key '{prompt.prompt_key}' already exists for language '{prompt.language}'"
            )
        
        created = await service.create_prompt(
            prompt_key=prompt.prompt_key,
            name=prompt.name,
            content=prompt.content,
            category=prompt.category,
            description=prompt.description,
            variables=prompt.variables,
            language=prompt.language,
            model_preferences=prompt.model_preferences,
            is_active=prompt.is_active,
            is_default=prompt.is_default,
            created_by=admin.get("username"),
            admin_notes=prompt.admin_notes
        )
        
        if not created:
            raise HTTPException(status_code=500, detail="Failed to create prompt")
        
        return created
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating prompt: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{prompt_id}")
async def update_prompt(
    prompt_id: str,
    update: PromptUpdate,
    admin: dict = Depends(get_current_admin)
):
    """
    Update an existing prompt.
    
    By default, content changes create a new version. Set create_new_version=false
    to update the current version in place.
    """
    try:
        service = get_prompt_service()
        
        updated = await service.update_prompt(
            prompt_id=prompt_id,
            content=update.content,
            name=update.name,
            description=update.description,
            variables=update.variables,
            model_preferences=update.model_preferences,
            is_active=update.is_active,
            is_default=update.is_default,
            admin_notes=update.admin_notes,
            updated_by=admin.get("username"),
            change_description=update.change_description,
            create_new_version=update.create_new_version
        )
        
        if not updated:
            raise HTTPException(status_code=404, detail="Prompt not found or update failed")
        
        return updated
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Delete a prompt (soft delete - sets is_active to false).
    
    The prompt is not permanently deleted, just deactivated.
    """
    try:
        service = get_prompt_service()
        success = await service.delete_prompt(prompt_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Prompt not found or already deleted")
        
        return {"message": "Prompt deactivated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete prompt")


@router.get("/{prompt_id}/versions")
async def get_prompt_versions(
    prompt_id: str,
    admin: dict = Depends(get_current_admin)
):
    """
    Get all version history for a prompt.
    
    Returns versions in descending order (newest first).
    """
    try:
        service = get_prompt_service()
        versions = await service.get_prompt_versions(prompt_id)
        
        return {
            "versions": versions,
            "total": len(versions)
        }
        
    except Exception as e:
        logger.error(f"Error getting versions for prompt {prompt_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch versions")


@router.post("/{prompt_id}/rollback/{version}")
async def rollback_prompt(
    prompt_id: str,
    version: int,
    admin: dict = Depends(get_current_admin)
):
    """
    Rollback a prompt to a previous version.
    
    This creates a new version with the content from the specified version.
    """
    try:
        service = get_prompt_service()
        
        updated = await service.rollback_to_version(
            prompt_id=prompt_id,
            version=version,
            updated_by=admin.get("username")
        )
        
        if not updated:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt or version {version} not found"
            )
        
        return {
            "message": f"Rolled back to version {version}",
            "prompt": updated
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rolling back prompt {prompt_id} to version {version}: {e}")
        raise HTTPException(status_code=500, detail="Failed to rollback")


@router.get("/key/{prompt_key}")
async def get_prompt_by_key(
    prompt_key: str,
    language: str = "en",
    version: Optional[int] = None,
    admin: dict = Depends(get_current_admin)
):
    """
    Get a prompt by its key.
    
    - **prompt_key**: The unique key identifier
    - **language**: Language code (default: en)
    - **version**: Specific version number (optional, defaults to active default)
    
    This is useful for testing and viewing prompts by their key.
    """
    try:
        service = get_prompt_service()
        prompt = await service.get_prompt_by_key(
            prompt_key=prompt_key,
            language=language,
            version=version
        )
        
        if not prompt:
            raise HTTPException(
                status_code=404,
                detail=f"Prompt with key '{prompt_key}' not found for language '{language}'"
            )
        
        return prompt
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting prompt by key {prompt_key}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prompt")


@router.get("/categories/list")
async def list_categories(admin: dict = Depends(get_current_admin)):
    """
    Get list of all prompt categories in use.
    
    Returns unique categories from all prompts.
    """
    try:
        service = get_prompt_service()
        prompts = await service.get_all_prompts()
        
        categories = sorted(list(set(p.get("category", "general") for p in prompts)))
        
        return {
            "categories": categories,
            "total": len(categories)
        }
        
    except Exception as e:
        logger.error(f"Error listing categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch categories")

