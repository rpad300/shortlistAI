"""
Enrichment database service.

Manages caching and retrieval of enriched company and candidate data.
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from uuid import UUID

from database.connection import get_supabase_client

logger = logging.getLogger(__name__)


class CompanyEnrichmentService:
    """
    Service for managing company enrichment data in the database.
    
    Handles caching, retrieval, and invalidation of enriched company data.
    """
    
    def __init__(self):
        """Initialize the service with database client."""
        self.client = get_supabase_client()
        self.table = "company_enrichments"
    
    async def get_latest(
        self,
        company_name: str,
        max_age_days: int = 7,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest valid enrichment for a company.
        
        Args:
            company_name: Name of the company
            max_age_days: Maximum age of cached data in days (default: 7)
        
        Returns:
            Latest enrichment data or None if not found or too old
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            response = (
                self.client.table(self.table)
                .select("*")
                .ilike("company_name", company_name)
                .eq("is_valid", True)
                .gte("enriched_at", cutoff_date.isoformat())
                .order("enriched_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                logger.info(f"Found cached enrichment for company: {company_name}")
                return response.data[0]
            
            logger.info(f"No recent enrichment found for company: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching company enrichment: {str(e)}")
            return None
    
    async def save(
        self,
        company_name: str,
        enrichment_data: Dict[str, Any],
        company_id: Optional[UUID] = None,
        expires_in_days: int = 30,
    ) -> Optional[Dict[str, Any]]:
        """
        Save company enrichment data to cache.
        
        Args:
            company_name: Name of the company
            enrichment_data: Enriched data from Brave Search
            company_id: Optional UUID of company in database
            expires_in_days: Days until cache expires (default: 30)
        
        Returns:
            Saved enrichment record or None if failed
        """
        try:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            record = {
                "company_id": str(company_id) if company_id else None,
                "company_name": company_name,
                "website": enrichment_data.get("website"),
                "description": enrichment_data.get("description"),
                "industry": enrichment_data.get("industry"),
                "company_size": enrichment_data.get("size"),
                "location": enrichment_data.get("location"),
                "social_media": enrichment_data.get("social_media", {}),
                "recent_news": enrichment_data.get("recent_news", []),
                "raw_results": [
                    result.dict() if hasattr(result, "dict") else result
                    for result in enrichment_data.get("raw_results", [])
                ],
                "search_query": company_name,
                "result_count": len(enrichment_data.get("raw_results", [])),
                "enriched_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "is_valid": True,
            }
            
            response = (
                self.client.table(self.table)
                .insert(record)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                logger.info(f"Saved enrichment for company: {company_name}")
                return response.data[0]
            
            logger.warning(f"Failed to save enrichment for company: {company_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error saving company enrichment: {str(e)}")
            return None
    
    async def invalidate(self, company_name: str) -> bool:
        """
        Invalidate all cached enrichments for a company.
        
        Args:
            company_name: Name of the company
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = (
                self.client.table(self.table)
                .update({"is_valid": False})
                .ilike("company_name", company_name)
                .execute()
            )
            
            logger.info(f"Invalidated enrichments for company: {company_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating company enrichment: {str(e)}")
            return False
    
    async def get_by_company_id(
        self,
        company_id: UUID,
        max_age_days: int = 7,
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest enrichment by company ID.
        
        Args:
            company_id: UUID of company
            max_age_days: Maximum age of cached data in days
        
        Returns:
            Latest enrichment data or None
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            response = (
                self.client.table(self.table)
                .select("*")
                .eq("company_id", str(company_id))
                .eq("is_valid", True)
                .gte("enriched_at", cutoff_date.isoformat())
                .order("enriched_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching company enrichment by ID: {str(e)}")
            return None


class CandidateEnrichmentService:
    """
    Service for managing candidate enrichment data in the database.
    
    Handles caching, retrieval, and invalidation of enriched candidate data.
    """
    
    def __init__(self):
        """Initialize the service with database client."""
        self.client = get_supabase_client()
        self.table = "candidate_enrichments"
    
    async def get_latest(
        self,
        candidate_id: UUID,
        max_age_days: int = 90,
    ) -> Optional[Dict[str, Any]]:
        """
        Get the latest valid enrichment for a candidate.
        
        Args:
            candidate_id: UUID of the candidate
            max_age_days: Maximum age of cached data in days (default: 90)
        
        Returns:
            Latest enrichment data or None if not found or too old
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            response = (
                self.client.table(self.table)
                .select("*")
                .eq("candidate_id", str(candidate_id))
                .eq("is_valid", True)
                .gte("enriched_at", cutoff_date.isoformat())
                .order("enriched_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                logger.info(f"Found cached enrichment for candidate: {candidate_id}")
                return response.data[0]
            
            logger.info(f"No recent enrichment found for candidate: {candidate_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching candidate enrichment: {str(e)}")
            return None
    
    async def save(
        self,
        candidate_id: UUID,
        candidate_name: str,
        enrichment_data: Dict[str, Any],
        search_keywords: Optional[List[str]] = None,
        expires_in_days: int = 90,
    ) -> Optional[Dict[str, Any]]:
        """
        Save candidate enrichment data to cache.
        
        Args:
            candidate_id: UUID of the candidate
            candidate_name: Name of the candidate
            enrichment_data: Enriched data from Brave Search
            search_keywords: Optional keywords used in search
            expires_in_days: Days until cache expires (default: 90)
        
        Returns:
            Saved enrichment record or None if failed
        """
        try:
            expires_at = datetime.now() + timedelta(days=expires_in_days)
            
            record = {
                "candidate_id": str(candidate_id),
                "candidate_name": candidate_name,
                "professional_summary": enrichment_data.get("professional_summary"),
                "linkedin_profile": enrichment_data.get("linkedin_profile"),
                "github_profile": enrichment_data.get("github_profile"),
                "portfolio_url": enrichment_data.get("portfolio_url"),
                "publications": enrichment_data.get("publications", []),
                "awards": enrichment_data.get("awards", []),
                "raw_results": [
                    result.dict() if hasattr(result, "dict") else result
                    for result in enrichment_data.get("raw_results", [])
                ],
                "search_query": candidate_name,
                "search_keywords": search_keywords or [],
                "result_count": len(enrichment_data.get("raw_results", [])),
                "enriched_at": datetime.now().isoformat(),
                "expires_at": expires_at.isoformat(),
                "is_valid": True,
            }
            
            response = (
                self.client.table(self.table)
                .insert(record)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                logger.info(f"Saved enrichment for candidate: {candidate_id}")
                return response.data[0]
            
            logger.warning(f"Failed to save enrichment for candidate: {candidate_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error saving candidate enrichment: {str(e)}")
            return None


    async def invalidate(self, candidate_id: UUID) -> bool:
        """
        Invalidate all cached enrichments for a candidate.
        
        Args:
            candidate_id: UUID of the candidate
        
        Returns:
            True if successful, False otherwise
        """
        try:
            response = (
                self.client.table(self.table)
                .update({"is_valid": False})
                .eq("candidate_id", str(candidate_id))
                .execute()
            )
            
            logger.info(f"Invalidated enrichments for candidate: {candidate_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error invalidating candidate enrichment: {str(e)}")
            return False
    
    async def get_by_name(
        self,
        candidate_name: str,
        max_age_days: int = 90,
    ) -> Optional[Dict[str, Any]]:
        """
        Get latest enrichment by candidate name.
        
        Args:
            candidate_name: Name of the candidate
            max_age_days: Maximum age of cached data in days
        
        Returns:
            Latest enrichment data or None
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=max_age_days)
            
            response = (
                self.client.table(self.table)
                .select("*")
                .ilike("candidate_name", candidate_name)
                .eq("is_valid", True)
                .gte("enriched_at", cutoff_date.isoformat())
                .order("enriched_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if response.data and len(response.data) > 0:
                return response.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error fetching candidate enrichment by name: {str(e)}")
            return None


_company_enrichment_service_instance: Optional[CompanyEnrichmentService] = None
_candidate_enrichment_service_instance: Optional[CandidateEnrichmentService] = None


def get_company_enrichment_service() -> CompanyEnrichmentService:
    """Get global company enrichment service instance."""
    global _company_enrichment_service_instance
    if _company_enrichment_service_instance is None:
        _company_enrichment_service_instance = CompanyEnrichmentService()
    return _company_enrichment_service_instance


def get_candidate_enrichment_service() -> CandidateEnrichmentService:
    """Get global candidate enrichment service instance."""
    global _candidate_enrichment_service_instance
    if _candidate_enrichment_service_instance is None:
        _candidate_enrichment_service_instance = CandidateEnrichmentService()
    return _candidate_enrichment_service_instance

