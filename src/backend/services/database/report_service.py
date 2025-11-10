"""
Analysis Report database service.

Handles CRUD operations for persistent analysis reports.
Reports group multiple candidate analyses and store evaluation criteria.
"""

from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from database import get_supabase_client
import logging
import random
import string

logger = logging.getLogger(__name__)


class ReportService:
    """Service for managing persistent analysis reports in the database."""
    
    def __init__(self):
        self.client = get_supabase_client()
        self.table = "analysis_reports"
    
    def _generate_report_code(self) -> str:
        """
        Generate a unique report code.
        
        Format: REP-YYYYMMDD-XXXXXX
        Example: REP-20250109-A3B7K2
        """
        date_str = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"REP-{date_str}-{random_str}"
    
    async def create(
        self,
        interviewer_id: UUID,
        job_posting_id: UUID,
        weights: Dict[str, float],
        key_points: str,
        company_id: Optional[UUID] = None,
        hard_blockers: Optional[List[str]] = None,
        nice_to_have: Optional[List[str]] = None,
        structured_job_posting: Optional[Dict[str, Any]] = None,
        title: Optional[str] = None,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new analysis report.
        
        Args:
            interviewer_id: UUID of interviewer creating the report
            job_posting_id: UUID of job posting
            weights: Category weights
            key_points: Key requirements text
            company_id: Optional company UUID
            hard_blockers: Optional list of hard blockers
            nice_to_have: Optional list of nice-to-have items
            structured_job_posting: Optional structured job data
            title: Optional report title
            language: Report language
            
        Returns:
            Created report dict or None if failed
        """
        try:
            # Generate unique report code
            max_attempts = 5
            report_code = None
            
            for _ in range(max_attempts):
                candidate_code = self._generate_report_code()
                # Check if code exists
                existing = self.client.table(self.table)\
                    .select("id")\
                    .eq("report_code", candidate_code)\
                    .execute()
                
                if not existing.data or len(existing.data) == 0:
                    report_code = candidate_code
                    break
            
            if not report_code:
                logger.error("Failed to generate unique report code")
                return None
            
            report_data = {
                "report_code": report_code,
                "interviewer_id": str(interviewer_id),
                "company_id": str(company_id) if company_id else None,
                "job_posting_id": str(job_posting_id),
                "title": title,
                "weights": weights,
                "hard_blockers": hard_blockers or [],
                "nice_to_have": nice_to_have or [],
                "key_points": key_points,
                "structured_job_posting": structured_job_posting,
                "language": language,
                "status": "active",
                "total_candidates": 0
            }
            
            result = self.client.table(self.table)\
                .insert(report_data)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Created analysis report: {report_code} ({result.data[0]['id']})")
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating analysis report: {e}")
            return None
    
    async def get_by_id(self, report_id: UUID) -> Optional[Dict[str, Any]]:
        """Get report by ID."""
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("id", str(report_id))\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting report: {e}")
            return None
    
    async def get_by_code(self, report_code: str) -> Optional[Dict[str, Any]]:
        """
        Get report by report code.
        
        Args:
            report_code: Report code (e.g., REP-20250109-A3B7K2)
            
        Returns:
            Report dict or None if not found
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("report_code", report_code.upper())\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting report by code: {e}")
            return None
    
    async def update_executive_recommendation(
        self,
        report_id: UUID,
        executive_recommendation: Dict[str, Any]
    ) -> bool:
        """
        Update report with executive recommendation.
        
        Args:
            report_id: Report UUID
            executive_recommendation: AI-generated recommendation
            
        Returns:
            True if updated successfully
        """
        try:
            result = self.client.table(self.table)\
                .update({
                    "executive_recommendation": executive_recommendation,
                    "analyzed_at": datetime.utcnow().isoformat()
                })\
                .eq("id", str(report_id))\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error updating executive recommendation: {e}")
            return False
    
    async def increment_candidate_count(self, report_id: UUID, count: int = 1) -> bool:
        """
        Increment the total candidates count.
        
        Args:
            report_id: Report UUID
            count: Number to increment by
            
        Returns:
            True if updated successfully
        """
        try:
            # Get current report
            report = await self.get_by_id(report_id)
            if not report:
                return False
            
            new_count = report.get('total_candidates', 0) + count
            
            result = self.client.table(self.table)\
                .update({"total_candidates": new_count})\
                .eq("id", str(report_id))\
                .execute()
            
            return bool(result.data)
            
        except Exception as e:
            logger.error(f"Error incrementing candidate count: {e}")
            return False
    
    async def get_analyses_for_report(self, report_id: UUID) -> List[Dict[str, Any]]:
        """
        Get all analyses associated with a report.
        
        Args:
            report_id: Report UUID
            
        Returns:
            List of analysis dicts sorted by global_score DESC
        """
        try:
            result = self.client.table("analyses")\
                .select("*")\
                .eq("report_id", str(report_id))\
                .order("global_score", desc=True)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting analyses for report: {e}")
            return []
    
    async def get_recent_reports(
        self,
        interviewer_id: UUID,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get recent reports for an interviewer.
        
        Args:
            interviewer_id: Interviewer UUID
            limit: Maximum number of reports to return
            
        Returns:
            List of recent reports
        """
        try:
            result = self.client.table(self.table)\
                .select("*")\
                .eq("interviewer_id", str(interviewer_id))\
                .eq("status", "active")\
                .order("created_at", desc=True)\
                .limit(limit)\
                .execute()
            
            return result.data or []
            
        except Exception as e:
            logger.error(f"Error getting recent reports: {e}")
            return []


# Global service instance
_report_service: Optional[ReportService] = None


def get_report_service() -> ReportService:
    """Get global report service instance."""
    global _report_service
    if _report_service is None:
        _report_service = ReportService()
    return _report_service

