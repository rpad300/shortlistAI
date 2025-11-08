"""
Company database service.

Handles CRUD operations for companies table.
"""

from typing import Optional, Dict, Any
from uuid import UUID
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class CompanyService:
    """Service for managing companies in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "companies"
    
    async def find_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find company by name (case-insensitive).
        
        Args:
            name: Company name
            
        Returns:
            Company dict if found, None otherwise
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .ilike("name", name)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Found existing company: {name}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error finding company by name: {e}")
            return None
    
    async def create(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Create a new company.
        
        Args:
            name: Company name
            
        Returns:
            Created company dict or None if failed
        """
        try:
            company_data = {"name": name.strip()}
            
            result = self.client.table(self.table)\
                .insert(company_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created new company: {name}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating company: {e}")
            return None
    
    async def find_or_create(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Find existing company or create new one.
        
        Args:
            name: Company name
            
        Returns:
            Existing or newly created company dict
        """
        if not name or not name.strip():
            return None
        
        # Try to find existing
        existing = await self.find_by_name(name)
        if existing:
            return existing
        
        # Create new
        return await self.create(name)
    
    async def get_by_id(self, company_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get company by ID.
        
        Args:
            company_id: Company UUID
            
        Returns:
            Company dict or None
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(company_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting company by ID: {e}")
            return None


# Global service instance
_company_service: Optional[CompanyService] = None


def get_company_service() -> CompanyService:
    """Get global company service instance."""
    global _company_service
    if _company_service is None:
        _company_service = CompanyService()
    return _company_service

