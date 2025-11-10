"""
Database services package.

Provides CRUD operations for all database entities.
"""

from .candidate_service import CandidateService, get_candidate_service
from .company_service import CompanyService, get_company_service
from .interviewer_service import InterviewerService, get_interviewer_service
from .session_service import SessionService, get_session_service
from .job_posting_service import JobPostingService, get_job_posting_service
from .cv_service import CVService, get_cv_service
from .analysis_service import AnalysisService, get_analysis_service
from .report_service import ReportService, get_report_service

__all__ = [
    "CandidateService",
    "get_candidate_service",
    "CompanyService",
    "get_company_service",
    "InterviewerService",
    "get_interviewer_service",
    "SessionService",
    "get_session_service",
    "JobPostingService",
    "get_job_posting_service",
    "CVService",
    "get_cv_service",
    "AnalysisService",
    "get_analysis_service",
    "ReportService",
    "get_report_service",
]
