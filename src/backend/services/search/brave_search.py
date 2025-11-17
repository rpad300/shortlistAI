"""
Brave Search API integration service.

Provides web search capabilities to enrich company information and candidate context.
"""

import logging
from typing import Dict, List, Optional, Any
import httpx
from pydantic import BaseModel

from config import settings
from services.ai.prompts import get_prompt

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
    ai_summary: Optional[str] = None  # AI-generated summary from Summarizer or Grounding


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
    ai_summary: Optional[str] = None  # AI-generated summary from Summarizer or Grounding


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
        result_filter: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform web search using Brave Search API.
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            country: Country code for search results
            search_lang: Language for search results
            freshness: Filter by freshness (e.g., "pd" for past day, "pw" for past week)
            result_filter: Comma-delimited string of result types (web, infobox, discussions, faq, news, videos)
        
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
        
        # Use result_filter for Rich Search features (infobox, discussions, faq, etc.)
        if result_filter:
            params["result_filter"] = result_filter
        
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
                
                # Parse Rich Search results if available (infobox, discussions, faq)
                # These provide structured data that can enhance enrichment
                if "infobox" in data:
                    infobox = data.get("infobox", {})
                    if infobox.get("results"):
                        logger.info(f"Brave Search: Found infobox data for '{query}'")
                
                if "discussions" in data:
                    discussions = data.get("discussions", {}).get("results", [])
                    if discussions:
                        logger.info(f"Brave Search: Found {len(discussions)} discussion results for '{query}'")
                
                if "faq" in data:
                    faq = data.get("faq", {}).get("results", [])
                    if faq:
                        logger.info(f"Brave Search: Found {len(faq)} FAQ results for '{query}'")
                
                logger.info(f"Brave Search: Found {len(results)} web results for '{query}'")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"Brave Search API error: {str(e)}")
            raise
    
    async def search_news(
        self,
        query: str,
        count: int = 10,
        country: str = "US",
        search_lang: str = "en",
        freshness: Optional[str] = None,
    ) -> List[SearchResult]:
        """
        Perform news search using Brave News Search API endpoint.
        
        This is more efficient than using web search with result_filter for news.
        
        Args:
            query: Search query string
            count: Number of results to return (max 20)
            country: Country code for search results
            search_lang: Language for search results
            freshness: Filter by freshness (e.g., "pd" for past day, "pw" for past week)
        
        Returns:
            List of news search results
            
        Raises:
            httpx.HTTPError: If API request fails
        """
        if not self.enabled:
            logger.warning("Brave Search not enabled. Returning empty results.")
            return []
        
        url = f"{self.BASE_URL}/news/search"
        
        params = {
            "q": query,
            "count": min(count, 20),
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
                
                # Parse news results
                news_results = data.get("news", {}).get("results", [])
                for result in news_results:
                    results.append(
                        SearchResult(
                            title=result.get("title", ""),
                            url=result.get("url", ""),
                            description=result.get("description"),
                            age=result.get("age"),
                            meta_url=result.get("meta_url"),
                        )
                    )
                
                logger.info(f"Brave News Search: Found {len(results)} news results for '{query}'")
                return results
                
        except httpx.HTTPError as e:
            logger.error(f"Brave News Search API error: {str(e)}")
            raise
    
    async def get_ai_summary(
        self,
        query: str,
        use_grounding: bool = True,
    ) -> Optional[str]:
        """
        Get AI-generated summary using Brave AI Grounding or Summarizer API.
        
        AI Grounding provides answers backed by verifiable sources on the Web.
        Summarizer provides summaries of search results.
        
        Args:
            query: Search query string
            use_grounding: If True, use AI Grounding (default). If False, use Summarizer.
        
        Returns:
            AI-generated summary or None if fails
        """
        if not self.enabled:
            return None
        
        try:
            url = f"{self.BASE_URL}/chat/completions"
            
            headers = {
                "Accept": "application/json",
                "Accept-Encoding": "gzip",
                "Content-Type": "application/json",
                "X-Subscription-Token": self.api_key,
            }
            
            # Use AI Grounding (recommended) or Summarizer
            model = "brave" if use_grounding else "brave-pro"
            
            payload = {
                "messages": [
                    {
                        "role": "user",
                        "content": query
                    }
                ],
                "model": model,
                "stream": False
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # Extract content from response
                if "choices" in data and len(data["choices"]) > 0:
                    content = data["choices"][0].get("message", {}).get("content", "")
                    if content:
                        logger.info(f"Brave AI Summary: Generated summary for '{query[:50]}...'")
                        return content
                
                return None
                
        except httpx.HTTPError as e:
            logger.warning(f"Brave AI Summary API error (may require Pro AI plan): {str(e)}")
            return None
        except Exception as e:
            logger.warning(f"Error getting AI summary: {str(e)}")
            return None
    
    async def enrich_company_from_links(
        self,
        company_name: str,
        website_url: Optional[str] = None,
        linkedin_url: Optional[str] = None,
        email: Optional[str] = None,
    ) -> Optional[CompanyEnrichment]:
        """
        Enrich company information using direct links provided by user.
        
        Uses the provided links directly with site: operators for more targeted searches.
        
        Args:
            company_name: Name of the company
            website_url: Direct website URL (if provided)
            linkedin_url: Direct LinkedIn company page URL (if provided)
            email: Company email (if provided)
        
        Returns:
            Enriched company data or None if search fails
        """
        if not self.enabled:
            return None
        
        try:
            enrichment = CompanyEnrichment(
                company_name=company_name,
                raw_results=[],
            )
            
            # Store provided links directly
            if website_url:
                enrichment.website = website_url
                
                # Search for information specifically from the website
                try:
                    # Extract domain from URL
                    from urllib.parse import urlparse
                    parsed = urlparse(website_url)
                    domain = parsed.netloc.replace("www.", "")
                    
                    # Search for company info on their own website
                    site_query = f'site:{domain} "{company_name}" (about OR company OR overview OR "who we are")'
                    site_results = await self.search_web(
                        query=site_query,
                        count=5,
                        result_filter="web,infobox"
                    )
                    
                    if site_results:
                        enrichment.raw_results.extend(site_results)
                        # Use first result as description if we don't have one
                        if site_results[0].description and not enrichment.description:
                            enrichment.description = site_results[0].description
                        
                        logger.info(f"Found {len(site_results)} results from company website {domain}")
                
                except Exception as e:
                    logger.warning(f"Failed to search company website {website_url}: {e}")
            
            # Search LinkedIn company page if provided
            if linkedin_url:
                enrichment.social_media["linkedin"] = linkedin_url
                
                try:
                    # Extract LinkedIn company slug from URL
                    # URL format: https://www.linkedin.com/company/company-name/
                    if "linkedin.com/company/" in linkedin_url:
                        linkedin_slug = linkedin_url.split("linkedin.com/company/")[-1].strip("/")
                        
                        # Search for information about this LinkedIn company page
                        linkedin_query = f'site:linkedin.com/company/{linkedin_slug} "{company_name}"'
                        linkedin_results = await self.search_web(
                            query=linkedin_query,
                            count=5,
                            result_filter="web"
                        )
                        
                        if linkedin_results:
                            enrichment.raw_results.extend(linkedin_results)
                            logger.info(f"Found {len(linkedin_results)} results from LinkedIn company page")
                
                except Exception as e:
                    logger.warning(f"Failed to search LinkedIn page {linkedin_url}: {e}")
            
            # If we have links, do a targeted search about the company using those links
            if website_url or linkedin_url:
                # Build targeted query using the provided links
                targeted_query_parts = [company_name]
                
                if website_url:
                    from urllib.parse import urlparse
                    parsed = urlparse(website_url)
                    domain = parsed.netloc.replace("www.", "")
                    targeted_query_parts.append(f'site:{domain}')
                
                targeted_query = " ".join(targeted_query_parts)
                targeted_query += " (about OR company OR overview OR services OR products OR technology)"
                
                try:
                    targeted_results = await self.search_web(
                        query=targeted_query,
                        count=10,
                        result_filter="web,infobox,discussions"
                    )
                    
                    if targeted_results:
                        enrichment.raw_results.extend(targeted_results)
                        
                        # Extract more structured data
                        for result in targeted_results[:3]:
                            url_lower = result.url.lower()
                            
                            # Try to extract industry/sector info
                            if "about" in url_lower or "company" in url_lower:
                                if result.description and not enrichment.description:
                                    enrichment.description = result.description
                        
                        logger.info(f"Found {len(targeted_results)} targeted results using provided links")
                
                except Exception as e:
                    logger.warning(f"Failed to do targeted search: {e}")
            
            # Search for recent news (this is still useful even with direct links)
            try:
                news_template = await get_prompt("brave_company_news", language="en")
                news_query = news_template.format(company_name=company_name)
            except Exception as e:
                logger.warning(f"Failed to load news prompt template, using fallback: {e}")
                news_query = f'"{company_name}" news'
            
            news_results = await self.search_news(
                news_query, 
                count=5, 
                freshness="pw"  # Past week
            )
            
            enrichment.recent_news = [
                {
                    "title": result.title,
                    "url": result.url,
                    "description": result.description or "",
                }
                for result in news_results
            ]
            
            # Try to get AI summary using the provided links
            try:
                summary_context = f"Company: {company_name}"
                if website_url:
                    summary_context += f", Website: {website_url}"
                if linkedin_url:
                    summary_context += f", LinkedIn: {linkedin_url}"
                
                summary_query = f"Provide a brief summary about {summary_context} including industry, size, technologies used, and recent developments. Focus on information relevant for CV optimization."
                ai_summary = await self.get_ai_summary(summary_query, use_grounding=True)
                if ai_summary:
                    enrichment.ai_summary = ai_summary
            except Exception as e:
                logger.debug(f"AI summary not available for company {company_name}: {e}")
            
            # Extract industry and size from description if available
            if enrichment.description:
                # Try to parse industry and size from description (simple extraction)
                desc_lower = enrichment.description.lower()
                # Common industry keywords
                industries = ["technology", "finance", "healthcare", "energy", "consulting", "software", "data", "ai", "bi", "business intelligence"]
                for industry in industries:
                    if industry in desc_lower:
                        enrichment.industry = industry.capitalize()
                        break
            
            logger.info(f"Successfully enriched company '{company_name}' using provided links")
            return enrichment
            
        except Exception as e:
            logger.error(f"Error enriching company from links {company_name}: {str(e)}")
            return None
    
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
            # Build search query using prompt template from database
            try:
                template = await get_prompt("brave_company_search", language="en")
                query = template.format(
                    company_name=company_name,
                    additional_context=f" {additional_context}" if additional_context else ""
                ).strip()
            except Exception as e:
                logger.warning(f"Failed to load prompt template, using fallback: {e}")
                # Fallback to hardcoded query
                query = company_name
                if additional_context:
                    query += f" {additional_context}"
            
            # Search for company info with Rich Search (infobox for structured company data)
            results = await self.search_web(
                query, 
                count=10,
                result_filter="web,infobox,discussions"  # Get structured data via Rich Search
            )
            
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
            
            # Search for recent news using prompt template
            try:
                news_template = await get_prompt("brave_company_news", language="en")
                news_query = news_template.format(company_name=company_name)
            except Exception as e:
                logger.warning(f"Failed to load news prompt template, using fallback: {e}")
                news_query = f"{company_name} news"
            
            # Use dedicated News Search endpoint for better results
            news_results = await self.search_news(
                news_query, 
                count=5, 
                freshness="pw"  # Past week
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
            
            # Optionally get AI summary for richer context
            try:
                summary_query = f"Provide a brief summary about {company_name} including industry, size, and recent developments"
                ai_summary = await self.get_ai_summary(summary_query, use_grounding=True)
                if ai_summary:
                    enrichment.ai_summary = ai_summary
            except Exception as e:
                logger.debug(f"AI summary not available for company {company_name}: {e}")
            
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
            # Build search query using prompt template from database
            try:
                template = await get_prompt("brave_candidate_search", language="en")
                additional_keywords_str = " " + " ".join(additional_keywords) if additional_keywords else ""
                query = template.format(
                    candidate_name=candidate_name,
                    additional_keywords=additional_keywords_str
                ).strip()
            except Exception as e:
                logger.warning(f"Failed to load prompt template, using fallback: {e}")
                # Fallback to hardcoded query
                query = candidate_name
                if additional_keywords:
                    query += " " + " ".join(additional_keywords)
            
            # Search for candidate info with Rich Search
            results = await self.search_web(
                query, 
                count=10,
                result_filter="web,discussions"  # Get discussions and web results
            )
            
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
            
            # Search for publications using prompt template
            try:
                pub_template = await get_prompt("brave_candidate_publications", language="en")
                pub_query = pub_template.format(candidate_name=candidate_name)
            except Exception as e:
                logger.warning(f"Failed to load publications prompt template, using fallback: {e}")
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
            
            # Optionally get AI summary for richer context
            try:
                summary_query = f"Provide a brief professional summary about {candidate_name} including skills, experience, and notable achievements"
                ai_summary = await self.get_ai_summary(summary_query, use_grounding=True)
                if ai_summary:
                    enrichment.ai_summary = ai_summary
            except Exception as e:
                logger.debug(f"AI summary not available for candidate {candidate_name}: {e}")
            
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
            
            # Use prompt template for news query
            try:
                news_template = await get_prompt("brave_company_news", language="en")
                query = news_template.format(company_name=company_name)
            except Exception as e:
                logger.warning(f"Failed to load news prompt template, using fallback: {e}")
                query = f"{company_name} news"
            
            # Use dedicated News Search endpoint for better results
            results = await self.search_news(
                query, 
                count=count, 
                freshness=freshness
            )
            
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

