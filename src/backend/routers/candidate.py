"""
API router for Candidate flow endpoints.

Handles all steps of the candidate flow:
1. Identification and consent
2. Job posting input
3. CV upload
4. AI analysis
5. Results display
6. Email and report generation
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/candidate", tags=["candidate"])


# =============================================================================
# Request/Response Models
# =============================================================================

class CandidateIdentification(BaseModel):
    """Step 1: Candidate identification and consent."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    consent_terms: bool = Field(..., description="Must accept terms and conditions")
    consent_privacy: bool = Field(..., description="Must accept privacy policy")
    consent_store_data: bool = Field(..., description="Must consent to data storage")
    consent_future_contact: bool = Field(..., description="Must consent to future headhunting contact")
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


class CandidateIdentificationResponse(BaseModel):
    """Response for step 1."""
    candidate_id: UUID
    session_id: UUID
    message: str


class CandidateJobPostingInput(BaseModel):
    """Step 2: Job posting input."""
    session_id: UUID
    raw_text: Optional[str] = Field(None, max_length=50000)
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


class CandidateAnalysisResponse(BaseModel):
    """Response for analysis results."""
    session_id: UUID
    categories: dict
    strengths: list
    gaps: list
    questions: list
    suggested_answers: list
    intro_pitch: str
    language: str


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/step1", response_model=CandidateIdentificationResponse)
async def step1_identification(data: CandidateIdentification):
    """
    Step 1: Candidate identification and consent.
    
    Creates or finds existing candidate and creates a new session.
    Validates that all required consents are given.
    """
    from services.database import get_candidate_service, get_session_service
    
    # Validate all consents are true
    if not all([
        data.consent_terms,
        data.consent_privacy,
        data.consent_store_data,
        data.consent_future_contact
    ]):
        raise HTTPException(
            status_code=400,
            detail="All consents must be accepted to proceed"
        )
    
    try:
        # Get services
        candidate_service = get_candidate_service()
        session_service = get_session_service()
        
        # 1. Find or create candidate (deduplication by email)
        candidate = await candidate_service.find_or_create(
            email=data.email,
            name=data.name,
            phone=data.phone,
            country=data.country,
            consent_given=True
        )
        
        if not candidate:
            raise HTTPException(
                status_code=500,
                detail="Failed to create candidate record"
            )
        
        candidate_id = candidate["id"]
        logger.info(f"Candidate created/found: {data.email} -> {candidate_id}")
        
        # 2. Create session for multi-step flow
        session_id = session_service.create_session(
            flow_type="candidate",
            user_id=candidate_id,
            initial_data={
                "candidate_id": candidate_id,
                "language": data.language,
                "consents": {
                    "terms": data.consent_terms,
                    "privacy": data.consent_privacy,
                    "store_data": data.consent_store_data,
                    "future_contact": data.consent_future_contact
                }
            }
        )
        
        logger.info(f"Session created: {session_id} for candidate {candidate_id}")
        
        # 3. TODO: Log audit event (future implementation)
        
        return CandidateIdentificationResponse(
            candidate_id=candidate_id,
            session_id=session_id,
            message=f"Welcome {data.name}! Proceed to step 2 to add the job posting."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step1_identification: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during identification"
        )


@router.post("/step2")
async def step2_job_posting(
    data: Optional[CandidateJobPostingInput] = None,
    file: Optional[UploadFile] = File(None)
):
    """
    Step 2: Job posting input.
    
    Accepts the job posting the candidate is applying for.
    Can be provided as text or file upload.
    """
    if not data and not file:
        raise HTTPException(
            status_code=400,
            detail="Either text or file must be provided"
        )
    
    if file:
        # TODO: Validate file type (PDF, DOCX)
        # TODO: Upload to Supabase storage
        # TODO: Extract text from file
        logger.info(f"Job posting file uploaded: {file.filename}")
    
    if data and data.raw_text:
        # TODO: Store raw text linked to session
        logger.info(f"Job posting text provided for session: {data.session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": "Job posting stored. Proceed to step 3 to upload your CV."
    })


@router.post("/step3")
async def step3_upload_cv(
    session_id: str,
    file: UploadFile = File(...)
):
    """
    Step 3: CV upload.
    
    Accepts candidate's CV file.
    """
    # TODO: 
    # 1. Validate file type and size
    # 2. Upload to Supabase storage
    # 3. Extract text using AI
    # 4. Link to candidate and session
    # 5. Store CV record
    
    logger.info(f"CV uploaded for session: {session_id}, file: {file.filename}")
    
    return JSONResponse({
        "status": "success",
        "message": "CV uploaded successfully. Proceed to step 4 for analysis."
    })


@router.post("/step4")
async def step4_analysis(session_id: str):
    """
    Step 4: Trigger AI analysis.
    
    Runs AI analysis of candidate's fit for the job posting.
    Returns preparation guidance.
    """
    # TODO:
    # 1. Fetch job posting and CV from session
    # 2. Call AI service (candidate mode)
    # 3. Store analysis
    # 4. Return results
    
    logger.info(f"Analysis triggered for candidate session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": "Analysis complete. View results in step 5."
    })


@router.get("/step5/{session_id}", response_model=CandidateAnalysisResponse)
async def step5_results(session_id: UUID):
    """
    Step 5: Display results.
    
    Returns analysis results with:
    - Scores per category
    - Strengths and gaps
    - Likely interview questions
    - Suggested answer structures
    - Intro pitch
    """
    # TODO:
    # 1. Fetch analysis from database
    # 2. Format results
    # 3. Return
    
    logger.info(f"Results requested for candidate session: {session_id}")
    
    # Placeholder response
    return CandidateAnalysisResponse(
        session_id=session_id,
        categories={
            "technical_skills": 4,
            "experience": 3,
            "soft_skills": 4,
            "languages": 5
        },
        strengths=[
            "Strong technical background in Python and React",
            "Excellent communication skills",
            "Fluent in multiple languages"
        ],
        gaps=[
            "Limited experience with cloud platforms",
            "No formal project management certification"
        ],
        questions=[
            "Tell me about your experience with Python and FastAPI",
            "How do you handle disagreements in a team?",
            "What cloud platforms have you worked with?"
        ],
        suggested_answers=[
            "Mention specific projects and quantify achievements",
            "Use STAR method: Situation, Task, Action, Result",
            "Be honest about gaps and show willingness to learn"
        ],
        intro_pitch="I'm a full-stack developer with 5 years of experience in Python and React...",
        language="en"
    )


@router.post("/step6/email")
async def step6_send_email(session_id: UUID, recipient_email: EmailStr):
    """
    Step 6: Send email summary.
    
    Sends preparation guide to candidate's email.
    """
    # TODO:
    # 1. Fetch results
    # 2. Generate email content in candidate's language
    # 3. Send via Resend
    # 4. Log email sent
    
    logger.info(f"Email requested for candidate session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": f"Preparation guide sent to {recipient_email}"
    })


@router.get("/step6/report/{session_id}")
async def step6_download_report(session_id: UUID):
    """
    Step 6: Download report.
    
    Generates and returns a PDF preparation guide.
    """
    # TODO:
    # 1. Fetch results
    # 2. Generate PDF report
    # 3. Return file
    
    logger.info(f"Report download requested for candidate session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": "Report generation in progress. Implementation pending."
    })

