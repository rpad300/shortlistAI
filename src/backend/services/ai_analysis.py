"""
AI Analysis service - High-level service for CV and candidate analysis.

Uses AI providers to analyze CVs against job postings.
"""

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
    
    async def analyze_candidate_for_interviewer(
        self,
        job_posting_text: str,
        cv_text: str,
        key_points: str,
        weights: Dict[str, float],
        hard_blockers: List[str],
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
            
            # Return structured data
            return response.data
            
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
            
            return response.data
            
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


# Global service instance
_ai_analysis_service: Optional[AIAnalysisService] = None


def get_ai_analysis_service() -> AIAnalysisService:
    """Get global AI analysis service instance."""
    global _ai_analysis_service
    if _ai_analysis_service is None:
        _ai_analysis_service = AIAnalysisService()
    return _ai_analysis_service

