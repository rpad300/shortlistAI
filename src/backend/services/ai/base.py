"""
Base classes for AI service providers.

Defines the interface that all AI providers must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from enum import Enum


class PromptType(str, Enum):
    """Types of AI prompts supported by the platform."""
    CV_EXTRACTION = "cv_extraction"
    JOB_POSTING_NORMALIZATION = "job_posting_normalization"
    INTERVIEWER_ANALYSIS = "interviewer_analysis"
    CANDIDATE_ANALYSIS = "candidate_analysis"
    WEIGHTING_RECOMMENDATION = "weighting_recommendation"
    CV_SUMMARY = "cv_summary"
    EXECUTIVE_RECOMMENDATION = "executive_recommendation"
    EMAIL_SUMMARY_INTERVIEWER = "email_summary_interviewer"
    EMAIL_SUMMARY_CANDIDATE = "email_summary_candidate"
    TRANSLATION = "translation"


class AIRequest(BaseModel):
    """Base request for AI operations."""
    prompt_type: PromptType
    template: str
    variables: Dict[str, Any]
    language: str = "en"
    max_tokens: Optional[int] = None
    temperature: Optional[float] = 0.7


class AIResponse(BaseModel):
    """Base response from AI operations."""
    success: bool
    data: Optional[Dict[str, Any]] = None
    raw_text: Optional[str] = None
    error: Optional[str] = None
    provider: str
    model: Optional[str] = None
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost_usd: Optional[float] = None


class AIProvider(ABC):
    """
    Abstract base class for AI service providers.
    
    All AI providers (Gemini, OpenAI, Claude, etc.) must implement this interface.
    """
    
    def __init__(self, api_key: str, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AI provider.
        
        Args:
            api_key: API key for the provider
            config: Optional provider-specific configuration
        """
        self.api_key = api_key
        self.config = config or {}
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
    
    @abstractmethod
    async def complete(self, request: AIRequest) -> AIResponse:
        """
        Execute an AI completion request.
        
        Args:
            request: The AI request to process
            
        Returns:
            AIResponse with results or error
        """
        pass
    
    @abstractmethod
    async def extract_structured_data(
        self,
        text: str,
        schema: Dict[str, Any],
        language: str = "en"
    ) -> AIResponse:
        """
        Extract structured data from text according to a schema.
        
        Args:
            text: Source text to extract from
            schema: JSON schema describing expected structure
            language: Language for AI to understand context
            
        Returns:
            AIResponse with extracted data
        """
        pass
    
    def build_prompt(self, template: str, variables: Dict[str, Any]) -> str:
        """
        Build a complete prompt from template and variables.
        
        Args:
            template: Prompt template with placeholders
            variables: Values to substitute into template
            
        Returns:
            Complete prompt string
        """
        prompt = template
        for key, value in variables.items():
            placeholder = "{" + key + "}"
            prompt = prompt.replace(placeholder, str(value))
        return prompt
    
    async def health_check(self) -> bool:
        """
        Check if the provider is accessible and healthy.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            # Simple test request
            test_request = AIRequest(
                prompt_type=PromptType.TRANSLATION,
                template="Translate 'hello' to {language}",
                variables={"language": "Portuguese"},
                language="en",
                max_tokens=10
            )
            response = await self.complete(test_request)
            return response.success
        except Exception:
            return False

