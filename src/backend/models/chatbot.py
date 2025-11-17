"""
Pydantic models for Chatbot CV Preparation feature.

All models follow the same patterns as existing candidate/interviewer models
but are separate to avoid interference with existing flows.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr, validator


# =============================================================================
# Request Models
# =============================================================================

class ChatbotWelcomeRequest(BaseModel):
    """Initial welcome request to start chatbot session."""
    language: str = Field(default="en", description="Language for conversation")
    consent_read_cv: bool = Field(..., description="Consent to read CV")
    consent_read_job_opportunity: bool = Field(..., description="Consent to read job opportunity")
    consent_analyze_links: bool = Field(..., description="Consent to analyze public links")
    consent_store_data: bool = Field(..., description="Consent to store data")
    
    @validator('consent_read_cv', 'consent_read_job_opportunity', 
               'consent_analyze_links', 'consent_store_data')
    def all_consents_required(cls, v):
        if not v:
            raise ValueError('All consents must be given to proceed')
        return v


class ChatbotMessageRequest(BaseModel):
    """Send a message to the chatbot."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    message: str = Field(..., min_length=1, max_length=5000, description="User message")
    message_type: str = Field(default="text", description="Type of message (text, file_upload)")


class ChatbotProfileDataRequest(BaseModel):
    """Update profile data during conversation."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    name: str = Field(..., min_length=1, max_length=200, description="Full name")
    email: EmailStr = Field(..., description="Email address")
    phone: Optional[str] = Field(None, max_length=50, description="Phone number")
    location: Optional[str] = Field(None, max_length=200, description="City and country")
    links: Dict[str, Optional[str]] = Field(
        default_factory=dict,
        description="Dictionary of links (linkedin, github, portfolio, etc.)"
    )


class ChatbotCVUploadRequest(BaseModel):
    """Upload CV in chatbot context."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    # File upload handled separately via FormData


class ChatbotJobOpportunityRequest(BaseModel):
    """Provide job opportunity in chatbot context."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    job_opportunity_text: Optional[str] = Field(None, max_length=50000, description="Job posting text")
    job_opportunity_url: Optional[str] = Field(None, max_length=500, description="URL to job posting")
    # File upload handled separately via FormData


class ChatbotAnswerQuestionRequest(BaseModel):
    """Answer a dynamically generated question."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    question_id: str = Field(..., description="ID of the question being answered")
    answer: str = Field(..., min_length=1, max_length=5000, description="Answer to the question")


class ChatbotCVRegenerationRequest(BaseModel):
    """Request CV regeneration with specific instructions."""
    session_id: UUID = Field(..., description="Chatbot session ID")
    version_type: str = Field(default="ats_friendly", description="Type of CV version")
    instructions: Optional[str] = Field(None, max_length=1000, description="Specific instructions for changes")
    language: str = Field(default="en", description="Language for CV output")


# =============================================================================
# Response Models
# =============================================================================

class ChatbotMessage(BaseModel):
    """Single message in conversation."""
    id: UUID
    role: str = Field(..., description="Message role: user, bot, or system")
    content: str = Field(..., description="Message content")
    message_type: str = Field(default="text", description="Type of message")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class ChatbotSessionResponse(BaseModel):
    """Chatbot session information."""
    session_id: UUID
    candidate_id: Optional[UUID]
    current_step: str
    status: str
    language: str
    messages: List[ChatbotMessage] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ChatbotWelcomeResponse(BaseModel):
    """Response to welcome request."""
    session_id: UUID
    message: str
    current_step: str
    next_actions: List[str] = Field(default_factory=list)


class ChatbotBotMessageResponse(BaseModel):
    """Response containing bot's message."""
    message: ChatbotMessage
    current_step: str
    next_suggested_actions: Optional[List[str]] = None
    progress_indicator: Optional[str] = None


class ChatbotQuestionsResponse(BaseModel):
    """Response containing dynamically generated questions."""
    questions: List[Dict[str, Any]] = Field(..., description="List of questions to ask")
    current_step: str
    total_questions: int
    questions_answered: int


class ChatbotCVPreviewResponse(BaseModel):
    """Response containing generated CV preview."""
    version_type: str
    cv_content: str
    ats_score: Optional[int] = None
    keyword_match_score: Optional[int] = None
    changes_summary: str = Field(..., description="Summary of changes made")
    language: str


class ChatbotInterviewPrepResponse(BaseModel):
    """Response containing interview preparation materials."""
    likely_questions: List[Dict[str, Any]]
    suggested_answers: List[Dict[str, Any]]
    key_stories: List[Dict[str, Any]]
    preparation_summary: str
    questions_to_ask: List[str]


class ChatbotEmployabilityScoreResponse(BaseModel):
    """Response containing employability score and analysis."""
    overall_score: int = Field(..., ge=0, le=100)
    technical_skills_score: Optional[int] = Field(None, ge=0, le=100)
    experience_score: Optional[int] = Field(None, ge=0, le=100)
    communication_score: Optional[int] = Field(None, ge=0, le=100)
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    explanation: str = Field(..., description="Human-readable explanation of the score")


class ChatbotJobRiskAssessmentResponse(BaseModel):
    """Response containing job opportunity risk assessment."""
    quality_score: Optional[int] = Field(None, ge=0, le=100)
    positive_points: List[str]
    red_flags: List[str]
    questions_to_ask: List[str]
    company_summary: Optional[str] = None


class ChatbotDigitalFootprintResponse(BaseModel):
    """Response containing digital footprint analysis."""
    linkedin_analysis: Optional[Dict[str, Any]] = None
    github_analysis: Optional[Dict[str, Any]] = None
    portfolio_analysis: Optional[Dict[str, Any]] = None
    inconsistencies: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ChatbotCompletionResponse(BaseModel):
    """Response when chatbot flow is completed."""
    session_id: UUID
    status: str
    summary: str
    generated_assets: Dict[str, Any] = Field(default_factory=dict)
    next_steps: List[str] = Field(default_factory=list)

