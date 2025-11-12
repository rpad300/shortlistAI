"""
Interviewer database service.

Handles CRUD operations for interviewers table.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class InterviewerService:
    """Service for managing interviewers in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "interviewers"
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """
        Find interviewer by email.
        
        Args:
            email: Interviewer email address
            
        Returns:
            Interviewer dict if found, None otherwise
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("email", email.lower())\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Found existing interviewer: {email}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding interviewer by email: {e}")
            return None
    
    async def create(
        self,
        email: str,
        name: str,
        company_id: Optional[UUID] = None,
        phone: Optional[str] = None,
        country: Optional[str] = None,
        consent_given: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new interviewer.
        
        Args:
            email: Interviewer email
            name: Interviewer full name
            company_id: Optional company UUID
            phone: Optional phone number
            country: Optional country
            consent_given: Whether consent was given
            
        Returns:
            Created interviewer dict or None if failed
        """
        try:
            interviewer_data = {
                "email": email.lower(),
                "name": name,
                "company_id": str(company_id) if company_id else None,
                "phone": phone,
                "country": country,
                "consent_given": consent_given,
                "consent_timestamp": datetime.utcnow().isoformat() if consent_given else None
            }
            
            result = self.client.table(self.table)\
                .insert(interviewer_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created new interviewer: {email}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating interviewer: {e}")
            return None
    
    async def find_or_create(
        self,
        email: str,
        name: str,
        company_id: Optional[UUID] = None,
        phone: Optional[str] = None,
        country: Optional[str] = None,
        consent_given: bool = False
    ) -> Optional[Dict[str, Any]]:
        """
        Find existing interviewer or create new one.
        
        Args:
            email: Interviewer email
            name: Interviewer name
            company_id: Optional company UUID
            phone: Optional phone
            country: Optional country
            consent_given: Whether consent was given
            
        Returns:
            Existing or newly created interviewer dict
        """
        # Try to find existing
        existing = await self.find_by_email(email)
        if existing:
            # Update consent if needed
            if not existing.get("consent_given") and consent_given:
                await self.update_consent(existing["id"], consent_given=True)
                existing["consent_given"] = True
            
            return existing
        
        # Create new
        return await self.create(
            email=email,
            name=name,
            company_id=company_id,
            phone=phone,
            country=country,
            consent_given=consent_given
        )
    
    async def update_consent(
        self,
        interviewer_id: UUID,
        consent_given: bool
    ) -> bool:
        """
        Update interviewer consent status.
        
        Args:
            interviewer_id: Interviewer UUID
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
                .eq("id", str(interviewer_id))\
                .execute()
            
            logger.info(f"Updated consent for interviewer: {interviewer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating interviewer consent: {e}")
            return False
    
    async def get_by_id(self, interviewer_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get interviewer by ID.
        
        Args:
            interviewer_id: Interviewer UUID
            
        Returns:
            Interviewer dict or None
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(interviewer_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting interviewer by ID: {e}")
            return None
    
    async def list_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all interviewers (for Admin use).
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of interviewer dicts
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .order("created_at", desc=True)\
                .range(offset, offset + limit - 1)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing interviewers: {e}")
            return []


# Global service instance
_interviewer_service: Optional[InterviewerService] = None


def get_interviewer_service() -> InterviewerService:
    """Get global interviewer service instance."""
    global _interviewer_service
    if _interviewer_service is None:
        _interviewer_service = InterviewerService()
    return _interviewer_service

