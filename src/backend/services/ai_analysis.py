"""
AI Analysis service - High-level service for CV and candidate analysis.

Uses AI providers to analyze CVs against job postings.
"""

import json
from typing import Dict, Any, List, Optional
from services.ai import get_ai_manager, AIRequest, PromptType
from services.ai.prompts import get_prompt
import logging

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """
    High-level service for AI-powered CV analysis.
    
    Orchestrates AI calls for different analysis scenarios.
    """
    
    def __init__(self):
        self.ai_manager = get_ai_manager()
    
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
        language: str = "en"
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
            
            # Prepare variables
            variables = {
                "job_posting": job_posting_text,
                "cv_text": cv_text,
                "key_points": key_points,
                "weights": str(weights),
                "hard_blockers": str(hard_blockers),
                "nice_to_have": str(nice_to_have),
                "language": language
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
        language: str = "en"
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze fit for candidate mode (self-preparation).
        
        Args:
            job_posting_text: Job posting content
            cv_text: CV content
            language: Response language
            
        Returns:
            Analysis dict with categories, strengths, gaps, questions, pitch
        """
        try:
            # Get prompt template
            template = get_prompt("candidate_analysis")
            
            # Prepare variables
            variables = {
                "job_posting": job_posting_text,
                "cv_text": cv_text,
                "language": language
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
            
            ai_request = AIRequest(
                prompt_type=PromptType.JOB_POSTING_NORMALIZATION,
                template=template,
                variables={"job_posting_text": job_posting_text},
                language=language,
                temperature=0.3,
                max_tokens=1024
            )
            
            response = await self.ai_manager.execute(ai_request)
            
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


# Global service instance
_ai_analysis_service: Optional[AIAnalysisService] = None


def get_ai_analysis_service() -> AIAnalysisService:
    """Get global AI analysis service instance."""
    global _ai_analysis_service
    if _ai_analysis_service is None:
        _ai_analysis_service = AIAnalysisService()
    return _ai_analysis_service

