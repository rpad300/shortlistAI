"""
Analysis database service.

Handles CRUD operations for analyses table.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from database import get_supabase_client
import logging

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for managing analyses in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "analyses"
    
    async def create(
        self,
        mode: str,
        job_posting_id: UUID,
        cv_id: UUID,
        candidate_id: UUID,
        provider: str,
        categories: Dict[str, Any],
        language: str,
        prompt_id: Optional[UUID] = None,
        global_score: Optional[float] = None,
        strengths: Optional[List[str]] = None,
        risks: Optional[List[str]] = None,
        questions: Optional[List[str]] = None,
        intro_pitch: Optional[str] = None,
        hard_blocker_flags: Optional[List[str]] = None,
        report_id: Optional[UUID] = None,
        detailed_analysis: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new analysis record.
        
        Args:
            mode: 'interviewer' or 'candidate'
            job_posting_id: Job posting UUID
            cv_id: CV UUID
            candidate_id: Candidate UUID
            provider: AI provider used
            categories: Dict of category scores
            language: Language of analysis
            prompt_id: Optional prompt UUID
            global_score: Optional weighted global score
            strengths: Optional list of strengths
            risks: Optional list of risks/gaps
            questions: Optional list of questions
            intro_pitch: Optional intro pitch (candidate mode)
            hard_blocker_flags: Optional hard blocker violations
            report_id: Optional report UUID to associate analysis with
            
        Returns:
            Created analysis dict or None if failed
        """
        try:
            analysis_data = {
                "mode": mode,
                "job_posting_id": str(job_posting_id),
                "cv_id": str(cv_id),
                "candidate_id": str(candidate_id),
                "prompt_id": str(prompt_id) if prompt_id else None,
                "provider": provider,
                "categories": categories,
                "global_score": global_score,
                "strengths": {"items": strengths} if strengths else None,
                "risks": {"items": risks} if risks else None,
                "questions": questions if isinstance(questions, dict) else ({"items": questions} if questions else None),
                "intro_pitch": intro_pitch,
                "hard_blocker_flags": {"flags": hard_blocker_flags} if hard_blocker_flags else None,
                "language": language,
                "report_id": str(report_id) if report_id else None,
                "detailed_analysis": detailed_analysis
            }
            
            result = self.client.table(self.table)\
                .insert(analysis_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created analysis: {result.data[0]['id']}")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating analysis: {e}")
            return None
    
    async def get_by_id(self, analysis_id: UUID) -> Optional[Dict[str, Any]]:
        """Get analysis by ID."""
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(analysis_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting analysis: {e}")
            return None
    
    async def get_by_job_posting(
        self,
        job_posting_id: UUID
    ) -> List[Dict[str, Any]]:
        """
        Get all analyses for a job posting.
        
        Args:
            job_posting_id: Job posting UUID
            
        Returns:
            List of analysis dicts sorted by global_score DESC
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("job_posting_id", str(job_posting_id))\
                .order("global_score", desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting analyses for job posting: {e}")
            return []
    
    async def list_all(
        self,
        mode: Optional[str] = None,
        provider: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List all analyses with optional filtering (for Admin use).
        
        Args:
            mode: Optional filter by 'interviewer' or 'candidate'
            provider: Optional filter by AI provider
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of analysis dicts
        """
        try:
            query = self.client.table(self.table).select("*")
            
            if mode:
                query = query.eq("mode", mode)
            
            if provider:
                query = query.eq("provider", provider)
            
            query = query.order("created_at", desc=True)\
                .range(offset, offset + limit - 1)
            
            result = query.execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error listing analyses: {e}")
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
            result = self.client.table(self.table)\
                .select("*")\
                .eq("candidate_id", str(candidate_id))\
                .order("created_at", desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting analyses for candidate: {e}")
            return []
    
    async def count_all(self) -> int:
        """Count total number of analyses."""
        try:
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error counting analyses: {e}")
            return 0
    
    async def count_recent(self, days: int = 30) -> int:
        """Count analyses created in the last N days."""
        try:
            from datetime import datetime, timedelta
            cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
            result = self.client.table(self.table)\
                .select("id", count="exact")\
                .gte("created_at", cutoff)\
                .execute()
            return result.count or 0
        except Exception as e:
            logger.error(f"Error counting recent analyses: {e}")
            return 0
    
    async def count_by_provider(self) -> Dict[str, int]:
        """Count analyses by AI provider."""
        try:
            result = self.client.table(self.table)\
                .select("provider")\
                .execute()
            
            counts = {}
            for row in (result.data or []):
                provider = row.get("provider", "unknown")
                counts[provider] = counts.get(provider, 0) + 1
            
            return counts
        except Exception as e:
            logger.error(f"Error counting by provider: {e}")
            return {}
    
    async def count_by_language(self) -> Dict[str, int]:
        """Count analyses by language."""
        try:
            result = self.client.table(self.table)\
                .select("language")\
                .execute()
            
            counts = {}
            for row in (result.data or []):
                language = row.get("language", "unknown")
                counts[language] = counts.get(language, 0) + 1
            
            return counts
        except Exception as e:
            logger.error(f"Error counting by language: {e}")
            return {}


# Global service instance
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """Get global analysis service instance."""
    global _analysis_service
    if _analysis_service is None:
        _analysis_service = AnalysisService()
    return _analysis_service

