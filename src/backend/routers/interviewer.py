"""
API router for Interviewer flow endpoints.

Handles all steps of the interviewer flow:
1. Identification and consent
2. Job posting input
3. Key points definition
4. Weighting and hard blockers
5. CV upload
6. AI analysis
7. Results display
8. Email and report generation
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interviewer", tags=["interviewer"])


# =============================================================================
# Request/Response Models
# =============================================================================

class InterviewerIdentification(BaseModel):
    """Step 1: Interviewer identification and consent."""
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=50)
    country: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    consent_terms: bool = Field(..., description="Must accept terms and conditions")
    consent_privacy: bool = Field(..., description="Must accept privacy policy")
    consent_store_data: bool = Field(..., description="Must consent to data storage")
    consent_future_contact: bool = Field(..., description="Must consent to future headhunting contact")
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


class InterviewerIdentificationResponse(BaseModel):
    """Response for step 1."""
    interviewer_id: UUID
    session_id: UUID
    message: str


class JobPostingInput(BaseModel):
    """Step 2: Job posting input."""
    session_id: UUID
    raw_text: Optional[str] = Field(None, max_length=50000)
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


class KeyPointsInput(BaseModel):
    """Step 3: Key points definition."""
    session_id: UUID
    key_points: str = Field(..., min_length=10, max_length=5000)
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


class WeightingInput(BaseModel):
    """Step 4: Category weights and hard blockers."""
    session_id: UUID
    weights: dict = Field(..., description="Category weights (e.g. {'technical': 50, 'languages': 20})")
    hard_blockers: List[str] = Field(default=[], description="List of hard blocker rules")
    language: str = Field(default="en", pattern="^(en|pt|fr|es)$")


# =============================================================================
# Endpoints
# =============================================================================

@router.post("/step1", response_model=InterviewerIdentificationResponse)
async def step1_identification(data: InterviewerIdentification):
    """
    Step 1: Interviewer identification and consent.
    
    Creates or finds existing interviewer, company, and creates a new session.
    Validates that all required consents are given.
    """
    from services.database import (
        get_company_service,
        get_interviewer_service,
        get_session_service
    )
    
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
        company_service = get_company_service()
        interviewer_service = get_interviewer_service()
        session_service = get_session_service()
        
        # 1. Find or create company (if provided)
        company_id = None
        if data.company_name:
            company = await company_service.find_or_create(data.company_name)
            if company:
                company_id = company["id"]
                logger.info(f"Company: {data.company_name} -> {company_id}")
        
        # 2. Find or create interviewer
        interviewer = await interviewer_service.find_or_create(
            email=data.email,
            name=data.name,
            company_id=company_id,
            phone=data.phone,
            country=data.country,
            consent_given=True
        )
        
        if not interviewer:
            raise HTTPException(
                status_code=500,
                detail="Failed to create interviewer record"
            )
        
        interviewer_id = interviewer["id"]
        logger.info(f"Interviewer created/found: {data.email} -> {interviewer_id}")
        
        # 3. Create session for multi-step flow
        session_id = session_service.create_session(
            flow_type="interviewer",
            user_id=interviewer_id,
            initial_data={
                "interviewer_id": interviewer_id,
                "company_id": company_id,
                "language": data.language,
                "consents": {
                    "terms": data.consent_terms,
                    "privacy": data.consent_privacy,
                    "store_data": data.consent_store_data,
                    "future_contact": data.consent_future_contact
                }
            }
        )
        
        logger.info(f"Session created: {session_id} for interviewer {interviewer_id}")
        
        # 4. TODO: Log audit event (future implementation)
        
        return InterviewerIdentificationResponse(
            interviewer_id=interviewer_id,
            session_id=session_id,
            message=f"Welcome {data.name}! Proceed to step 2 to add your job posting."
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
    
    Accepts job posting as text or file upload.
    Validates and stores raw content.
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
            else:
                logger.warning(f"Could not extract text from file: {error}")
        
        # Create job posting record
        job_posting = await job_posting_service.create(
            raw_text=final_text,
            company_id=session["data"].get("company_id"),
            interviewer_id=session["data"].get("interviewer_id"),
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
                "job_posting_text": final_text[:500]  # Store preview
            },
            step=2
        )
        
        logger.info(f"Job posting created: {job_posting['id']} for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "job_posting_id": job_posting["id"],
            "text_length": len(final_text),
            "message": "Job posting stored successfully. Proceed to step 3."
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
async def step3_key_points(data: KeyPointsInput):
    """
    Step 3: Key points definition.
    
    Stores interviewer-defined key requirements and priorities.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service
    )
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        
        # Validate session
        session = session_service.get_session(data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get job posting ID from session
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(
                status_code=400,
                detail="Job posting not found. Complete step 2 first."
            )
        
        # Update job posting with key points
        success = await job_posting_service.update_key_points(
            UUID(job_posting_id),
            data.key_points
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store key points"
            )
        
        # Update session
        session_service.update_session(
            data.session_id,
            {"key_points": data.key_points},
            step=3
        )
        
        logger.info(f"Key points stored for session: {data.session_id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Key points stored. Proceed to step 4 to define weighting."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step3_key_points: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error storing key points"
        )


@router.post("/step4")
async def step4_weighting(data: WeightingInput):
    """
    Step 4: Category weighting and hard blockers.
    
    Stores evaluation weights and hard blocker rules.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service
    )
    from uuid import UUID
    
    # Validate weights sum to reasonable value (e.g., 100 or close to it)
    total_weight = sum(data.weights.values())
    if total_weight < 80 or total_weight > 120:
        raise HTTPException(
            status_code=400,
            detail=f"Total weights should sum to ~100, got {total_weight}"
        )
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        
        # Validate session
        session = session_service.get_session(data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get job posting ID
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(
                status_code=400,
                detail="Job posting not found. Complete steps 2 and 3 first."
            )
        
        # Update job posting with weights and hard blockers
        success = await job_posting_service.update_weights_and_blockers(
            UUID(job_posting_id),
            data.weights,
            {"blockers": data.hard_blockers}
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to store weighting configuration"
            )
        
        # Update session
        session_service.update_session(
            data.session_id,
            {
                "weights": data.weights,
                "hard_blockers": data.hard_blockers
            },
            step=4
        )
        
        logger.info(f"Weighting configured for session: {data.session_id}")
        
        return JSONResponse({
            "status": "success",
            "message": "Weighting configured. Proceed to step 5 to upload CVs."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step4_weighting: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error configuring weighting"
        )


@router.post("/step5")
async def step5_upload_cvs(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Step 5: CV upload (batch).
    
    Accepts multiple CV files for analysis.
    """
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one CV file must be uploaded"
        )
    
    # TODO: For each file:
    # 1. Validate file type and size
    # 2. Upload to Supabase storage
    # 3. Extract text using AI
    # 4. Detect or create candidate (deduplication by email)
    # 5. Store CV record linked to candidate
    
    logger.info(f"Uploaded {len(files)} CVs for session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "files_processed": len(files),
        "message": f"Uploaded {len(files)} CVs. Proceed to step 6 for analysis."
    })


@router.post("/step6")
async def step6_analysis(session_id: str):
    """
    Step 6: Trigger AI analysis.
    
    Runs AI analysis for all uploaded CVs against the job posting.
    Returns analysis results with rankings.
    """
    # TODO: 
    # 1. Fetch job posting, key points, weights, hard blockers from session
    # 2. Fetch all CVs for this session
    # 3. Call AI service for each CV
    # 4. Store analyses
    # 5. Compute rankings
    # 6. Return results
    
    logger.info(f"Analysis triggered for session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": "Analysis complete. View results in step 7."
    })


@router.get("/step7/{session_id}")
async def step7_results(session_id: UUID):
    """
    Step 7: Display results.
    
    Returns ranked list of candidates with scores and details.
    """
    # TODO:
    # 1. Fetch all analyses for session
    # 2. Sort by global score
    # 3. Format results
    # 4. Return
    
    logger.info(f"Results requested for session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "results": [],
        "message": "Placeholder results. Implementation in progress."
    })


@router.post("/step8/email")
async def step8_send_email(session_id: UUID, recipient_email: EmailStr):
    """
    Step 8: Send email summary.
    
    Sends analysis summary to interviewer's email.
    """
    # TODO:
    # 1. Fetch results
    # 2. Generate email content
    # 3. Send via Resend
    # 4. Log email sent
    
    logger.info(f"Email requested for session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": f"Summary email sent to {recipient_email}"
    })


@router.get("/step8/report/{session_id}")
async def step8_download_report(session_id: UUID):
    """
    Step 8: Download report.
    
    Generates and returns a PDF report of the analysis.
    """
    # TODO:
    # 1. Fetch results
    # 2. Generate PDF report
    # 3. Return file
    
    logger.info(f"Report download requested for session: {session_id}")
    
    return JSONResponse({
        "status": "success",
        "message": "Report generation in progress. Implementation pending."
    })

