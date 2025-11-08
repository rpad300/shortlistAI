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

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
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
    session_id: str = Form(...),
    raw_text: Optional[str] = Form(None),
    language: str = Form("en"),
    file: Optional[UploadFile] = File(None)
):
    """
    Step 2: Job posting input.
    
    Accepts the job posting the candidate is applying for.
    Can be provided as text or file upload.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service
    )
    from services.storage import get_storage_service
    from utils import FileProcessor
    from uuid import UUID
    
    if not raw_text and not file:
        raise HTTPException(
            status_code=400,
            detail="Either text or file must be provided"
        )
    
    try:
        # Get services
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        storage_service = get_storage_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        final_text = raw_text or ""
        file_url = None
        
        # Handle file upload
        if file:
            # Validate file
            is_valid, error = FileProcessor.validate_file_type(file.filename)
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            # Read file content
            file_content = await file.read()
            
            # Validate size
            is_valid, error = FileProcessor.validate_file_size(len(file_content))
            if not is_valid:
                raise HTTPException(status_code=400, detail=error)
            
            # Upload to storage
            success, url, error = await storage_service.upload_job_posting(
                file_content,
                file.filename,
                session_id
            )
            
            if not success:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload file: {error}"
                )
            
            file_url = url
            
            # Extract text from file
            success, extracted_text, error = FileProcessor.extract_text(
                file_content,
                file.filename
            )
            
            if success and extracted_text:
                final_text = extracted_text
                logger.info(f"Extracted {len(extracted_text)} chars from {file.filename}")
        
        # Create job posting record
        job_posting = await job_posting_service.create(
            raw_text=final_text,
            candidate_id=session["data"].get("candidate_id"),
            file_url=file_url,
            language=language
        )
        
        if not job_posting:
            raise HTTPException(
                status_code=500,
                detail="Failed to create job posting record"
            )
        
        # Update session with job posting ID
        session_service.update_session(
            UUID(session_id),
            {
                "job_posting_id": job_posting["id"],
                "job_posting_text": final_text[:500]
            },
            step=2
        )
        
        logger.info(f"Job posting created: {job_posting['id']} for candidate session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "job_posting_id": job_posting["id"],
            "text_length": len(final_text),
            "message": "Job posting stored successfully. Proceed to step 3 to upload your CV."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step2_job_posting: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing job posting"
        )


@router.post("/step3")
async def step3_upload_cv(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Step 3: CV upload.
    
    Accepts candidate's CV file.
    """
    from services.database import (
        get_session_service,
        get_cv_service
    )
    from services.storage import get_storage_service
    from utils import FileProcessor
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        cv_service = get_cv_service()
        storage_service = get_storage_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        candidate_id = session["data"].get("candidate_id")
        if not candidate_id:
            raise HTTPException(status_code=400, detail="Candidate ID not found in session")
        
        # Validate file
        is_valid, error = FileProcessor.validate_file_type(file.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Read file content
        file_content = await file.read()
        
        # Validate size
        is_valid, error = FileProcessor.validate_file_size(len(file_content))
        if not is_valid:
            raise HTTPException(status_code=400, detail=error)
        
        # Upload to storage
        success, file_url, error = await storage_service.upload_cv(
            file_content,
            file.filename,
            candidate_id
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload CV: {error}"
            )
        
        # Extract text from file
        success, extracted_text, error = FileProcessor.extract_text(
            file_content,
            file.filename
        )
        
        if not success or not extracted_text:
            logger.warning(f"Could not extract text from CV: {error}")
            extracted_text = ""
        
        # Create CV record
        cv = await cv_service.create(
            candidate_id=UUID(candidate_id),
            file_url=file_url,
            uploaded_by_flow="candidate",
            extracted_text=extracted_text
        )
        
        if not cv:
            raise HTTPException(
                status_code=500,
                detail="Failed to create CV record"
            )
        
        # Update session
        session_service.update_session(
            UUID(session_id),
            {
                "cv_id": cv["id"],
                "cv_text_length": len(extracted_text)
            },
            step=3
        )
        
        logger.info(f"CV uploaded: {cv['id']} for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "cv_id": cv["id"],
            "text_length": len(extracted_text),
            "message": "CV uploaded successfully. Proceed to step 4 for AI analysis."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step3_upload_cv: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error uploading CV"
        )


@router.post("/step4")
async def step4_analysis(session_id: str):
    """
    Step 4: Trigger AI analysis.
    
    Runs AI analysis of candidate's fit for the job posting.
    Returns preparation guidance.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service,
        get_cv_service,
        get_analysis_service
    )
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        cv_service = get_cv_service()
        analysis_service = get_analysis_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get job posting and CV
        job_posting_id = session["data"].get("job_posting_id")
        cv_id = session["data"].get("cv_id")
        candidate_id = session["data"].get("candidate_id")
        
        if not all([job_posting_id, cv_id, candidate_id]):
            raise HTTPException(
                status_code=400,
                detail="Missing required data. Complete steps 2 and 3 first."
            )
        
        # Placeholder analysis (TODO: Use actual AI)
        categories = {
            "technical_skills": 4,
            "experience": 3,
            "soft_skills": 5,
            "languages": 5,
            "education": 4
        }
        
        global_score = sum(categories.values()) / len(categories)
        
        # Create analysis record
        analysis = await analysis_service.create(
            mode="candidate",
            job_posting_id=UUID(job_posting_id),
            cv_id=UUID(cv_id),
            candidate_id=UUID(candidate_id),
            provider="placeholder",
            categories=categories,
            global_score=round(global_score, 2),
            strengths=[
                "Strong technical background",
                "Excellent communication skills",
                "Relevant experience"
            ],
            risks=[
                "Limited experience with cloud platforms",
                "No formal certifications"
            ],
            questions=[
                "Tell me about your experience with Python",
                "How do you handle team conflicts?",
                "What are your career goals?"
            ],
            intro_pitch="I'm a passionate developer with 5 years of experience...",
            language=session["data"].get("language", "en")
        )
        
        if not analysis:
            raise HTTPException(
                status_code=500,
                detail="Failed to create analysis"
            )
        
        # Update session
        session_service.update_session(
            UUID(session_id),
            {
                "analysis_id": analysis["id"],
                "analysis_complete": True
            },
            step=4
        )
        
        logger.info(f"Candidate analysis complete: {analysis['id']}")
        
        return JSONResponse({
            "status": "success",
            "analysis_id": analysis["id"],
            "message": "Analysis complete. View results in step 5."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step4_analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis"
        )


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
    from services.database import get_session_service, get_analysis_service
    
    try:
        session_service = get_session_service()
        analysis_service = get_analysis_service()
        
        # Validate session
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get analysis ID
        analysis_id = session["data"].get("analysis_id")
        if not analysis_id:
            raise HTTPException(
                status_code=400,
                detail="Analysis not found. Complete step 4 first."
            )
        
        # Fetch analysis
        analysis = await analysis_service.get_by_id(UUID(analysis_id))
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Format response
        return CandidateAnalysisResponse(
            session_id=session_id,
            categories=analysis["categories"],
            strengths=analysis.get("strengths", {}).get("items", []),
            gaps=analysis.get("risks", {}).get("items", []),
            questions=analysis.get("questions", {}).get("items", []),
            suggested_answers=[
                "Use STAR method: Situation, Task, Action, Result",
                "Quantify your achievements with specific metrics",
                "Be honest about gaps and show willingness to learn",
                "Prepare specific examples from your experience"
            ],
            intro_pitch=analysis.get("intro_pitch", ""),
            language=analysis["language"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step5_results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving results"
        )


@router.post("/step6/email")
async def step6_send_email(
    session_id: str,
    recipient_email: EmailStr
):
    """
    Step 6: Send email summary.
    
    Sends preparation guide to candidate's email.
    """
    from services.database import get_session_service, get_analysis_service
    from services.email import get_email_service
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        analysis_service = get_analysis_service()
        email_service = get_email_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get analysis
        analysis_id = session["data"].get("analysis_id")
        if not analysis_id:
            raise HTTPException(status_code=400, detail="Analysis not found")
        
        analysis = await analysis_service.get_by_id(UUID(analysis_id))
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Send email
        success = await email_service.send_candidate_preparation(
            to_email=recipient_email,
            candidate_name=session["data"].get("candidate_name", "Candidate"),
            job_title="Position",
            scores=analysis["categories"],
            questions=analysis.get("questions", {}).get("items", []),
            intro_pitch=analysis.get("intro_pitch", ""),
            language=analysis["language"]
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to send email")
        
        logger.info(f"Preparation email sent to {recipient_email}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Preparation guide sent to {recipient_email}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error sending email"
        )


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

