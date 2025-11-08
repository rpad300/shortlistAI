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
            
            result = self.client.table(self.table)\
                .insert(candidate_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created new candidate: {email}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating candidate: {e}")
            return None
    
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

