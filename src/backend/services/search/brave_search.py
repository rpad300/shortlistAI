"""
Brave Search API integration service.

Provides web search capabilities to enrich company information and candidate context.
"""

import logging
from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel

from config import settings

logger = logging.getLogger(__name__)


class SearchResult(BaseModel):
    """Single search result from Brave Search."""
    
    title: str
    url: str
    description: Optional[str] = None
    age: Optional[str] = None  # How recent the content is
    meta_url: Optional[Dict[str, Any]] = None  # URL metadata


class CompanyEnrichment(BaseModel):
    """Enriched company information from search results."""
    
    company_name: str
    industry: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    size: Optional[str] = None
    location: Optional[str] = None
    recent_news: List[Dict[str, str]] = []
    social_media: Dict[str, str] = {}
    raw_results: List[SearchResult] = []


class CandidateEnrichment(BaseModel):
    """Enriched candidate information from search results."""
    
    name: str
    professional_summary: Optional[str] = None
    linkedin_profile: Optional[str] = None
    github_profile: Optional[str] = None
    portfolio_url: Optional[str] = None
    publications: List[Dict[str, str]] = []
    awards: List[str] = []
    raw_results: List[SearchResult] = []


class BraveSearchService:
    """
    Brave Search API service for enriching company and candidate data.
    
    Uses the Brave Web Search API to gather additional context about:
    - Companies (from job postings)
    - Candidates (public professional information)
    
    Privacy considerations:
    - Only searches publicly available information
    - Does not send CV content or sensitive personal data
    - Respects rate limits and privacy policies
    """
    
    BASE_URL = "https://api.search.brave.com/res/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Brave Search service.
        
        Args:
            api_key: Brave Search API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.brave_search_api_key
        self.enabled = bool(self.api_key)
        
        if not self.enabled:
            logger.warning(
                "Brave Search API key not configured. "
                "Company and candidate enrichment will be disabled."
            )
    
    async def search_web(
        self,
        query: str,
        count: int = 10,
        country: str = "US",
        search_lang: str = "en",
        freshness: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform web search using Brave Search API.
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            country: Country code for search results
            search_lang: Language for search results
            freshness: Filter by freshness (e.g., "pd" for past day, "pw" for past week)
        
        Returns:
            List of search results
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if not self.enabled:
            logger.warning("Brave Search not enabled. Returning empty results.")
            return []
        
        url = f"{self.BASE_URL}/web/search"
        
        params = {
            "q": query,
            "count": min(count, 20),  # API max is 20
            "country": country,
            "search_lang": search_lang,
        }
        
        if freshness:
            params["freshness"] = freshness
        
        headers = {
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            "X-Subscription-Token": self.api_key,
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                results = []
                
                # Parse web results
                web_results = data.get("web", {}).get("results", [])
                for result in web_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            description=result.get("description"),
                            age=result.get("age"),
                            meta_url=result.get("meta_url"),
                        )
                    )
                
                logger.info(f"Brave Search: Found {len(results)} results for '{query}'")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"Brave Search API error: {str(e)}")
            raise
    
    async def enrich_company(
        self,
        company_name: str,
        additional_context: Optional[str] = None,
    ) -> Optional[CompanyEnrichment]:
        """
        Enrich company information using web search.
        
        Searches for:
        - Company website and basic info
        - Industry and size
        - Recent news and updates
        - Social media presence
        
        Args:
            company_name: Name of the company
            additional_context: Additional context (e.g., industry, location)
        
        Returns:
            Enriched company data or None if search fails
        """
        if not self.enabled:
            return None
        
        try:
            # Build search query
            query = company_name
            if additional_context:
                query += f" {additional_context}"
            
            # Search for company info
            results = await self.search_web(query, count=10)
            
            if not results:
                logger.warning(f"No search results found for company: {company_name}")
                return None
            
            # Extract company information from results
            enrichment = CompanyEnrichment(
                company_name=company_name,
                raw_results=results,
            )
            
            # Extract website (usually first result)
            if results:
                enrichment.website = results[0].url
                enrichment.description = results[0].description
            
            # Search for recent news
            news_query = f"{company_name} news"
            news_results = await self.search_web(
                news_query, count=5, freshness="pw"  # Past week
            )
            
            enrichment.recent_news = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description or "",
                }
                for result in news_results
            ]
            
            # Extract social media links from results
            for result in results:
                url_lower = result.url.lower()
                if "linkedin.com/company" in url_lower:
                    enrichment.social_media["linkedin"] = result.url
                elif "twitter.com" in url_lower or "x.com" in url_lower:
                    enrichment.social_media["twitter"] = result.url
                elif "facebook.com" in url_lower:
                    enrichment.social_media["facebook"] = result.url
            
            logger.info(f"Successfully enriched company: {company_name}")
            return enrichment
            
        except Exception as e:
            logger.error(f"Error enriching company {company_name}: {str(e)}")
            return None
    
    async def enrich_candidate(
        self,
        candidate_name: str,
        additional_keywords: Optional[List[str]] = None,
    ) -> Optional[CandidateEnrichment]:
        """
        Enrich candidate information using web search.
        
        PRIVACY NOTE: Only searches publicly available information.
        Does NOT send CV content or sensitive personal data.
        
        Searches for:
        - LinkedIn profile
        - GitHub profile
        - Portfolio/personal website
        - Publications and achievements
        
        Args:
            candidate_name: Name of the candidate
            additional_keywords: Additional search terms (e.g., skills, company names)
        
        Returns:
            Enriched candidate data or None if search fails
        """
        if not self.enabled:
            return None
        
        try:
            # Build search query
            query = candidate_name
            if additional_keywords:
                query += " " + " ".join(additional_keywords)
            
            # Search for candidate info
            results = await self.search_web(query, count=10)
            
            if not results:
                logger.warning(f"No search results found for candidate: {candidate_name}")
                return None
            
            # Extract candidate information from results
            enrichment = CandidateEnrichment(
                name=candidate_name,
                raw_results=results,
            )
            
            # Extract professional profiles from results
            for result in results:
                url_lower = result.url.lower()
                
                if "linkedin.com/in" in url_lower:
                    enrichment.linkedin_profile = result.url
                    if result.description:
                        enrichment.professional_summary = result.description
                        
                elif "github.com" in url_lower and "/github.com/" in url_lower:
                    enrichment.github_profile = result.url
                    
                elif any(keyword in url_lower for keyword in ["portfolio", "about", "bio"]):
                    if not enrichment.portfolio_url:  # Take first portfolio-like URL
                        enrichment.portfolio_url = result.url
            
            # Search for publications
            pub_query = f"{candidate_name} publication OR paper OR article"
            pub_results = await self.search_web(pub_query, count=5)
            
            enrichment.publications = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description or "",
                }
                for result in pub_results
                if any(
                    keyword in result.url.lower()
                    for keyword in ["scholar", "researchgate", "arxiv", "medium", "blog"]
                )
            ]
            
            logger.info(f"Successfully enriched candidate: {candidate_name}")
            return enrichment
            
        except Exception as e:
            logger.error(f"Error enriching candidate {candidate_name}: {str(e)}")
            return None
    
    async def search_company_news(
        self,
        company_name: str,
        days: int = 7,
        count: int = 5,
    ) -> List[Dict[str, str]]:
        """
        Search for recent news about a company.
        
        Args:
            company_name: Name of the company
            days: Number of days to look back
            count: Maximum number of news items to return
        
        Returns:
            List of news items with title, URL, and description
        """
        if not self.enabled:
            return []
        
        try:
            # Determine freshness parameter
            freshness = None
            if days <= 1:
                freshness = "pd"  # Past day
            elif days <= 7:
                freshness = "pw"  # Past week
            elif days <= 30:
                freshness = "pm"  # Past month
            
            query = f"{company_name} news"
            results = await self.search_web(query, count=count, freshness=freshness)
            
            return [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description or "",
                    "age": result.age or "",
                }
                for result in results
            ]
            
        except Exception as e:
            logger.error(f"Error searching company news: {str(e)}")
            return []
    
    def is_enabled(self) -> bool:
        """Check if Brave Search is enabled (API key configured)."""
        return self.enabled


# Global service instance
_brave_search_service: Optional[BraveSearchService] = None


def get_brave_search_service() -> BraveSearchService:
    """
    Get or create global BraveSearchService instance.
    
    Returns:
        BraveSearchService instance
    """
    global _brave_search_service
    
    if _brave_search_service is None:
        _brave_search_service = BraveSearchService()
    
    return _brave_search_service

