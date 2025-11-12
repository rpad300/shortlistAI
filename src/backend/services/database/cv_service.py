"""
CV database service.

Handles CRUD operations for CVs table with versioning support.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class CVService:
    """Service for managing CVs in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "cvs"
    
    async def get_next_version(self, candidate_id: UUID) -> int:
        """
        Get next version number for candidate's CVs.
        
        Args:
            candidate_id: Candidate UUID
            
        Returns:
            Next version number (1 if no CVs exist)
        """
        try:
            result = self.client.table(self.table)\
                .select("version")\
                .eq("candidate_id", str(candidate_id))\
                .order("version", desc=True)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["version"] + 1
            
            return 1
            
        except Exception as e:
            logger.error(f"Error getting next CV version: {e}")
            return 1
    
    async def create(
        self,
        candidate_id: UUID,
        file_url: str,
        uploaded_by_flow: str,
        extracted_text: Optional[str] = None,
        structured_data: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new CV record.
        
        Args:
            candidate_id: Candidate UUID
            file_url: URL to CV file in storage
            uploaded_by_flow: 'interviewer' or 'candidate'
            extracted_text: Optional extracted text
            structured_data: Optional AI-extracted structured data
            language: Optional detected language
            
        Returns:
            Created CV dict or None if failed
        """
        try:
            # Get next version number
            version = await self.get_next_version(candidate_id)
            
            cv_data = {
                "candidate_id": str(candidate_id),
                "file_url": file_url,
                "extracted_text": extracted_text,
                "structured_data": structured_data,
                "language": language,
                "version": version,
                "uploaded_by_flow": uploaded_by_flow
            }
            
            result = self.client.table(self.table)\
                .insert(cv_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created CV version {version} for candidate: {candidate_id}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating CV: {e}")
            return None
    
    async def get_by_id(self, cv_id: UUID) -> Optional[Dict[str, Any]]:
        """Get CV by ID."""
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(cv_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting CV: {e}")
            return None
    
    async def get_by_candidate(
        self,
        candidate_id: UUID,
        latest_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get all CVs for a candidate.
        
        Args:
            candidate_id: Candidate UUID
            latest_only: If True, return only the latest version
            
        Returns:
            List of CV dicts
        """
        try:
            query = self.client.table(self.table)\
                .select("*")\
                .eq("candidate_id", str(candidate_id))\
                .order("version", desc=True)
            
            if latest_only:
                query = query.limit(1)
            
            result = query.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting CVs for candidate: {e}")
            return []
    
    async def update_extracted_data(
        self,
        cv_id: UUID,
        extracted_text: str,
        structured_data: Optional[Dict[str, Any]] = None,
        language: Optional[str] = None
    ) -> bool:
        """
        Update CV with extracted text and structured data.
        
        Args:
            cv_id: CV UUID
            extracted_text: Extracted text from file
            structured_data: AI-extracted structured data
            language: Detected language
            
        Returns:
            True if updated successfully
        """
        try:
            update_data = {
                "extracted_text": extracted_text,
                "structured_data": structured_data,
                "language": language
            }
            
            result = self.client.table(self.table)\
                .update(update_data)\
                .eq("id", str(cv_id))\
                .execute()
            
            logger.info(f"Updated extracted data for CV: {cv_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating CV extracted data: {e}")
            return False
    
    async def count_all(self) -> int:
        """Count total number of CVs."""
        try:
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error counting CVs: {e}")
            return 0


# Global service instance
_cv_service: Optional[CVService] = None


def get_cv_service() -> CVService:
    """Get global CV service instance."""
    global _cv_service
    if _cv_service is None:
        _cv_service = CVService()
    return _cv_service

