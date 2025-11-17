"""
Company Profile database service.

Handles CRUD operations for company_profiles and company_job_positions tables.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
import logging

from database import get_supabase_client


logger = logging.getLogger(__name__)


class CompanyProfileService:
    """Service for managing structured company profiles and positions."""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_profiles = "company_profiles"
        self.table_positions = "company_job_positions"

    # -------------------------------------------------------------------------
    # Company Profiles
    # -------------------------------------------------------------------------
    def upsert_company_profile(
        self,
        company_name: str,
        normalized_name: Optional[str],
        basic_info: Optional[Dict[str, Any]] = None,
        contact_info: Optional[Dict[str, Any]] = None,
        culture: Optional[Dict[str, Any]] = None,
        technologies: Optional[Dict[str, Any]] = None,
        recent_activity: Optional[List[Dict[str, Any]]] = None,
        hiring_info: Optional[Dict[str, Any]] = None,
        ai_summary: Optional[str] = None,
        ai_insights: Optional[Dict[str, Any]] = None,
        reputation_risk_analysis: Optional[Dict[str, Any]] = None,
        raw_brave_data: Optional[Dict[str, Any]] = None,
        enrichment_source: Optional[str] = "chatbot",
        enriched_by_session_id: Optional[UUID] = None,
        enriched_by_user_id: Optional[UUID] = None,
        data_quality_score: Optional[int] = None,
        is_verified: Optional[bool] = None,
        verification_notes: Optional[str] = None,
        company_id: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upsert a company profile by normalized_name or company_name."""
        try:
            # Try to find existing by normalized_name first
            query = self.client.table(self.table_profiles).select("*").limit(1)
            if normalized_name:
                query = query.eq("normalized_name", normalized_name)
            else:
                query = query.eq("company_name", company_name)
            existing = query.execute()
            record = {
                "company_id": str(company_id) if company_id else None,
                "company_name": company_name,
                "normalized_name": normalized_name,
                "basic_info": basic_info or {},
                "contact_info": contact_info or {},
                "culture": culture or {},
                "technologies": technologies or {},
                "recent_activity": recent_activity or [],
                "hiring_info": hiring_info or {},
                "ai_summary": ai_summary,
                "ai_insights": ai_insights or {},
                "reputation_risk_analysis": reputation_risk_analysis or {},
                "raw_brave_data": raw_brave_data or {},
                "enrichment_source": enrichment_source,
                "enriched_by_session_id": str(enriched_by_session_id) if enriched_by_session_id else None,
                "enriched_by_user_id": str(enriched_by_user_id) if enriched_by_user_id else None,
                "data_quality_score": data_quality_score,
                "is_verified": is_verified,
                "verification_notes": verification_notes,
            }
            if existing.data:
                profile_id = existing.data[0]["id"]
                result = (
                    self.client.table(self.table_profiles)
                    .update(record)
                    .eq("id", profile_id)
                    .execute()
                )
                return result.data[0] if result.data else None
            else:
                result = self.client.table(self.table_profiles).insert(record).execute()
                return result.data[0] if result.data else None
        except Exception as e:
            logger.error(f"Error upserting company profile: {e}")
            return None

    def get_company_profile_by_name(
        self, company_name: str
    ) -> Optional[Dict[str, Any]]:
        try:
            res = (
                self.client.table(self.table_profiles)
                .select("*")
                .eq("company_name", company_name)
                .limit(1)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error fetching company profile: {e}")
            return None

    # -------------------------------------------------------------------------
    # Company Job Positions
    # -------------------------------------------------------------------------
    def create_job_position(
        self,
        company_profile_id: UUID,
        job_title: str,
        normalized_title: Optional[str] = None,
        job_details: Optional[Dict[str, Any]] = None,
        requirements: Optional[Dict[str, Any]] = None,
        description: Optional[Dict[str, Any]] = None,
        source_url: Optional[str] = None,
        source_type: Optional[str] = None,
        source_metadata: Optional[Dict[str, Any]] = None,
        ai_analysis: Optional[Dict[str, Any]] = None,
        status: Optional[str] = "active",
        posted_date: Optional[str] = None,
        closing_date: Optional[str] = None,
        company_id: Optional[UUID] = None,
    ) -> Optional[Dict[str, Any]]:
        try:
            payload = {
                "company_profile_id": str(company_profile_id),
                "company_id": str(company_id) if company_id else None,
                "job_title": job_title,
                "normalized_title": normalized_title,
                "job_details": job_details or {},
                "requirements": requirements or {},
                "description": description or {},
                "source_url": source_url,
                "source_type": source_type,
                "source_metadata": source_metadata or {},
                "ai_analysis": ai_analysis or {},
                "status": status,
                "posted_date": posted_date,
                "closing_date": closing_date,
            }
            res = self.client.table(self.table_positions).insert(payload).execute()
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error creating company job position: {e}")
            return None


def get_company_profile_service() -> CompanyProfileService:
    return CompanyProfileService()


