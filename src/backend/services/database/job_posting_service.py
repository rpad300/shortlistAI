"""
Job Posting database service.

Handles CRUD operations for job_postings table.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class JobPostingService:
    """Service for managing job postings in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "job_postings"
    
    async def create(
        self,
        raw_text: str,
        company_id: Optional[UUID] = None,
        interviewer_id: Optional[UUID] = None,
        candidate_id: Optional[UUID] = None,
        file_url: Optional[str] = None,
        key_points: Optional[str] = None,
        weights: Optional[Dict[str, Any]] = None,
        hard_blockers: Optional[Dict[str, Any]] = None,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new job posting.
        
        Args:
            raw_text: Job posting text
            company_id: Optional company UUID
            interviewer_id: Optional interviewer UUID (for interviewer flow)
            candidate_id: Optional candidate UUID (for candidate flow)
            file_url: Optional URL to uploaded file
            key_points: Optional key points text
            weights: Optional category weights
            hard_blockers: Optional hard blocker rules
            language: Language of the posting
            
        Returns:
            Created job posting dict or None if failed
            
        Raises:
            ValueError: If constraints are violated (e.g., both interviewer_id and candidate_id are None)
        """
        # Validate constraint: must have either interviewer_id OR candidate_id, not both, not none
        if not interviewer_id and not candidate_id:
            error_msg = "Job posting must have either interviewer_id or candidate_id, but both are None"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        if interviewer_id and candidate_id:
            error_msg = "Job posting cannot have both interviewer_id and candidate_id"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Validate raw_text
        if not raw_text or not raw_text.strip():
            error_msg = "Job posting raw_text cannot be empty"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        try:
            job_data = {
                "raw_text": raw_text.strip(),
                "company_id": str(company_id) if company_id else None,
                "interviewer_id": str(interviewer_id) if interviewer_id else None,
                "candidate_id": str(candidate_id) if candidate_id else None,
                "file_url": file_url,
                "key_points": key_points,
                "weights": weights,
                "hard_blockers": hard_blockers,
                "language": language or "en"
            }
            
            logger.info(
                f"Attempting to create job posting: "
                f"raw_text_length={len(job_data['raw_text'])}, "
                f"company_id={job_data['company_id']}, "
                f"interviewer_id={job_data['interviewer_id']}, "
                f"candidate_id={job_data['candidate_id']}, "
                f"language={job_data['language']}"
            )
            
            result = self.client.table(self.table)\
                .insert(job_data)\
                .execute()
            
            # Check for errors in response
            if hasattr(result, 'error') and result.error:
                logger.error(f"Supabase error creating job posting: {result.error}")
                return None
            
            if result.data and len(result.data) > 0:
                logger.info(f"Successfully created job posting: {result.data[0]['id']}")
                return result.data[0]
            
            logger.warning("Insert succeeded but no data returned from Supabase")
            return None
            
        except ValueError:
            # Re-raise validation errors
            raise
        except Exception as e:
            logger.error(
                f"Exception creating job posting: {type(e).__name__}: {e}",
                exc_info=True
            )
            return None
    
    async def get_by_id(self, job_posting_id: UUID) -> Optional[Dict[str, Any]]:
        """Get job posting by ID."""
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(job_posting_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting job posting: {e}")
            return None
    
    async def update_structured_data(
        self,
        job_posting_id: UUID,
        structured_data: Dict[str, Any]
    ) -> bool:
        """
        Update job posting with AI-extracted structured data.
        
        Args:
            job_posting_id: Job posting UUID
            structured_data: Extracted structured representation
            
        Returns:
            True if updated successfully
        """
        try:
            result = self.client.table(self.table)\
                .update({"structured_data": structured_data})\
                .eq("id", str(job_posting_id))\
                .execute()
            
            logger.info(f"Updated structured data for job posting: {job_posting_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating job posting structured data: {e}")
            return False
    
    async def update_key_points(
        self,
        job_posting_id: UUID,
        key_points: str
    ) -> bool:
        """Update job posting key points."""
        try:
            result = self.client.table(self.table)\
                .update({"key_points": key_points})\
                .eq("id", str(job_posting_id))\
                .execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating key points: {e}")
            return False
    
    async def update_weights_and_blockers(
        self,
        job_posting_id: UUID,
        weights: Dict[str, Any],
        hard_blockers: Dict[str, Any]
    ) -> bool:
        """Update job posting weights and hard blockers."""
        try:
            result = self.client.table(self.table)\
                .update({
                    "weights": weights,
                    "hard_blockers": hard_blockers
                })\
                .eq("id", str(job_posting_id))\
                .execute()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating weights and blockers: {e}")
            return False
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all job postings (for Admin use).
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of job posting dicts
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing job postings: {e}")
            return []
    
    async def count_all(self) -> int:
        """Count total number of job postings."""
        try:
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error counting job postings: {e}")
            return 0
    
    async def count_recent(self, days: int = 30) -> int:
        """Count job postings created in the last N days."""
        try:
            from datetime import datetime, timedelta
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .gte("created_at", cutoff)\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error counting recent job postings: {e}")
            return 0


# Global service instance
_job_posting_service: Optional[JobPostingService] = None


def get_job_posting_service() -> JobPostingService:
    """Get global job posting service instance."""
    global _job_posting_service
    if _job_posting_service is None:
        _job_posting_service = JobPostingService()
    return _job_posting_service

