"""
Data enrichment endpoints using Brave Search API.

Provides endpoints to enrich company and candidate information
with publicly available data from web search.
"""

import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from services.search.brave_search import (
    get_brave_search_service,
    CompanyEnrichment,
    CandidateEnrichment,
)
from services.database.job_posting_service import JobPostingService
from services.database.candidate_service import CandidateService
from services.database.enrichment_service import (
    CompanyEnrichmentService,
    CandidateEnrichmentService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/enrichment", tags=["enrichment"])


# Request/Response Models
class CompanyEnrichmentRequest(BaseModel):
    """Request to enrich company data."""
    
    company_name: str = Field(..., description="Name of the company to enrich")
    additional_context: Optional[str] = Field(
        None,
        description="Additional context (e.g., industry, location) to improve search"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached data if available"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh even if cache is valid"
    )


class CompanyEnrichmentFromJobRequest(BaseModel):
    """Request to enrich company data from a job posting."""
    
    session_id: UUID = Field(..., description="Session ID containing the job posting")


class CandidateEnrichmentRequest(BaseModel):
    """Request to enrich candidate data."""
    
    candidate_name: str = Field(..., description="Name of the candidate to enrich")
    additional_keywords: Optional[list[str]] = Field(
        None,
        description="Additional search keywords (e.g., skills, previous companies)"
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use cached data if available"
    )
    force_refresh: bool = Field(
        default=False,
        description="Force refresh even if cache is valid"
    )


class CandidateEnrichmentFromCVRequest(BaseModel):
    """Request to enrich candidate data from their CV."""
    
    candidate_id: UUID = Field(..., description="Candidate ID")


class NewsSearchRequest(BaseModel):
    """Request to search for company news."""
    
    company_name: str = Field(..., description="Name of the company")
    days: int = Field(default=7, ge=1, le=365, description="Number of days to look back")
    count: int = Field(default=5, ge=1, le=20, description="Maximum number of results")


class ServiceStatusResponse(BaseModel):
    """Enrichment service status."""
    
    enabled: bool
    message: str


# Endpoints

@router.get("/status", response_model=ServiceStatusResponse)
async def get_enrichment_status():
    """
    Check if enrichment services are enabled.
    
    Returns service status and configuration info.
    """
    brave_service = get_brave_search_service()
    
    return ServiceStatusResponse(
        enabled=brave_service.is_enabled(),
        message=(
            "Brave Search enrichment is enabled"
            if brave_service.is_enabled()
            else "Brave Search enrichment is disabled. Set BRAVE_SEARCH_API_KEY to enable."
        )
    )


@router.post("/company", response_model=CompanyEnrichment)
async def enrich_company(request: CompanyEnrichmentRequest):
    """
    Enrich company information using web search.
    
    Searches for:
    - Company website and description
    - Industry information
    - Recent news
    - Social media profiles
    
    **Privacy**: Only uses publicly available information.
    
    **Caching**: Results are cached for 7 days by default.
    Use `use_cache=False` or `force_refresh=True` to bypass cache.
    """
    brave_service = get_brave_search_service()
    enrichment_service = CompanyEnrichmentService()
    
    if not brave_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Brave Search enrichment is not enabled. Configure BRAVE_SEARCH_API_KEY."
        )
    
    try:
        # Try cache first (if enabled and not forcing refresh)
        if request.use_cache and not request.force_refresh:
            cached = await enrichment_service.get_latest(
                company_name=request.company_name,
                max_age_days=7,  # Company data cache: 7 days
            )
            
            if cached:
                logger.info(f"Returning cached enrichment for company: {request.company_name}")
                # Convert cached data to CompanyEnrichment model
                return CompanyEnrichment(
                    company_name=cached["company_name"],
                    website=cached.get("website"),
                    description=cached.get("description"),
                    industry=cached.get("industry"),
                    size=cached.get("company_size"),
                    location=cached.get("location"),
                    social_media=cached.get("social_media", {}),
                    recent_news=cached.get("recent_news", []),
                    raw_results=[],  # Don't return raw results from cache
                )
        
        # If no cache or force refresh, fetch from API
        logger.info(f"Fetching fresh enrichment for company: {request.company_name}")
        enrichment = await brave_service.enrich_company(
            company_name=request.company_name,
            additional_context=request.additional_context,
        )
        
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No information found for company: {request.company_name}"
            )
        
        # Save to cache
        await enrichment_service.save(
            company_name=request.company_name,
            enrichment_data=enrichment.dict(),
            expires_in_days=30,  # Cache expires in 30 days
        )
        
        return enrichment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching company: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich company data: {str(e)}"
        )


@router.post("/company/from-job", response_model=CompanyEnrichment)
async def enrich_company_from_job(request: CompanyEnrichmentFromJobRequest):
    """
    Enrich company information from a job posting session.
    
    Extracts company name from the job posting and enriches it with web data.
    
    **Privacy**: Only uses publicly available information.
    """
    brave_service = get_brave_search_service()
    
    if not brave_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Brave Search enrichment is not enabled. Configure BRAVE_SEARCH_API_KEY."
        )
    
    try:
        # Get job posting from session
        job_service = JobPostingService()
        job_posting = await job_service.get_by_session_id(request.session_id)
        
        if not job_posting:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No job posting found for session: {request.session_id}"
            )
        
        # Extract company name from job posting
        # Note: This assumes job posting has a 'company_id' field
        # You may need to adjust based on your actual schema
        company_name = job_posting.get("company_name")
        
        if not company_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job posting does not contain company name"
            )
        
        # Enrich company data
        enrichment = await brave_service.enrich_company(
            company_name=company_name,
            additional_context=None,
        )
        
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No information found for company: {company_name}"
            )
        
        return enrichment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching company from job: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich company data: {str(e)}"
        )


@router.post("/candidate", response_model=CandidateEnrichment)
async def enrich_candidate(request: CandidateEnrichmentRequest):
    """
    Enrich candidate information using web search.
    
    Searches for:
    - LinkedIn profile
    - GitHub profile
    - Portfolio/personal website
    - Publications and achievements
    
    **Privacy**: 
    - Only searches publicly available information
    - Does NOT send CV content or sensitive personal data
    - Respects user privacy and data protection regulations
    """
    brave_service = get_brave_search_service()
    
    if not brave_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Brave Search enrichment is not enabled. Configure BRAVE_SEARCH_API_KEY."
        )
    
    try:
        enrichment = await brave_service.enrich_candidate(
            candidate_name=request.candidate_name,
            additional_keywords=request.additional_keywords,
        )
        
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No information found for candidate: {request.candidate_name}"
            )
        
        return enrichment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching candidate: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich candidate data: {str(e)}"
        )


@router.post("/candidate/from-cv", response_model=CandidateEnrichment)
async def enrich_candidate_from_cv(request: CandidateEnrichmentFromCVRequest):
    """
    Enrich candidate information from their CV data.
    
    Extracts candidate name from stored CV and enriches with public web data.
    
    **Privacy**: 
    - Only searches publicly available information
    - Does NOT send CV content to search API
    - Only uses candidate name for search
    """
    brave_service = get_brave_search_service()
    
    if not brave_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Brave Search enrichment is not enabled. Configure BRAVE_SEARCH_API_KEY."
        )
    
    try:
        # Get candidate from database
        candidate_service = CandidateService()
        candidate = await candidate_service.get_by_id(request.candidate_id)
        
        if not candidate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No candidate found with ID: {request.candidate_id}"
            )
        
        # Extract candidate name
        candidate_name = candidate.get("full_name") or candidate.get("name")
        
        if not candidate_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Candidate record does not contain name"
            )
        
        # Enrich candidate data
        enrichment = await brave_service.enrich_candidate(
            candidate_name=candidate_name,
            additional_keywords=None,
        )
        
        if not enrichment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No information found for candidate: {candidate_name}"
            )
        
        return enrichment
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error enriching candidate from CV: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enrich candidate data: {str(e)}"
        )


@router.post("/company/news")
async def search_company_news(request: NewsSearchRequest):
    """
    Search for recent news about a company.
    
    Useful for getting up-to-date information about companies mentioned in job postings.
    
    Returns:
        List of recent news articles about the company
    """
    brave_service = get_brave_search_service()
    
    if not brave_service.is_enabled():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Brave Search enrichment is not enabled. Configure BRAVE_SEARCH_API_KEY."
        )
    
    try:
        news = await brave_service.search_company_news(
            company_name=request.company_name,
            days=request.days,
            count=request.count,
        )
        
        return {
            "company_name": request.company_name,
            "days_searched": request.days,
            "news_count": len(news),
            "news": news,
        }
        
    except Exception as e:
        logger.error(f"Error searching company news: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search company news: {str(e)}"
        )

