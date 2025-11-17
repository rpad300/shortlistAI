"""
Candidate Profile database service.

Handles CRUD operations for candidate_profiles table.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
import logging

from database import get_supabase_client


logger = logging.getLogger(__name__)


class CandidateProfileService:
    """Service for managing structured candidate profiles."""

    def __init__(self):
        self.client = get_supabase_client()
        self.table_profiles = "candidate_profiles"

    def upsert_candidate_profile(
        self,
        candidate_id: UUID,
        full_name: str,
        normalized_name: Optional[str],
        basic_info: Optional[Dict[str, Any]] = None,
        contact_info: Optional[Dict[str, Any]] = None,
        professional_summary: Optional[str] = None,
        professional_summary_structured: Optional[Dict[str, Any]] = None,
        work_experience: Optional[List[Dict[str, Any]]] = None,
        education: Optional[List[Dict[str, Any]]] = None,
        skills: Optional[Dict[str, Any]] = None,
        projects: Optional[List[Dict[str, Any]]] = None,
        publications: Optional[List[Dict[str, Any]]] = None,
        awards: Optional[List[Dict[str, Any]]] = None,
        career_preferences: Optional[Dict[str, Any]] = None,
        ai_summary: Optional[str] = None,
        ai_insights: Optional[Dict[str, Any]] = None,
        social_media_risk_analysis: Optional[Dict[str, Any]] = None,
        raw_brave_data: Optional[Dict[str, Any]] = None,
        source_cv_id: Optional[UUID] = None,
        source_session_id: Optional[UUID] = None,
        enrichment_source: Optional[str] = "chatbot",
        data_quality_score: Optional[int] = None,
        is_verified: Optional[bool] = None,
        verification_notes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Upsert a candidate profile by candidate_id."""
        try:
            existing = (
                self.client.table(self.table_profiles)
                .select("*")
                .eq("candidate_id", str(candidate_id))
                .limit(1)
                .execute()
            )
            record = {
                "candidate_id": str(candidate_id),
                "full_name": full_name,
                "normalized_name": normalized_name,
                "basic_info": basic_info or {},
                "contact_info": contact_info or {},
                "professional_summary": professional_summary,
                "professional_summary_structured": professional_summary_structured or {},
                "work_experience": work_experience or [],
                "education": education or [],
                "skills": skills or {},
                "projects": projects or [],
                "publications": publications or [],
                "awards": awards or [],
                "career_preferences": career_preferences or {},
                "ai_summary": ai_summary,
                "ai_insights": ai_insights or {},
                "social_media_risk_analysis": social_media_risk_analysis or {},
                "raw_brave_data": raw_brave_data or {},
                "source_cv_id": str(source_cv_id) if source_cv_id else None,
                "source_session_id": str(source_session_id) if source_session_id else None,
                "enrichment_source": enrichment_source,
                "data_quality_score": data_quality_score,
                "is_verified": is_verified,
                "verification_notes": verification_notes,
            }
            if existing.data:
                profile_id = existing.data[0]["id"]
                res = (
                    self.client.table(self.table_profiles)
                    .update(record)
                    .eq("id", profile_id)
                    .execute()
                )
                return res.data[0] if res.data else None
            else:
                res = self.client.table(self.table_profiles).insert(record).execute()
                return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error upserting candidate profile: {e}")
            return None

    def get_candidate_profile_by_candidate(
        self, candidate_id: UUID
    ) -> Optional[Dict[str, Any]]:
        try:
            res = (
                self.client.table(self.table_profiles)
                .select("*")
                .eq("candidate_id", str(candidate_id))
                .limit(1)
                .execute()
            )
            return res.data[0] if res.data else None
        except Exception as e:
            logger.error(f"Error fetching candidate profile: {e}")
            return None


def get_candidate_profile_service() -> CandidateProfileService:
    return CandidateProfileService()


