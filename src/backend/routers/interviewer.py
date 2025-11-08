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
    from services.database import (
        get_session_service,
        get_cv_service,
        get_candidate_service
    )
    from services.storage import get_storage_service
    from utils import FileProcessor
    from uuid import UUID
    
    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="At least one CV file must be uploaded"
        )
    
    try:
        session_service = get_session_service()
        cv_service = get_cv_service()
        candidate_service = get_candidate_service()
        storage_service = get_storage_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        processed_cvs = []
        errors = []
        
        # Process each CV file
        for idx, file in enumerate(files):
            try:
                # Validate file
                is_valid, error = FileProcessor.validate_file_type(file.filename)
                if not is_valid:
                    errors.append(f"{file.filename}: {error}")
                    continue
                
                # Read file
                file_content = await file.read()
                
                # Validate size
                is_valid, error = FileProcessor.validate_file_size(len(file_content))
                if not is_valid:
                    errors.append(f"{file.filename}: {error}")
                    continue
                
                # Extract text to try to find email for deduplication
                success, extracted_text, error = FileProcessor.extract_text(
                    file_content,
                    file.filename
                )
                
                if not success or not extracted_text:
                    extracted_text = ""
                
                # For now, create anonymous candidate for each CV
                # In production, we'd use AI to extract email from CV text
                candidate = await candidate_service.create(
                    email=f"candidate_{idx+1}@temp.com",  # TODO: Extract from CV with AI
                    name=f"Candidate {idx+1}",  # TODO: Extract from CV with AI
                    consent_given=False  # Consent from interviewer, not candidate
                )
                
                if not candidate:
                    errors.append(f"{file.filename}: Failed to create candidate")
                    continue
                
                # Upload CV file
                success, file_url, error = await storage_service.upload_cv(
                    file_content,
                    file.filename,
                    candidate["id"]
                )
                
                if not success:
                    errors.append(f"{file.filename}: {error}")
                    continue
                
                # Create CV record
                cv = await cv_service.create(
                    candidate_id=UUID(candidate["id"]),
                    file_url=file_url,
                    uploaded_by_flow="interviewer",
                    extracted_text=extracted_text
                )
                
                if cv:
                    processed_cvs.append({
                        "cv_id": cv["id"],
                        "candidate_id": candidate["id"],
                        "filename": file.filename
                    })
                    logger.info(f"CV processed: {file.filename} -> {cv['id']}")
                
            except Exception as e:
                errors.append(f"{file.filename}: {str(e)}")
                logger.error(f"Error processing CV {file.filename}: {e}")
        
        if len(processed_cvs) == 0:
            raise HTTPException(
                status_code=400,
                detail=f"No CVs could be processed. Errors: {errors}"
            )
        
        # Update session with CV IDs
        session_service.update_session(
            UUID(session_id),
            {
                "cv_ids": [cv["cv_id"] for cv in processed_cvs],
                "cv_count": len(processed_cvs)
            },
            step=5
        )
        
        logger.info(f"Uploaded {len(processed_cvs)} CVs for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "files_processed": len(processed_cvs),
            "files_failed": len(errors),
            "cvs": processed_cvs,
            "errors": errors if errors else None,
            "message": f"Uploaded {len(processed_cvs)} CVs. Proceed to step 6 for AI analysis."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step5_upload_cvs: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error uploading CVs"
        )


@router.post("/step6")
async def step6_analysis(session_id: str):
    """
    Step 6: Trigger AI analysis.
    
    Runs AI analysis for all uploaded CVs against the job posting.
    Returns analysis results with rankings.
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
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(status_code=400, detail="Job posting not found")
        
        job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
        
        # Get CV IDs
        cv_ids = session["data"].get("cv_ids", [])
        if len(cv_ids) == 0:
            raise HTTPException(status_code=400, detail="No CVs uploaded. Complete step 5 first.")
        
        # Get weights and blockers
        weights = session["data"].get("weights", {})
        hard_blockers = session["data"].get("hard_blockers", [])
        
        # For now, create placeholder analyses
        # TODO: Call AI service for actual analysis
        analyses = []
        for cv_id in cv_ids:
            cv = await cv_service.get_by_id(UUID(cv_id))
            if not cv:
                continue
            
            # Placeholder analysis
            categories = {
                "technical_skills": 4,
                "experience": 3,
                "soft_skills": 4,
                "languages": 5,
                "education": 4
            }
            
            # Calculate weighted global score
            global_score = sum(
                categories.get(cat, 0) * weights.get(cat, 1)
                for cat in categories.keys()
            ) / sum(weights.values()) if weights else sum(categories.values()) / len(categories)
            
            # Create analysis record
            analysis = await analysis_service.create(
                mode="interviewer",
                job_posting_id=UUID(job_posting_id),
                cv_id=UUID(cv_id),
                candidate_id=UUID(cv["candidate_id"]),
                provider="placeholder",  # TODO: Use actual AI provider
                categories=categories,
                global_score=round(global_score, 2),
                strengths=["Strong technical background", "Good communication"],
                risks=["Limited experience in X"],
                questions=["Tell me about your experience with Y"],
                language=session["data"].get("language", "en")
            )
            
            if analysis:
                analyses.append(analysis)
        
        # Update session
        session_service.update_session(
            UUID(session_id),
            {
                "analysis_ids": [a["id"] for a in analyses],
                "analysis_complete": True
            },
            step=6
        )
        
        logger.info(f"Analysis complete: {len(analyses)} analyses created for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "analyses_created": len(analyses),
            "message": "Analysis complete. View results in step 7."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step6_analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis"
        )


@router.get("/step7/{session_id}")
async def step7_results(session_id: UUID):
    """
    Step 7: Display results.
    
    Returns ranked list of candidates with scores and details.
    """
    from services.database import get_session_service, get_analysis_service
    
    try:
        session_service = get_session_service()
        analysis_service = get_analysis_service()
        
        # Validate session
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if analysis is complete
        if not session["data"].get("analysis_complete"):
            raise HTTPException(
                status_code=400,
                detail="Analysis not complete. Run step 6 first."
            )
        
        # Get all analyses for this job posting
        job_posting_id = session["data"].get("job_posting_id")
        analyses = await analysis_service.get_by_job_posting(UUID(job_posting_id))
        
        # Format results
        results = []
        for analysis in analyses:
            results.append({
                "analysis_id": analysis["id"],
                "candidate_id": analysis["candidate_id"],
                "global_score": analysis["global_score"],
                "categories": analysis["categories"],
                "strengths": analysis.get("strengths", {}).get("items", []),
                "risks": analysis.get("risks", {}).get("items", []),
                "questions": analysis.get("questions", {}).get("items", []),
                "hard_blocker_flags": analysis.get("hard_blocker_flags", {}).get("flags", [])
            })
        
        logger.info(f"Results retrieved: {len(results)} candidates for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "total_candidates": len(results),
            "results": results,
            "message": f"Analysis complete for {len(results)} candidates."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step7_results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving results"
        )


@router.post("/step8/email")
async def step8_send_email(
    session_id: str,
    recipient_email: EmailStr
):
    """
    Step 8: Send email summary.
    
    Sends analysis summary to interviewer's email.
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
        
        # Get analyses
        job_posting_id = session["data"].get("job_posting_id")
        analyses = await analysis_service.get_by_job_posting(UUID(job_posting_id))
        
        # Prepare top candidates for email
        top_candidates = [
            {
                "name": f"Candidate {idx+1}",
                "score": analysis.get("global_score", 0)
            }
            for idx, analysis in enumerate(analyses[:5])
        ]
        
        # Send email
        success = await email_service.send_interviewer_summary(
            to_email=recipient_email,
            interviewer_name=session["data"].get("interviewer_name", "Interviewer"),
            job_title="Position",  # TODO: Extract from job posting
            candidate_count=len(analyses),
            top_candidates=top_candidates,
            language=session["data"].get("language", "en")
        )
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send email"
            )
        
        logger.info(f"Email sent to {recipient_email} for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "message": f"Summary email sent to {recipient_email}"
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sending email: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error sending email"
        )


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

