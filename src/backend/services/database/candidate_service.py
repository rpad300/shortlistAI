"""
Candidate database service.

Handles all CRUD operations for candidates table with deduplication logic.
"""

from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class CandidateService:
    """
    Service for managing candidates in the database.
    
    Key responsibilities:
    - Create new candidates
    - Find existing candidates by email (deduplication)
    - Update candidate information
    - Link candidates to CVs and analyses
    """
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "candidates"
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find candidate by email address.
        
        Email is the primary deduplication key for candidates.
        
        Args:
            email: Candidate email address
            
        Returns:
            Candidate dict if found, None otherwise
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("email", email.lower())\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Found existing candidate: {email}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding candidate by email: {e}")
            return None
    
    async def create(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        country: Optional[str] = None,
        consent_given: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new candidate.
        
        Args:
            email: Candidate email (will be lowercased)
            name: Candidate full name
            phone: Optional phone number
            country: Optional country
            consent_given: Whether candidate gave consent
            
        Returns:
            Created candidate dict or None if failed
        """
        try:
            candidate_data = {
                "email": email.lower(),
                "name": name,
                "phone": phone,
                "country": country,
                "consent_given": consent_given,
                "consent_timestamp": datetime.utcnow().isoformat() if consent_given else None
            }
            
            logger.info(f"Attempting to create candidate: email={email}, name={name}")
            
            result = self.client.table(self.table)\
                .insert(candidate_data)\
                .execute()
            
            # Check for errors in response
            if hasattr(result, 'error') and result.error:
                error_msg = f"Supabase error creating candidate: {result.error}"
                logger.error(error_msg)
                # Log detailed error information
                if hasattr(result.error, 'message'):
                    logger.error(f"Supabase error message: {result.error.message}")
                if hasattr(result.error, 'details'):
                    logger.error(f"Supabase error details: {result.error.details}")
                if hasattr(result.error, 'hint'):
                    logger.error(f"Supabase error hint: {result.error.hint}")
                if hasattr(result.error, 'code'):
                    logger.error(f"Supabase error code: {result.error.code}")
                # Raise exception instead of returning None
                raise Exception(f"Database error creating candidate: {result.error}")
            
            # Check if result has data
            if not result.data:
                error_msg = "Insert succeeded but no data returned from Supabase"
                logger.warning(error_msg)
                raise Exception(error_msg)
            
            if len(result.data) > 0:
                logger.info(f"Created new candidate: {email} (id: {result.data[0]['id']})")
                return result.data[0]
            
            error_msg = "Insert succeeded but result.data is empty"
            logger.warning(error_msg)
            raise Exception(error_msg)
            
        except Exception as e:
            logger.error(
                f"Exception creating candidate: {type(e).__name__}: {e}",
                exc_info=True
            )
            # Re-raise exception so router can handle it properly
            raise
    
    async def find_or_create(
        self,
        email: str,
        name: str,
        phone: Optional[str] = None,
        country: Optional[str] = None,
        consent_given: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Find existing candidate by email or create new one.
        
        This is the main method for candidate deduplication.
        
        Args:
            email: Candidate email
            name: Candidate name
            phone: Optional phone
            country: Optional country
            consent_given: Whether consent was given
            
        Returns:
            Existing or newly created candidate dict
        """
        # Try to find existing
        existing = await self.find_by_email(email)
        if existing:
            # Update consent if it wasn't given before but is now
            if not existing.get("consent_given") and consent_given:
                await self.update_consent(existing["id"], consent_given=True)
                existing["consent_given"] = True
                existing["consent_timestamp"] = datetime.utcnow().isoformat()
            
            return existing
        
        # Create new
        return await self.create(
            email=email,
            name=name,
            phone=phone,
            country=country,
            consent_given=consent_given
        )
    
    async def update_consent(
        self,
        candidate_id: UUID,
        consent_given: bool
    ) -> bool:
        """
        Update candidate consent status.
        
        Args:
            candidate_id: Candidate UUID
            consent_given: New consent status
            
        Returns:
            True if updated successfully
        """
        try:
            update_data = {
                "consent_given": consent_given,
                "consent_timestamp": datetime.utcnow().isoformat() if consent_given else None
            }
            
            result = self.client.table(self.table)\
                .update(update_data)\
                .eq("id", str(candidate_id))\
                .execute()
            
            logger.info(f"Updated consent for candidate: {candidate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating candidate consent: {e}")
            return False
    
    async def get_by_id(self, candidate_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get candidate by ID.
        
        Args:
            candidate_id: Candidate UUID
            
        Returns:
            Candidate dict or None
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(candidate_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting candidate by ID: {e}")
            return None
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all candidates (for Admin use).
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of candidate dicts
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing candidates: {e}")
            return []
    
    async def get_cvs_by_candidate(self, candidate_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all CVs for a specific candidate.
        
        Args:
            candidate_id: Candidate UUID
            
        Returns:
            List of CV dicts for the candidate
        """
        try:
            result = self.client.table("cvs")\
                .select("*")\
                .eq("candidate_id", str(candidate_id))\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting CVs for candidate: {e}")
            return []
    
    async def get_analyses_by_candidate(self, candidate_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all analyses for a specific candidate.
        
        Args:
            candidate_id: Candidate UUID
            
        Returns:
            List of analysis dicts for the candidate
        """
        try:
            result = self.client.table("analyses")\
                .select("*")\
                .eq("candidate_id", str(candidate_id))\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting analyses for candidate: {e}")
            return []
    
    async def count_all(self) -> int:
        """
        Count total number of candidates.
        
        Returns:
            Total count of candidates
        """
        try:
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Error counting candidates: {e}")
            return 0
    
    async def count_recent(self, days: int = 30) -> int:
        """
        Count candidates created in the last N days.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Count of recent candidates
        """
        try:
            from datetime import datetime, timedelta
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .gte("created_at", cutoff)\
                .execute()
            
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Error counting recent candidates: {e}")
            return 0


# Global service instance
_candidate_service: Optional[CandidateService] = None


def get_candidate_service() -> CandidateService:
    """
    Get global candidate service instance.
    
    Returns:
        CandidateService singleton
    """
    global _candidate_service
    if _candidate_service is None:
        _candidate_service = CandidateService()
    return _candidate_service

