"""
AI Analysis service - High-level service for CV and candidate analysis.

Uses AI providers to analyze CVs against job postings.
"""

import json
from typing import Dict, Any, List, Optional
from uuid import UUID

from services.ai import get_ai_manager, AIRequest, PromptType
from services.ai.prompts import get_prompt
from services.database.enrichment_service import (
    CompanyEnrichmentService,
    CandidateEnrichmentService,
)
from services.search.brave_search import get_brave_search_service
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    High-level service for AI-powered CV analysis.
    
    Orchestrates AI calls for different analysis scenarios.
    """
    
    def __init__(self):
        self.ai_manager = get_ai_manager()
        self.company_enrichment_service = CompanyEnrichmentService()
        self.candidate_enrichment_service = CandidateEnrichmentService()
        self.brave_service = get_brave_search_service()
    
    async def recommend_weighting_and_blockers(
        self,
        job_posting_text: str,
        structured_job_posting: Optional[Dict[str, Any]],
        key_points: Optional[str],
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Recommend category weights, hard blockers, and nice-to-have requirements.
        """
        try:
            template = get_prompt("weighting_recommendation")
            
            variables = {
                "job_posting": job_posting_text or "No job posting text provided.",
                "structured_job_posting": json.dumps(structured_job_posting, indent=2, ensure_ascii=False) if structured_job_posting else "Not available",
                "key_points": key_points or "Not provided",
                "language": language
            }
            
            ai_request = AIRequest(
                prompt_type=PromptType.WEIGHTING_RECOMMENDATION,
                template=template,
                variables=variables,
                language=language,
                temperature=0.4,
                max_tokens=1024
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if not response.success:
                logger.error("Weighting recommendation failed: %s", response.error)
                return None
            
            return response.data
        
        except Exception as exc:
            logger.error("Error generating weighting recommendation: %s", exc)
            return None
    
    async def analyze_candidate_for_interviewer(
        self,
        job_posting_text: str,
        cv_text: str,
        key_points: str,
        weights: Dict[str, float],
        hard_blockers: List[str],
        nice_to_have: List[str],
        language: str = "en",
        company_name: Optional[str] = None,
        candidate_id: Optional[UUID] = None,
        candidate_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze a candidate for interviewer mode.
        
        Args:
            job_posting_text: Job posting content
            cv_text: CV content
            key_points: Interviewer-defined key requirements
            weights: Category weights
            hard_blockers: Hard blocker rules
            language: Response language
            
        Returns:
            Analysis dict with categories, scores, strengths, etc.
        """
        try:
            # Get prompt template
            template = get_prompt("interviewer_analysis")
            
            # Build enrichment context
            enrichment_context = await self._build_enrichment_context(
                company_name=company_name,
                candidate_id=candidate_id,
                candidate_name=candidate_name,
            )

            # Prepare variables
            variables = {
                "job_posting": job_posting_text,
                "cv_text": cv_text,
                "key_points": key_points,
                "weights": str(weights),
                "hard_blockers": str(hard_blockers),
                "nice_to_have": str(nice_to_have),
                "language": language,
                "enrichment_context": enrichment_context,
            }
            
            # Create AI request
            ai_request = AIRequest(
                prompt_type=PromptType.INTERVIEWER_ANALYSIS,
                template=template,
                variables=variables,
                language=language,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Execute with AI manager (auto-selects provider and handles fallback)
            response = await self.ai_manager.execute(ai_request)
            
            if not response.success:
                logger.error(f"AI analysis failed: {response.error}")
                return None
            
            return {
                "provider": response.provider,
                "model": response.model,
                "data": response.data or {},
                "raw_text": response.raw_text
            }
            
        except Exception as e:
            logger.error(f"Error in interviewer analysis: {e}")
            return None
    
    async def analyze_candidate_for_candidate(
        self,
        job_posting_text: str,
        cv_text: str,
        language: str = "en",
        company_context: Optional[Dict[str, Any]] = None,
        candidate_id: Optional[UUID] = None,
        candidate_name: Optional[str] = None,
        company_name: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze fit for candidate mode (self-preparation).
        
        Args:
            job_posting_text: Job posting content
            cv_text: CV content
            language: Response language
            company_context: Optional company research context
            
        Returns:
            Analysis dict with categories, strengths, gaps, questions, pitch
        """
        try:
            # Get prompt template
            template = get_prompt("candidate_analysis")
            
            # Build enrichment context using available data
            enrichment_context = await self._build_enrichment_context(
                company_name=company_name or (company_context or {}).get("company_name"),
                candidate_id=candidate_id,
                candidate_name=candidate_name,
            )
            
            # Prepare variables
            variables = {
                "job_posting": job_posting_text,
                "cv_text": cv_text,
                "language": language,
                "enrichment_context": enrichment_context,
            }
            
            # Create AI request
            ai_request = AIRequest(
                prompt_type=PromptType.CANDIDATE_ANALYSIS,
                template=template,
                variables=variables,
                language=language,
                temperature=0.7,
                max_tokens=2048
            )
            
            # Execute
            response = await self.ai_manager.execute(ai_request)
            
            if not response.success:
                logger.error(f"AI analysis failed: {response.error}")
                return None
            
            return {
                "provider": response.provider,
                "model": response.model,
                "data": response.data or {},
                "raw_text": response.raw_text
            }
            
        except Exception as e:
            logger.error(f"Error in candidate analysis: {e}")
            return None
    
    async def extract_cv_data(
        self,
        cv_text: str,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from CV text.
        
        Args:
            cv_text: Raw CV text
            language: Language of the CV
            
        Returns:
            Structured CV data dict
        """
        try:
            template = get_prompt("cv_extraction")
            
            ai_request = AIRequest(
                prompt_type=PromptType.CV_EXTRACTION,
                template=template,
                variables={"cv_text": cv_text},
                language=language,
                temperature=0.3,  # Lower for extraction
                max_tokens=2048
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            return response.data if response.success else None
            
        except Exception as e:
            logger.error(f"Error extracting CV data: {e}")
            return None

    async def summarize_cv(
        self,
        cv_text: str,
        file_name: str,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate a structured summary for a CV.
        """
        try:
            template = get_prompt("cv_summary")

            ai_request = AIRequest(
                prompt_type=PromptType.CV_SUMMARY,
                template=template,
                variables={
                    "cv_text": cv_text,
                    "file_name": file_name,
                    "language": language
                },
                language=language,
                temperature=0.4,
                max_tokens=1024
            )

            response = await self.ai_manager.execute(ai_request)

            if not response.success:
                logger.error(f"CV summary failed: {response.error}")
                return None

            return response.data

        except Exception as exc:
            logger.error(f"Error summarizing CV: {exc}")
            return None
    
    async def normalize_job_posting(
        self,
        job_posting_text: str,
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured data from job posting.
        
        Args:
            job_posting_text: Raw job posting text
            language: Language of the posting
            
        Returns:
            Structured job posting data dict
        """
        try:
            template = get_prompt("job_posting_normalization")
            
            # 🔍 DEBUG: Log exactly what we're sending
            logger.info("=" * 100)
            logger.info("🔍 JOB POSTING NORMALIZATION REQUEST")
            logger.info(f"Language: {language}")
            logger.info(f"Job Posting Length: {len(job_posting_text)} chars")
            logger.info("-" * 100)
            logger.info("TEMPLATE:")
            logger.info(template)
            logger.info("-" * 100)
            logger.info("JOB POSTING TEXT (first 2000 chars):")
            logger.info(job_posting_text[:2000])
            logger.info("-" * 100)
            logger.info("=" * 100)
            
            ai_request = AIRequest(
                prompt_type=PromptType.JOB_POSTING_NORMALIZATION,
                template=template,
                variables={"job_posting_text": job_posting_text},
                language=language,
                temperature=0.3,
                max_tokens=1024
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            logger.info(f"🔍 NORMALIZATION RESPONSE: success={response.success}, provider={response.provider}, model={response.model}")
            if not response.success:
                logger.error(f"🔴 NORMALIZATION FAILED: {response.error}")
            
            return response.data if response.success else None
            
        except Exception as e:
            logger.error(f"Error normalizing job posting: {e}")
            return None
    
    async def generate_executive_recommendation(
        self,
        job_posting_summary: str,
        candidates_data: List[Dict[str, Any]],
        weights: Dict[str, float],
        hard_blockers: List[str],
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Generate an executive recommendation summary for hiring decision.
        
        Args:
            job_posting_summary: Summary of the job position
            candidates_data: List of analyzed candidates with scores
            weights: Category weights used in evaluation
            hard_blockers: Hard blocker rules
            language: Response language
            
        Returns:
            Executive recommendation with top candidate and insights
        """
        try:
            # Build candidates summary for the prompt
            candidates_summary_list = []
            for idx, candidate in enumerate(candidates_data[:5], 1):  # Top 5 only
                name = candidate.get('candidate_label', f'Candidate {idx}')
                score = candidate.get('global_score', 0)
                categories = candidate.get('categories', {})
                strengths = candidate.get('strengths', [])[:3]  # Top 3 strengths
                blockers = candidate.get('hard_blocker_flags', [])
                
                summary_parts = [
                    f"#{idx}: {name}",
                    f"Score: {score}/5",
                    f"Categories: {', '.join(f'{k}={v}' for k, v in categories.items())}",
                    f"Key Strengths: {'; '.join(strengths)}" if strengths else ""
                ]
                
                if blockers:
                    summary_parts.append(f"⚠️ Blockers: {', '.join(blockers)}")
                
                candidates_summary_list.append("\n".join(filter(None, summary_parts)))
            
            candidates_summary = "\n\n".join(candidates_summary_list)
            
            template = get_prompt("executive_recommendation")
            
            variables = {
                "job_posting_summary": job_posting_summary,
                "candidate_count": len(candidates_data),
                "candidates_summary": candidates_summary,
                "weights": json.dumps(weights, indent=2),
                "hard_blockers": "\n".join(f"- {b}" for b in hard_blockers) if hard_blockers else "None specified",
                "language": language
            }
            
            ai_request = AIRequest(
                prompt_type=PromptType.EXECUTIVE_RECOMMENDATION,
                template=template,
                variables=variables,
                language=language,
                temperature=0.6,
                max_tokens=1536
            )
            
            response = await self.ai_manager.execute(ai_request)
            
            if not response.success:
                logger.error(f"Executive recommendation failed: {response.error}")
                return None
            
            return response.data
        
        except Exception as exc:
            logger.error(f"Error generating executive recommendation: {exc}")
            return None


    async def _build_enrichment_context(
        self,
        company_name: Optional[str] = None,
        candidate_id: Optional[UUID] = None,
        candidate_name: Optional[str] = None,
    ) -> str:
        """
        Build enrichment context string using cached Brave Search results.
        Fetches latest company and candidate enrichment data, refreshing via API if needed.
        """
        sections: List[str] = []

        company_data = await self._get_company_enrichment(company_name)
        if company_data:
            formatted = self._format_company_enrichment(company_data)
            if formatted:
                sections.append(formatted)

        candidate_data = await self._get_candidate_enrichment(candidate_id, candidate_name)
        if candidate_data:
            formatted = self._format_candidate_enrichment(candidate_data)
            if formatted:
                sections.append(formatted)

        context = "\n\n".join(section.strip() for section in sections if section).strip()
        return context

    async def _get_company_enrichment(self, company_name: Optional[str]) -> Optional[Dict[str, Any]]:
        """Fetch company enrichment from cache or Brave Search."""
        if not company_name:
            return None

        enrichment = await self.company_enrichment_service.get_latest(company_name, max_age_days=30)
        if enrichment:
            return enrichment

        if not self.brave_service or not self.brave_service.is_enabled():
            return None

        try:
            enrichment_result = await self.brave_service.enrich_company(company_name)
            if enrichment_result:
                enrichment_dict = enrichment_result.dict()
                saved = await self.company_enrichment_service.save(
                    company_name=company_name,
                    enrichment_data=enrichment_dict,
                    expires_in_days=30,
                )
                if saved:
                    return saved
                return enrichment_dict
        except Exception as exc:
            logger.warning(f"Failed to fetch company enrichment via Brave Search: {exc}")
        return None

    async def _get_candidate_enrichment(
        self,
        candidate_id: Optional[UUID],
        candidate_name: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """Fetch candidate enrichment from cache or Brave Search."""
        if not candidate_id:
            return None

        enrichment = await self.candidate_enrichment_service.get_latest(candidate_id)
        if enrichment:
            return enrichment

        if not candidate_name or not self.brave_service or not self.brave_service.is_enabled():
            return None

        try:
            enrichment_result = await self.brave_service.enrich_candidate(candidate_name)
            if enrichment_result:
                enrichment_dict = enrichment_result.dict()
                saved = await self.candidate_enrichment_service.save(
                    candidate_id=candidate_id,
                    candidate_name=candidate_name,
                    enrichment_data=enrichment_dict,
                    expires_in_days=90,
                )
                if saved:
                    return saved
                return enrichment_dict
        except Exception as exc:
            logger.warning(f"Failed to fetch candidate enrichment via Brave Search: {exc}")
        return None

    def _format_company_enrichment(self, data: Dict[str, Any]) -> str:
        """Format company enrichment data into a concise context block."""
        lines: List[str] = []
        company_name = data.get("company_name")
        if company_name:
            lines.append(f"Company: {company_name}")
        if data.get("description"):
            lines.append(f"Summary: {data['description']}")
        if data.get("industry"):
            lines.append(f"Industry: {data['industry']}")
        size = data.get("company_size") or data.get("size")
        if size:
            lines.append(f"Company Size: {size}")
        location = data.get("location") or data.get("headquarters")
        if location:
            lines.append(f"Location: {location}")
        website = data.get("website") or data.get("site")
        if website:
            lines.append(f"Website: {website}")

        social_media = data.get("social_media") or {}
        if isinstance(social_media, dict):
            handles = [
                f"{platform.capitalize()}: {url}"
                for platform, url in social_media.items()
                if url
            ]
            if handles:
                lines.append("Social Links: " + " | ".join(handles))

        recent_news = data.get("recent_news") or []
        if isinstance(recent_news, list) and recent_news:
            news_lines = []
            for item in recent_news[:3]:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("headline")
                    url = item.get("url")
                    age = item.get("age") or item.get("published_at")
                    summary = item.get("description") or item.get("summary")
                    parts = [part for part in [title, age] if part]
                    if parts:
                        line = " • " + " – ".join(parts)
                        if summary:
                            line += f": {summary}"
                        news_lines.append(line)
                    elif url:
                        news_lines.append(f" • {url}")
            if news_lines:
                lines.append("Recent News:\n" + "\n".join(news_lines))

        if not lines:
            return ""
        return "COMPANY ENRICHMENT:\n" + "\n".join(lines)

    def _format_candidate_enrichment(self, data: Dict[str, Any]) -> str:
        """Format candidate enrichment data into a concise context block."""
        lines: List[str] = []
        candidate_name = data.get("candidate_name") or data.get("name")
        if candidate_name:
            lines.append(f"Candidate: {candidate_name}")

        if data.get("professional_summary"):
            lines.append(f"Summary: {data['professional_summary']}")

        links = []
        for field in ("linkedin_profile", "github_profile", "portfolio_url"):
            value = data.get(field)
            if value:
                label = field.replace("_profile", "").replace("_url", "").capitalize()
                links.append(f"{label}: {value}")
        if links:
            lines.append("Links: " + " | ".join(links))

        publications = self._normalize_list_field(data.get("publications"))
        if publications:
            lines.append(
                "Publications:\n" + "\n".join(f"• {item}" for item in publications[:3])
            )

        awards = self._normalize_list_field(data.get("awards"))
        if awards:
            lines.append("Awards:\n" + "\n".join(f"• {item}" for item in awards[:3]))

        if not lines:
            return ""
        return "CANDIDATE ENRICHMENT:\n" + "\n".join(lines)

    @staticmethod
    def _normalize_list_field(value: Any) -> List[str]:
        """Normalize list-like enrichment values into a list of strings."""
        if isinstance(value, list):
            items: List[str] = []
            for item in value:
                if isinstance(item, dict):
                    title = item.get("title") or item.get("name") or item.get("summary")
                    url = item.get("url")
                    if title and url:
                        items.append(f"{title} ({url})")
                    elif title:
                        items.append(title)
                    elif url:
                        items.append(url)
                elif item:
                    items.append(str(item))
            return items
        if isinstance(value, str):
            return [part.strip() for part in value.split(",") if part.strip()]
        return []


# Global service instance
_ai_analysis_service: Optional[AIAnalysisService] = None


def get_ai_analysis_service() -> AIAnalysisService:
    """Get global AI analysis service instance."""
    global _ai_analysis_service
    if _ai_analysis_service is None:
        _ai_analysis_service = AIAnalysisService()
    return _ai_analysis_service

