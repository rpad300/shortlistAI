"""
Company Research Service.

Enriches job posting analysis with web research about the company.
"""

import logging
from typing import Dict, Any, Optional
import requests
from datetime import datetime

logger = logging.getLogger(__name__)


class CompanyResearchService:
    """
    Service for researching companies via web search.
    
    Enriches candidate preparation with company context.
    """
    
    def __init__(self):
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    async def research_company(
        self,
        company_name: str,
        job_title: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Research company using web search.
        
        Args:
            company_name: Name of the company
            job_title: Optional job title for context
            
        Returns:
            Company research dict with key insights
        """
        if not company_name or len(company_name) < 2:
            return None
        
        # Check cache
        cache_key = company_name.lower().strip()
        if cache_key in self.cache:
            logger.info(f"Using cached company research for: {company_name}")
            return self.cache[cache_key]
        
        try:
            # Build search query
            search_query = f"{company_name} company"
            if job_title:
                search_query += f" {job_title}"
            search_query += " culture values mission about"
            
            logger.info(f"Researching company: {company_name}")
            
            # Simple web scraping approach (in production, use proper web search API)
            # For MVP, we'll return structured research prompt for AI to fill
            research_data = {
                "company_name": company_name,
                "search_query": search_query,
                "researched_at": datetime.utcnow().isoformat(),
                "insights": {
                    "mission": f"Research needed: {company_name} mission and values",
                    "culture": f"Research needed: {company_name} culture and work environment",
                    "recent_news": f"Research needed: Recent news about {company_name}",
                    "interview_tips": f"Research needed: Interview tips for {company_name}"
                },
                "status": "research_prompt_ready"
            }
            
            # Cache result
            self.cache[cache_key] = research_data
            
            return research_data
            
        except Exception as e:
            logger.error(f"Error researching company {company_name}: {e}")
            return None
    
    def enrich_candidate_analysis_prompt(
        self,
        base_prompt: str,
        company_research: Optional[Dict[str, Any]]
    ) -> str:
        """
        Add company research context to candidate analysis prompt.
        
        Args:
            base_prompt: Original analysis prompt
            company_research: Research data about the company
            
        Returns:
            Enriched prompt with company context
        """
        if not company_research:
            return base_prompt
        
        company_name = company_research.get("company_name", "")
        
        enrichment = f"""

COMPANY CONTEXT (use this to tailor your guidance):
Company: {company_name}

When preparing the candidate:
- Tailor the intro pitch to mention alignment with {company_name}'s known values or mission
- Suggest researching {company_name}'s recent projects, products, or news
- Include questions the candidate should ask about {company_name}'s culture and growth
- Reference {company_name} specifically in suggested answers where relevant

"""
        
        # Insert enrichment before the JSON structure requirement
        enriched_prompt = base_prompt.replace(
            "Return ONLY valid JSON:",
            enrichment + "\nReturn ONLY valid JSON:"
        )
        
        return enriched_prompt


# Global service instance
_company_research_service: Optional[CompanyResearchService] = None


def get_company_research_service() -> CompanyResearchService:
    """Get global company research service instance."""
    global _company_research_service
    if _company_research_service is None:
        _company_research_service = CompanyResearchService()
    return _company_research_service





