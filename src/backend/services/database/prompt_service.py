"""
Prompt management database service.

This service handles all database operations for AI prompts, including:
- CRUD operations for prompts
- Version history management
- Prompt testing and evaluation
- Statistics and usage tracking
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from database import get_supabase_client
import logging
import json

logger = logging.getLogger(__name__)


class PromptService:
    """Service for managing AI prompts in the database."""
    
    def __init__(self):
        """Initialize the prompt service."""
        self.client = get_supabase_client()
    
    async def get_all_prompts(
        self,
        category: Optional[str] = None,
        is_active: Optional[bool] = None,
        language: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all prompts with optional filtering.
        
        Args:
            category: Filter by prompt category
            is_active: Filter by active status
            language: Filter by language code
            
        Returns:
            List of prompt dictionaries
        """
        try:
            query = self.client.table("ai_prompts").select("*")
            
            if category:
                query = query.eq("category", category)
            if is_active is not None:
                query = query.eq("is_active", is_active)
            if language:
                query = query.eq("language", language)
            
            # Order by category and name
            query = query.order("category").order("name")
            
            result = query.execute()
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching prompts: {e}")
            return []
    
    async def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single prompt by ID.
        
        Args:
            prompt_id: UUID of the prompt
            
        Returns:
            Prompt dictionary or None if not found
        """
        try:
            result = self.client.table("ai_prompts")\
                .select("*")\
                .eq("id", prompt_id)\
                .single()\
                .execute()
            
            return result.data if result.data else None
            
        except Exception as e:
            logger.error(f"Error fetching prompt {prompt_id}: {e}")
            return None
    
    async def get_prompt_by_key(
        self,
        prompt_key: str,
        language: str = "en",
        version: Optional[int] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get a prompt by its key.
        
        This is the main method used by the AI service to fetch prompts.
        
        Args:
            prompt_key: Unique key identifier (e.g., "cv_extraction")
            language: Language code (default: "en")
            version: Specific version number (optional, defaults to active default)
            
        Returns:
            Prompt dictionary or None if not found
        """
        try:
            query = self.client.table("ai_prompts")\
                .select("*")\
                .eq("prompt_key", prompt_key)\
                .eq("language", language)\
                .eq("is_active", True)
            
            if version:
                query = query.eq("version", version)
            else:
                # Get the default version for this key
                query = query.eq("is_default", True)
            
            result = query.execute()
            
            if result.data and len(result.data) > 0:
                # Update usage stats
                await self._increment_usage(result.data[0]["id"])
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching prompt by key {prompt_key}: {e}")
            return None
    
    async def create_prompt(
        self,
        prompt_key: str,
        name: str,
        content: str,
        category: str = "general",
        description: Optional[str] = None,
        variables: Optional[List[str]] = None,
        language: str = "en",
        model_preferences: Optional[Dict[str, Any]] = None,
        is_active: bool = True,
        is_default: bool = True,
        created_by: Optional[str] = None,
        admin_notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new prompt.
        
        Args:
            prompt_key: Unique identifier for the prompt
            name: Human-readable name
            content: The prompt template
            category: Prompt category
            description: Description of the prompt's purpose
            variables: List of variable names used in the prompt
            language: Language code
            model_preferences: Preferred AI model settings
            is_active: Whether this prompt is active
            is_default: Whether this is the default version for this key
            created_by: Admin username who created this
            admin_notes: Notes for admins
            
        Returns:
            Created prompt dictionary or None on error
        """
        try:
            prompt_data = {
                "prompt_key": prompt_key,
                "name": name,
                "content": content,
                "category": category,
                "description": description,
                "variables": json.dumps(variables or []),
                "language": language,
                "model_preferences": json.dumps(model_preferences or {}),
                "is_active": is_active,
                "is_default": is_default,
                "created_by": created_by,
                "admin_notes": admin_notes,
                "version": 1
            }
            
            result = self.client.table("ai_prompts")\
                .insert(prompt_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                prompt = result.data[0]
                
                # Create initial version history entry
                await self._create_version_history(
                    prompt_id=prompt["id"],
                    version=1,
                    content=content,
                    variables=variables or [],
                    model_preferences=model_preferences or {},
                    change_description="Initial version",
                    created_by=created_by
                )
                
                logger.info(f"Created new prompt: {prompt_key} (ID: {prompt['id']})")
                return prompt
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating prompt: {e}")
            return None
    
    async def update_prompt(
        self,
        prompt_id: str,
        content: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        variables: Optional[List[str]] = None,
        model_preferences: Optional[Dict[str, Any]] = None,
        is_active: Optional[bool] = None,
        is_default: Optional[bool] = None,
        admin_notes: Optional[str] = None,
        updated_by: Optional[str] = None,
        change_description: Optional[str] = None,
        create_new_version: bool = True
    ) -> Optional[Dict[str, Any]]:
        """
        Update an existing prompt.
        
        Args:
            prompt_id: UUID of the prompt to update
            content: New prompt content
            name: New name
            description: New description
            variables: New variables list
            model_preferences: New model preferences
            is_active: New active status
            is_default: New default status
            admin_notes: New admin notes
            updated_by: Admin username who updated this
            change_description: Description of what changed
            create_new_version: Whether to create a new version (default: True)
            
        Returns:
            Updated prompt dictionary or None on error
        """
        try:
            # Get current prompt
            current = await self.get_prompt_by_id(prompt_id)
            if not current:
                logger.error(f"Prompt {prompt_id} not found")
                return None
            
            # Build update data
            update_data = {"updated_by": updated_by}
            
            if name is not None:
                update_data["name"] = name
            if description is not None:
                update_data["description"] = description
            if variables is not None:
                update_data["variables"] = json.dumps(variables)
            if model_preferences is not None:
                update_data["model_preferences"] = json.dumps(model_preferences)
            if is_active is not None:
                update_data["is_active"] = is_active
            if is_default is not None:
                update_data["is_default"] = is_default
            if admin_notes is not None:
                update_data["admin_notes"] = admin_notes
            
            # If content changed and we want a new version
            if content is not None and create_new_version:
                new_version = current["version"] + 1
                update_data["content"] = content
                update_data["version"] = new_version
                
                # Create version history
                await self._create_version_history(
                    prompt_id=prompt_id,
                    version=new_version,
                    content=content,
                    variables=variables if variables is not None else json.loads(current.get("variables", "[]")),
                    model_preferences=model_preferences if model_preferences is not None else json.loads(current.get("model_preferences", "{}")),
                    change_description=change_description or "Updated prompt",
                    created_by=updated_by
                )
            elif content is not None:
                update_data["content"] = content
            
            # Update the prompt
            result = self.client.table("ai_prompts")\
                .update(update_data)\
                .eq("id", prompt_id)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Updated prompt {prompt_id}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error updating prompt {prompt_id}: {e}")
            return None
    
    async def delete_prompt(self, prompt_id: str) -> bool:
        """
        Delete a prompt (soft delete - set to inactive).
        
        Args:
            prompt_id: UUID of the prompt to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Soft delete: just set to inactive
            result = self.client.table("ai_prompts")\
                .update({"is_active": False})\
                .eq("id", prompt_id)\
                .execute()
            
            success = result.data is not None and len(result.data) > 0
            if success:
                logger.info(f"Deactivated prompt {prompt_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error deleting prompt {prompt_id}: {e}")
            return False
    
    async def get_prompt_versions(self, prompt_id: str) -> List[Dict[str, Any]]:
        """
        Get all version history for a prompt.
        
        Args:
            prompt_id: UUID of the prompt
            
        Returns:
            List of version dictionaries, ordered by version descending
        """
        try:
            result = self.client.table("prompt_versions")\
                .select("*")\
                .eq("prompt_id", prompt_id)\
                .order("version", desc=True)\
                .execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"Error fetching versions for prompt {prompt_id}: {e}")
            return []
    
    async def rollback_to_version(
        self,
        prompt_id: str,
        version: int,
        updated_by: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Rollback a prompt to a previous version.
        
        Args:
            prompt_id: UUID of the prompt
            version: Version number to rollback to
            updated_by: Admin username performing the rollback
            
        Returns:
            Updated prompt or None on error
        """
        try:
            # Get the version
            version_result = self.client.table("prompt_versions")\
                .select("*")\
                .eq("prompt_id", prompt_id)\
                .eq("version", version)\
                .single()\
                .execute()
            
            if not version_result.data:
                logger.error(f"Version {version} not found for prompt {prompt_id}")
                return None
            
            version_data = version_result.data
            
            # Update the prompt with this version's data
            return await self.update_prompt(
                prompt_id=prompt_id,
                content=version_data["content"],
                variables=json.loads(version_data.get("variables", "[]")),
                model_preferences=json.loads(version_data.get("model_preferences", "{}")),
                updated_by=updated_by,
                change_description=f"Rolled back to version {version}",
                create_new_version=True
            )
            
        except Exception as e:
            logger.error(f"Error rolling back prompt {prompt_id} to version {version}: {e}")
            return None
    
    async def get_prompt_stats(self) -> Dict[str, Any]:
        """
        Get statistics about prompts.
        
        Returns:
            Dictionary with stats (total, by category, etc.)
        """
        try:
            all_prompts = await self.get_all_prompts()
            active_prompts = [p for p in all_prompts if p.get("is_active")]
            
            categories = {}
            for prompt in all_prompts:
                cat = prompt.get("category", "general")
                categories[cat] = categories.get(cat, 0) + 1
            
            return {
                "total": len(all_prompts),
                "active": len(active_prompts),
                "inactive": len(all_prompts) - len(active_prompts),
                "by_category": categories,
                "most_used": sorted(
                    active_prompts,
                    key=lambda p: p.get("usage_count", 0),
                    reverse=True
                )[:5]
            }
            
        except Exception as e:
            logger.error(f"Error getting prompt stats: {e}")
            return {"total": 0, "active": 0, "inactive": 0, "by_category": {}}
    
    async def _increment_usage(self, prompt_id: str) -> None:
        """
        Increment usage counter for a prompt.
        
        Args:
            prompt_id: UUID of the prompt
        """
        try:
            self.client.rpc(
                "increment_prompt_usage",
                {"prompt_id": prompt_id}
            ).execute()
        except Exception:
            # Non-critical - just update the fields directly
            try:
                self.client.table("ai_prompts")\
                    .update({
                        "usage_count": self.client.table("ai_prompts").select("usage_count").eq("id", prompt_id).single().execute().data["usage_count"] + 1,
                        "last_used_at": datetime.utcnow().isoformat()
                    })\
                    .eq("id", prompt_id)\
                    .execute()
            except Exception:
                pass  # Non-critical, ignore
    
    async def _create_version_history(
        self,
        prompt_id: str,
        version: int,
        content: str,
        variables: List[str],
        model_preferences: Dict[str, Any],
        change_description: str,
        created_by: Optional[str] = None
    ) -> None:
        """
        Create a version history entry.
        
        Args:
            prompt_id: UUID of the prompt
            version: Version number
            content: Prompt content at this version
            variables: Variables at this version
            model_preferences: Model preferences at this version
            change_description: Description of changes
            created_by: Admin who made the change
        """
        try:
            self.client.table("prompt_versions")\
                .insert({
                    "prompt_id": prompt_id,
                    "version": version,
                    "content": content,
                    "variables": json.dumps(variables),
                    "model_preferences": json.dumps(model_preferences),
                    "change_description": change_description,
                    "created_by": created_by
                })\
                .execute()
            
            logger.debug(f"Created version {version} for prompt {prompt_id}")
            
        except Exception as e:
            logger.warning(f"Failed to create version history: {e}")


# Global instance
_prompt_service = None


def get_prompt_service() -> PromptService:
    """
    Get the global prompt service instance.
    
    Returns:
        PromptService instance
    """
    global _prompt_service
    if _prompt_service is None:
        _prompt_service = PromptService()
    return _prompt_service

