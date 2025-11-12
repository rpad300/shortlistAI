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

import asyncio
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
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
    existing_report_code: Optional[str] = Field(None, max_length=50, description="Optional: Continue existing report by providing report code")


class InterviewerIdentificationResponse(BaseModel):
    """Response for step 1."""
    interviewer_id: UUID
    session_id: UUID
    report_id: Optional[UUID] = None
    report_code: Optional[str] = None
    is_continuing: bool = False
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
    nice_to_have: List[str] = Field(default=[], description="Preferred but optional requirements")
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
        get_session_service,
        get_report_service
    )
    
    # Check if continuing existing report
    existing_report = None
    if data.existing_report_code:
        report_service = get_report_service()
        existing_report = await report_service.get_by_code(data.existing_report_code)
        
        if not existing_report:
            raise HTTPException(
                status_code=404,
                detail=f"Report code '{data.existing_report_code}' not found"
            )
        
        # Verify the report belongs to this interviewer (by email)
        # We'll validate after finding/creating interviewer
        logger.info(f"Continuing existing report: {data.existing_report_code}")
    
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
        
        # Validate existing report belongs to this interviewer
        if existing_report:
            if existing_report["interviewer_id"] != interviewer_id:
                raise HTTPException(
                    status_code=403,
                    detail="This report belongs to another interviewer"
                )
        
        # 3. Create session for multi-step flow
        initial_session_data = {
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
        
        # If continuing report, load context from DB
        if existing_report:
            initial_session_data.update({
                "report_id": existing_report["id"],
                "report_code": existing_report["report_code"],
                "job_posting_id": existing_report["job_posting_id"],
                "weights": existing_report["weights"],
                "hard_blockers": existing_report.get("hard_blockers", []),
                "nice_to_have": existing_report.get("nice_to_have", []),
                "key_points": existing_report.get("key_points"),
                "structured_job_posting": existing_report.get("structured_job_posting"),
                "is_continuing_report": True
            })
        
        session_id = session_service.create_session(
            flow_type="interviewer",
            user_id=interviewer_id,
            initial_data=initial_session_data
        )
        
        logger.info(f"Session created: {session_id} for interviewer {interviewer_id}")
        
        # 4. TODO: Log audit event (future implementation)
        
        message = f"Welcome {data.name}! "
        if existing_report:
            message += f"Continuing report {existing_report['report_code']}. Skip to step 5 to add more CVs."
        else:
            message += "Proceed to step 2 to add your job posting."
        
        return InterviewerIdentificationResponse(
            interviewer_id=interviewer_id,
            session_id=session_id,
            report_id=UUID(existing_report["id"]) if existing_report else None,
            report_code=existing_report["report_code"] if existing_report else None,
            is_continuing=bool(existing_report),
            message=message
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
        
        # ALWAYS use AI to extract key points from job posting
        # Gemini is default, others are fallbacks
        suggested_key_points = None
        from services.ai_analysis import get_ai_analysis_service
        
        ai_service = get_ai_analysis_service()
        
        # Normalize job posting to extract structured requirements with AI
        # Note: First normalization without company_name (it will be extracted from the result)
        logger.info(f"Using AI to analyze job posting (provider: {ai_service.ai_manager.default_provider})")
        normalized = await ai_service.normalize_job_posting(final_text, language)
        
        if normalized:
            # Build suggested key points from AI analysis
            key_points_parts = []
            
            if normalized.get("required_skills"):
                skills = ", ".join(normalized["required_skills"][:5])
                key_points_parts.append(f"• Required skills: {skills}")
            
            if normalized.get("experience_level"):
                key_points_parts.append(f"• Experience level: {normalized['experience_level']}")
            
            if normalized.get("languages"):
                langs = ", ".join(normalized["languages"])
                key_points_parts.append(f"• Languages: {langs}")
            
            if normalized.get("qualifications"):
                quals = "\n  - ".join(normalized["qualifications"][:3])
                key_points_parts.append(f"• Key qualifications:\n  - {quals}")
            
            if normalized.get("preferred_skills"):
                prefs = ", ".join(normalized["preferred_skills"][:3])
                key_points_parts.append(f"• Nice to have: {prefs}")
            
            suggested_key_points = "\n\n".join(key_points_parts)
            
            # Persist structured data for later steps
            try:
                await job_posting_service.update_structured_data(
                    UUID(job_posting["id"]),
                    normalized
                )
            except Exception as structured_err:  # pragma: no cover - logging only
                logger.warning(
                    "Failed to store structured job posting data: %s",
                    structured_err
                )
            logger.info(f"AI-generated suggested key points ({len(suggested_key_points)} chars)")
        else:
            logger.warning("AI returned no normalized data")
            suggested_key_points = "• Could not extract key points with AI. Please write them manually."
        
        # Update session with job posting ID and suggested key points
        session_service.update_session(
            UUID(session_id),
            {
                "job_posting_id": job_posting["id"],
                "job_posting_text": final_text,  # COMPLETE text (no truncation!)
                "suggested_key_points": suggested_key_points,  # AI-generated suggestions
                "structured_job_posting": normalized
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


@router.get("/step3/suggestions/{session_id}")
async def get_key_points_suggestions(session_id: UUID):
    """
    Get AI-suggested key points based on job posting from Step 2.
    
    Returns suggested key points that user can edit/enhance.
    """
    from services.database import get_session_service
    
    try:
        session_service = get_session_service()
        
        # Get session
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Get AI-suggested key points from session (generated in Step 2)
        suggested_key_points = session["data"].get("suggested_key_points")
        
        if not suggested_key_points:
            # Return empty if AI didn't generate suggestions
            return JSONResponse({
                "status": "success",
                "suggested_key_points": "",
                "has_suggestions": False,
                "message": "No AI suggestions available. Please write your own key points."
            })
        
        return JSONResponse({
            "status": "success",
            "suggested_key_points": suggested_key_points,
            "has_suggestions": True,
            "message": "AI-suggested key points. You can edit or add more."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting suggestions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Error retrieving AI suggestions"
        )


@router.post("/step3")
async def step3_key_points(data: KeyPointsInput):
    """
    Step 3: Key points definition.
    
    Stores interviewer-defined key requirements and priorities.
    User can edit AI-suggested key points or write their own.
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
        
        # Update job posting with key points (user-edited version)
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
        
        logger.info(f"Key points stored (user-edited) for session: {data.session_id}")
        
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


@router.get("/step4/suggestions/{session_id}")
async def get_weighting_suggestions(session_id: UUID):
    """
    Get AI recommendations for category weights, hard blockers, and nice-to-have items.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service
    )
    from services.ai_analysis import get_ai_analysis_service
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        ai_service = get_ai_analysis_service()
        
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Return cached suggestions if already generated in this session
        cached = session["data"].get("weighting_suggestions")
        if cached:
            return JSONResponse({
                "status": "success",
                "has_suggestions": True,
                "weights": cached.get("weights", {}),
                "hard_blockers": cached.get("hard_blockers", []),
                "nice_to_have": cached.get("nice_to_have", []),
                "summary": cached.get("summary", "")
            })
        
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(
                status_code=400,
                detail="Job posting not found. Complete steps 2 and 3 first."
            )
        
        key_points = session["data"].get("key_points") or session["data"].get("suggested_key_points", "")
        job_posting_text = session["data"].get("job_posting_text")
        structured_job_posting = session["data"].get("structured_job_posting")
        
        # Fallback: load from database if session does not have full context
        if not job_posting_text or not structured_job_posting:
            job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
            if job_posting:
                job_posting_text = job_posting_text or job_posting.get("raw_text")
                structured_job_posting = structured_job_posting or job_posting.get("structured_data")
        
        if not job_posting_text:
            return JSONResponse({
                "status": "success",
                "has_suggestions": False,
                "message": "Job posting text missing. Unable to generate AI recommendations."
            })
        
        # Extract company name from structured data if available
        company_name = None
        if structured_job_posting and isinstance(structured_job_posting, dict):
            company_name = structured_job_posting.get("company") or structured_job_posting.get("organization")
        
        suggestions = None
        try:
            logger.info(f"Requesting AI weighting suggestions for session {session_id}")
            suggestions = await asyncio.wait_for(
                ai_service.recommend_weighting_and_blockers(
                    job_posting_text,
                    structured_job_posting,
                    key_points,
                    session["data"].get("language", "en"),
                    company_name=company_name
                ),
                timeout=60  # Increased timeout for large context
            )
            logger.info(f"AI weighting suggestions received: {bool(suggestions)}")
        except asyncio.TimeoutError:
            logger.error("AI weighting recommendation timed out for session %s", session_id)
            raise HTTPException(
                status_code=504,
                detail="AI request timed out. Please try again or check AI provider status."
            )
        except Exception as ai_exc:
            logger.error(
                "AI weighting recommendation failed for session %s: %s",
                session_id,
                ai_exc,
                exc_info=True  # Add full traceback
            )
            raise HTTPException(
                status_code=500,
                detail=f"AI weighting recommendation failed: {str(ai_exc)}"
            )
        
        if not suggestions:
            raise HTTPException(
                status_code=500,
                detail="AI failed to generate weighting suggestions. Cannot proceed without AI."
            )
        
        normalized = {
            "weights": suggestions.get("weights", {}),
            "hard_blockers": suggestions.get("hard_blockers", []),
            "nice_to_have": suggestions.get("nice_to_have", []),
            "summary": suggestions.get("summary", "")
        }
        
        session_service.update_session(
            session_id,
            {"weighting_suggestions": normalized}
        )
        
        return JSONResponse({
            "status": "success",
            "has_suggestions": True,
            **normalized
        })
    
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Error generating weighting suggestions: %s", exc)
        raise HTTPException(
            status_code=500,
            detail="Internal server error generating weighting suggestions"
        )


@router.post("/step4")
async def step4_weighting(data: WeightingInput):
    """
    Step 4: Category weighting and hard blockers.
    
    Stores evaluation weights and hard blocker rules.
    Creates persistent Analysis Report in database.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service,
        get_report_service
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
        report_service = get_report_service()
        
        # Validate session
        session = session_service.get_session(data.session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if continuing existing report
        existing_report_id = session["data"].get("report_id")
        is_continuing = session["data"].get("is_continuing_report", False)
        
        # Get job posting ID
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(
                status_code=400,
                detail="Job posting not found. Complete steps 2 and 3 first."
            )
        
        job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
        
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
        
        # Persist nice-to-have items inside structured data for later use
        if job_posting is not None:
            structured = job_posting.get("structured_data") or {}
            if isinstance(structured, dict):
                structured["nice_to_have"] = data.nice_to_have
                try:
                    await job_posting_service.update_structured_data(
                        UUID(job_posting_id),
                        structured
                    )
                except Exception as structured_err:  # pragma: no cover - logging only
                    logger.warning(
                        "Failed to update structured data with nice-to-have items: %s",
                        structured_err
                    )
        
        # Create or update persistent Report in database
        report = None
        report_code = None
        
        if not is_continuing:
            # Create new report
            interviewer_id = session["data"].get("interviewer_id")
            company_id = session["data"].get("company_id")
            key_points = session["data"].get("key_points") or session["data"].get("suggested_key_points", "")
            structured_job_posting = session["data"].get("structured_job_posting")
            
            report = await report_service.create(
                interviewer_id=UUID(interviewer_id),
                job_posting_id=UUID(job_posting_id),
                weights=data.weights,
                key_points=key_points,
                company_id=UUID(company_id) if company_id else None,
                hard_blockers=data.hard_blockers,
                nice_to_have=data.nice_to_have,
                structured_job_posting=structured_job_posting,
                title=job_posting.get("raw_text", "")[:200] if job_posting else None,
                language=data.language
            )
            
            if report:
                report_code = report["report_code"]
                logger.info(f"Created persistent report: {report_code} ({report['id']})")
            else:
                logger.warning("Failed to create persistent report (non-critical)")
        else:
            # Continuing existing report
            report_id = existing_report_id
            report_code = session["data"].get("report_code")
            logger.info(f"Continuing existing report: {report_code}")
        
        # Update session
        session_update_data = {
            "weights": data.weights,
            "hard_blockers": data.hard_blockers,
            "nice_to_have": data.nice_to_have
        }
        
        if report:
            session_update_data.update({
                "report_id": report["id"],
                "report_code": report["report_code"]
            })
        
        session_service.update_session(
            data.session_id,
            session_update_data,
            step=4
        )
        
        logger.info(f"Weighting configured for session: {data.session_id}")
        
        response_data = {
            "status": "success",
            "message": "Weighting configured. Proceed to step 5 to upload CVs."
        }
        
        if report_code:
            response_data["report_code"] = report_code
            response_data["message"] += f" Report code: {report_code}"
        
        return JSONResponse(response_data)
        
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
    from services.ai_analysis import get_ai_analysis_service
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
        ai_service = get_ai_analysis_service()
        
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
                
                # Generate unique email to avoid duplicates during batch upload
                generated_email = f"interviewer_session_{session_id}_{idx+1}@shortlistai.test"
                candidate = await candidate_service.create(
                    email=generated_email,
                    name=f"Candidate {idx+1}",
                    consent_given=False  # Consent from interviewer, not candidate
                )
                
                if not candidate:
                    errors.append(f"{file.filename}: Failed to create candidate")
                    continue
                
                # Summarize CV with AI (if we have extracted text)
                summary = None
                if extracted_text:
                    summary = await ai_service.summarize_cv(
                        extracted_text,
                        file.filename,
                        session["data"].get("language", "en")
                    )
                else:
                    logger.warning("No extracted text available for %s, skipping AI summary", file.filename)
                
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
                        "filename": file.filename,
                        "summary": summary
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
                "cv_count": len(processed_cvs),
                "candidates_info": processed_cvs,
                "analysis_complete": False,
                "analysis_results": []
            },
            step=5
        )
        
        logger.info(f"Uploaded {len(processed_cvs)} CVs for session: {session_id}")

        response_cvs = [
            {
                "cv_id": info["cv_id"],
                "candidate_id": info["candidate_id"],
                "filename": info["filename"],
                "summary": info.get("summary")
            }
            for info in processed_cvs
        ]
        
        return JSONResponse({
            "status": "success",
            "files_processed": len(processed_cvs),
            "files_failed": len(errors),
            "cvs": response_cvs,
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
        get_analysis_service,
        get_report_service,
        get_candidate_service,
    )
    from services.ai_analysis import get_ai_analysis_service
    from utils import FileProcessor
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        cv_service = get_cv_service()
        analysis_service = get_analysis_service()
        ai_service = get_ai_analysis_service()
        candidate_service = get_candidate_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            raise HTTPException(status_code=400, detail="Job posting not found")
        
        job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
        job_posting_markdown = ""
        if job_posting and job_posting.get("raw_text"):
            job_posting_markdown = FileProcessor.text_to_markdown(job_posting["raw_text"])
        structured_job_posting = (
            session["data"].get("structured_job_posting")
            or (job_posting.get("structured_data") if job_posting else None)
        )
        company_name = None
        if isinstance(structured_job_posting, dict):
            company_name = structured_job_posting.get("company") or structured_job_posting.get("organization")
        
        # Get CV IDs
        cv_ids = session["data"].get("cv_ids", [])
        if len(cv_ids) == 0:
            raise HTTPException(status_code=400, detail="No CVs uploaded. Complete step 5 first.")
        
        # Get weights and blockers
        weights = session["data"].get("weights", {})
        hard_blockers = session["data"].get("hard_blockers", [])
        nice_to_have = session["data"].get("nice_to_have", [])
        key_points = session["data"].get("key_points") or session["data"].get("suggested_key_points", "")
        language = session["data"].get("language", "en")
        candidates_info = session["data"].get("candidates_info", [])

        def _normalize_list(value: Any) -> List[Any]:
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                for key in ("items", "flags", "values", "value"):
                    maybe = value.get(key)
                    if isinstance(maybe, list):
                        return maybe
            if value is None:
                return []
            return [value]
        
        analyses = []
        session_results = []
        candidate_lookup = {info["cv_id"]: info for info in candidates_info}

        for cv_id in cv_ids:
            cv = await cv_service.get_by_id(UUID(cv_id))
            if not cv:
                continue

            candidate_info = candidate_lookup.get(cv_id, {})
            extracted_text = cv.get("extracted_text") or ""
            candidate_uuid: Optional[UUID] = None
            candidate_name: Optional[str] = None
            candidate_id_value = candidate_info.get("candidate_id") or cv.get("candidate_id")
            if candidate_id_value:
                try:
                    candidate_uuid = UUID(str(candidate_id_value))
                    candidate_record = await candidate_service.get_by_id(candidate_uuid)
                    if candidate_record:
                        candidate_name = (
                            candidate_record.get("name")
                            or candidate_record.get("full_name")
                            or candidate_record.get("email")
                        )
                except Exception as candidate_err:
                    logger.warning(f"Failed to fetch candidate details for enrichment: {candidate_err}")
            if not candidate_name:
                summary_info = candidate_info.get("summary") or {}
                candidate_name = summary_info.get("full_name") or candidate_info.get("filename")

            ai_result = None
            cv_markdown = FileProcessor.text_to_markdown(extracted_text) if extracted_text else ""
            
            # Note: Gemini can handle large CVs (4M tokens), no truncation needed

            if not cv_markdown or not job_posting_markdown:
                logger.error("Missing CV or job posting text for analysis. CV ID: %s", cv_id)
                continue

            try:
                ai_result = await asyncio.wait_for(
                    ai_service.analyze_candidate_for_interviewer(
                        job_posting_markdown,
                        cv_markdown,
                        key_points,
                        weights,
                        hard_blockers,
                        nice_to_have,
                        language,
                        company_name=company_name,
                        candidate_id=candidate_uuid,
                        candidate_name=candidate_name,
                    ),
                    timeout=90  # 90 seconds for large context
                )
            except asyncio.TimeoutError:
                logger.error("AI analysis timed out for CV %s", cv_id)
                raise HTTPException(
                    status_code=504,
                    detail=f"AI analysis timed out for CV {cv_id}. Please try again or check AI provider status."
                )
            except Exception as ai_exc:
                logger.error("AI analysis failed for CV %s: %s", cv_id, ai_exc)
                raise HTTPException(
                    status_code=500,
                    detail=f"AI analysis failed for CV {cv_id}: {str(ai_exc)}"
                )

            if not ai_result or not ai_result.get("data"):
                raise HTTPException(
                    status_code=500,
                    detail=f"AI failed to analyze CV {cv_id}. Cannot proceed without AI analysis."
                )

            data = ai_result.get("data", {})
            categories = data.get("categories", {})
            strengths = _normalize_list(data.get("strengths"))
            risks = _normalize_list(data.get("risks"))
            questions = _normalize_list(data.get("custom_questions") or data.get("questions"))
            blocker_flags = _normalize_list(data.get("hard_blocker_violations") or data.get("hard_blocker_flags"))
            recommendation = data.get("recommendation") or ""  # Brief hiring recommendation from AI
            intro_pitch = data.get("intro_pitch") or ""  # Candidate intro pitch
            gap_strategies = _normalize_list(data.get("gap_strategies") or [])  # Strategies to address gaps
            preparation_tips = _normalize_list(data.get("preparation_tips") or [])  # Study topics for interview
            provider_used = ai_result.get("provider") or ai_result.get("model") or "ai"
            
            # Debug: Log what we got from AI
            logger.info(f"AI result for CV {cv_id}: strengths={len(strengths)}, risks={len(risks)}, questions={len(questions)}, blocker_flags={len(blocker_flags)}, has_recommendation={bool(recommendation)}")
            if not questions:
                logger.warning(f"No questions returned from AI for CV {cv_id}. Data keys: {list(data.keys())}")

            global_score = sum(
                categories.get(cat, 0) * weights.get(cat, 1)
                for cat in categories.keys()
            ) / sum(weights.values()) if weights else sum(categories.values()) / len(categories)

            summary = candidate_info.get("summary") or {}
            candidate_label = (
                summary.get("full_name")
                or summary.get("current_role")
                or candidate_info.get("filename")
                or f"Candidate {len(session_results) + 1}"
            )

            # Fetch enrichment data for candidate and company
            enrichment_data = {}
            try:
                from services.database.enrichment_service import (
                    CompanyEnrichmentService,
                    CandidateEnrichmentService
                )
                
                # Get company enrichment
                if company_name:
                    company_enrichment_service = CompanyEnrichmentService()
                    company_enrichment = await company_enrichment_service.get_latest(company_name, max_age_days=30)
                    if company_enrichment:
                        enrichment_data["company"] = {
                            "name": company_enrichment.get("company_name"),
                            "website": company_enrichment.get("website"),
                            "description": company_enrichment.get("description"),
                            "industry": company_enrichment.get("industry"),
                            "size": company_enrichment.get("company_size"),
                            "location": company_enrichment.get("location"),
                            "social_media": company_enrichment.get("social_media", {}),
                            "recent_news": company_enrichment.get("recent_news", []),
                            "ai_summary": company_enrichment.get("ai_summary")
                        }
                
                # Get candidate enrichment
                if candidate_uuid:
                    candidate_enrichment_service = CandidateEnrichmentService()
                    candidate_enrichment = await candidate_enrichment_service.get_latest(candidate_uuid)
                    if candidate_enrichment:
                        enrichment_data["candidate"] = {
                            "name": candidate_enrichment.get("candidate_name") or candidate_enrichment.get("name"),
                            "professional_summary": candidate_enrichment.get("professional_summary"),
                            "linkedin_profile": candidate_enrichment.get("linkedin_profile"),
                            "github_profile": candidate_enrichment.get("github_profile"),
                            "portfolio_url": candidate_enrichment.get("portfolio_url"),
                            "publications": candidate_enrichment.get("publications", []),
                            "awards": candidate_enrichment.get("awards", []),
                            "ai_summary": candidate_enrichment.get("ai_summary")
                        }
            except Exception as enrichment_err:
                logger.warning(f"Failed to fetch enrichment data: {enrichment_err}")

            # Get report_id from session (if exists)
            report_id = session["data"].get("report_id")
            
            analysis = await analysis_service.create(
                mode="interviewer",
                job_posting_id=UUID(job_posting_id),
                cv_id=UUID(cv_id),
                candidate_id=UUID(cv["candidate_id"]),
                provider=provider_used,
                categories=categories,
                global_score=round(global_score, 2),
                strengths=strengths,
                risks=risks,
                questions=questions,
                language=language,
                hard_blocker_flags=blocker_flags,
                report_id=UUID(report_id) if report_id else None
            )
            
            session_results.append({
                "analysis_id": analysis["id"] if analysis else None,
                "candidate_id": str(cv["candidate_id"]),
                "candidate_label": candidate_label,
                "file_name": candidate_info.get("filename"),
                "summary": summary,
                "global_score": round(global_score, 2),
                "categories": categories,
                "strengths": strengths,
                "risks": risks,
                "questions": questions,
                "hard_blocker_flags": blocker_flags,
                "recommendation": recommendation,  # Brief hiring recommendation from AI analysis
                "intro_pitch": intro_pitch,  # Candidate intro pitch
                "gap_strategies": gap_strategies,  # Strategies to address gaps/risks
                "preparation_tips": preparation_tips,  # Study topics for interview
                "provider": provider_used,
                "enrichment": enrichment_data if enrichment_data else None
            })

            if analysis:
                analyses.append(analysis)
        
        # Generate executive recommendation (AI summary of results)
        executive_recommendation = None
        try:
            logger.info(f"Generating executive recommendation for session {session_id}")
            executive_recommendation = await ai_service.generate_executive_recommendation(
                job_posting_summary=key_points or "Position evaluation",
                candidates_data=session_results,
                weights=weights,
                hard_blockers=hard_blockers,
                language=language,
                company_name=company_name
            )
            if executive_recommendation:
                logger.info("Executive recommendation generated successfully")
            else:
                logger.warning("Executive recommendation returned None")
        except Exception as exec_err:
            logger.error(f"Failed to generate executive recommendation: {exec_err}")
            # Continue without recommendation - not critical
        
        # Update persistent report in database (if exists)
        report_id = session["data"].get("report_id")
        if report_id and executive_recommendation:
            try:
                report_service = get_report_service()
                await report_service.update_executive_recommendation(
                    UUID(report_id),
                    executive_recommendation
                )
                # Update candidate count
                await report_service.increment_candidate_count(UUID(report_id), len(analyses))
                logger.info(f"Updated report {report_id} with executive recommendation")
            except Exception as report_err:
                logger.error(f"Failed to update report: {report_err}")
        
        # Update session
        session_service.update_session(
            UUID(session_id),
            {
                "analysis_ids": [a["id"] for a in analyses],
                "analysis_complete": True,
                "analysis_results": session_results,
                "executive_recommendation": executive_recommendation
            },
            step=6
        )
        
        logger.info(f"Analysis complete: {len(analyses)} analyses created for session: {session_id}")
        
        return JSONResponse({
            "status": "success",
            "analyses_created": len(analyses),
            "message": "Analysis complete. View results in step 7.",
            "results": session_results,
            "executive_recommendation": executive_recommendation
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
async def step7_results(
    session_id: UUID,
    report_code: Optional[str] = Query(
        default=None,
        max_length=50,
        description="Optional report code to recover results if session expired"
    )
):
    """
    Step 7: Display results.
    
    Returns ranked list of candidates with scores and details.
    """
    from services.database import (
        get_session_service,
        get_analysis_service,
        get_report_service,
        get_candidate_service
    )
    
    try:
        session_service = get_session_service()
        analysis_service = get_analysis_service()
        
        # Validate session
        session = session_service.get_session(session_id)
        if not session:
            if not report_code:
                raise HTTPException(status_code=404, detail="Session not found or expired")
            
            # Fallback: load results directly from persistent report
            report_service = get_report_service()
            report = await report_service.get_by_code(report_code)
            
            if not report:
                raise HTTPException(
                    status_code=404,
                    detail="Session expired and report code not found. Please restart the analysis."
                )
            
            analyses = await report_service.get_analyses_for_report(UUID(report["id"]))
            
            if not analyses:
                raise HTTPException(
                    status_code=404,
                    detail="No analysis results found for this report yet."
                )
            
            candidate_service = get_candidate_service()
            
            def _ensure_list(value: Any) -> List[Any]:
                if isinstance(value, list):
                    return value
                if isinstance(value, dict):
                    items = value.get("items")
                    if isinstance(items, list):
                        return items
                    flags = value.get("flags")
                    if isinstance(flags, list):
                        return flags
                    values = value.get("value") or value.get("values")
                    if isinstance(values, list):
                        return values
                if value is None:
                    return []
                return [value]
            
            fallback_results: List[Dict[str, Any]] = []
            for idx, analysis in enumerate(analyses, start=1):
                candidate_label = None
                try:
                    candidate = await candidate_service.get_by_id(UUID(analysis["candidate_id"]))
                    if candidate and candidate.get("name"):
                        candidate_label = candidate["name"]
                except Exception as candidate_err:  # pragma: no cover - logging only
                    logger.warning(
                        "Failed to load candidate %s for report fallback: %s",
                        analysis.get("candidate_id"),
                        candidate_err
                    )
                
                fallback_results.append({
                    "analysis_id": analysis["id"],
                    "candidate_id": analysis["candidate_id"],
                    "candidate_label": candidate_label or f"Candidate {idx}",
                    "global_score": analysis.get("global_score", 0),
                    "categories": analysis.get("categories") or {},
                    "strengths": _ensure_list(analysis.get("strengths")),
                    "risks": _ensure_list(analysis.get("risks")),
                    "questions": _ensure_list(analysis.get("questions")),
                    "hard_blocker_flags": _ensure_list(analysis.get("hard_blocker_flags")),
                    "provider": analysis.get("provider")
                })
            
            logger.info(
                "Loaded %d results from persistent report %s for session %s",
                len(fallback_results),
                report_code,
                session_id
            )
            
            return JSONResponse({
                "status": "success",
                "total_candidates": len(fallback_results),
                "results": fallback_results,
                "executive_recommendation": report.get("executive_recommendation"),
                "hard_blockers": report.get("hard_blockers", []),  # Include hard blockers from report
                "message": f"Recovered {len(fallback_results)} candidates from report {report_code}.",
                "report_id": report.get("id"),
                "report_code": report.get("report_code"),
                "source": "report"
            })
        
        # Check if analysis is complete
        if not session["data"].get("analysis_complete"):
            raise HTTPException(
                status_code=400,
                detail="Analysis not complete. Run step 6 first."
            )
        
        report_code_in_session = session["data"].get("report_code")
        results = session["data"].get("analysis_results")
        executive_recommendation = session["data"].get("executive_recommendation")
        
        # Extract company name from structured job posting
        company_name = None
        structured_job_posting = session["data"].get("structured_job_posting")
        if structured_job_posting and isinstance(structured_job_posting, dict):
            company_name = structured_job_posting.get("company") or structured_job_posting.get("organization")
        
        if results:
            # SORT by global_score DESCENDING (best candidates first)
            sorted_results = sorted(
                results,
                key=lambda x: x.get('global_score', 0),
                reverse=True
            )
            
            # Fetch enrichment data for all candidates and ensure all required fields
            from services.database.enrichment_service import (
                CompanyEnrichmentService,
                CandidateEnrichmentService
            )
            company_enrichment_service = CompanyEnrichmentService()
            candidate_enrichment_service = CandidateEnrichmentService()
            
            # Get company enrichment once (same for all candidates)
            company_enrichment_data = None
            if company_name:
                company_enrichment = await company_enrichment_service.get_latest(company_name, max_age_days=30)
                if company_enrichment:
                    company_enrichment_data = {
                        "name": company_enrichment.get("company_name"),
                        "website": company_enrichment.get("website"),
                        "description": company_enrichment.get("description"),
                        "industry": company_enrichment.get("industry"),
                        "size": company_enrichment.get("company_size"),
                        "location": company_enrichment.get("location"),
                        "social_media": company_enrichment.get("social_media", {}),
                        "recent_news": company_enrichment.get("recent_news", []),
                        "ai_summary": company_enrichment.get("ai_summary")
                    }
            
            # Ensure all required fields are present for each result
            for result in sorted_results:
                # Ensure summary is a dict (not None)
                if not result.get("summary") or not isinstance(result.get("summary"), dict):
                    result["summary"] = {}
                # Ensure candidate_label exists
                if not result.get("candidate_label"):
                    summary = result.get("summary", {})
                    result["candidate_label"] = (
                        summary.get("full_name") 
                        or summary.get("current_role")
                        or result.get("file_name")
                        or "Candidate"
                    )
                # Ensure all list fields are arrays
                if not isinstance(result.get("strengths"), list):
                    result["strengths"] = []
                if not isinstance(result.get("risks"), list):
                    result["risks"] = []
                if not isinstance(result.get("questions"), list):
                    result["questions"] = []
                if not isinstance(result.get("hard_blocker_flags"), list):
                    result["hard_blocker_flags"] = []
                # Ensure categories is a dict
                if not isinstance(result.get("categories"), dict):
                    result["categories"] = {}
                # Ensure global_score is a number
                if result.get("global_score") is None:
                    result["global_score"] = 0
                # Ensure recommendation exists (can be empty string)
                if "recommendation" not in result:
                    result["recommendation"] = ""
                # Ensure intro_pitch exists (can be empty string)
                if "intro_pitch" not in result:
                    result["intro_pitch"] = ""
                # Ensure gap_strategies is a list
                if not isinstance(result.get("gap_strategies"), list):
                    result["gap_strategies"] = []
                # Ensure preparation_tips is a list
                if not isinstance(result.get("preparation_tips"), list):
                    result["preparation_tips"] = []
                
                # Fetch or update enrichment data for this candidate
                enrichment_data = result.get("enrichment") or {}
                try:
                    candidate_id = result.get("candidate_id")
                    if candidate_id:
                        candidate_enrichment = await candidate_enrichment_service.get_latest(UUID(candidate_id))
                        if candidate_enrichment:
                            enrichment_data["candidate"] = {
                                "name": candidate_enrichment.get("candidate_name") or candidate_enrichment.get("name"),
                                "professional_summary": candidate_enrichment.get("professional_summary"),
                                "linkedin_profile": candidate_enrichment.get("linkedin_profile"),
                                "github_profile": candidate_enrichment.get("github_profile"),
                                "portfolio_url": candidate_enrichment.get("portfolio_url"),
                                "publications": candidate_enrichment.get("publications", []),
                                "awards": candidate_enrichment.get("awards", []),
                                "ai_summary": candidate_enrichment.get("ai_summary"),
                                "result_count": candidate_enrichment.get("result_count", 0)
                            }
                except Exception as enrichment_err:
                    logger.warning(f"Failed to fetch candidate enrichment for step7: {enrichment_err}")
                
                # Add company enrichment if available
                if company_enrichment_data:
                    enrichment_data["company"] = company_enrichment_data
                
                # Set enrichment (can be empty dict if no data)
                result["enrichment"] = enrichment_data if enrichment_data else None
            
            logger.info("Returning %d analysis results from session cache for %s", len(sorted_results), session_id)
            if sorted_results:
                first_result = sorted_results[0]
                logger.info("Step7 first result fields: analysis_id=%s, candidate_id=%s, candidate_label=%s, global_score=%s, strengths_count=%d, risks_count=%d, questions_count=%d, has_enrichment=%s",
                    first_result.get("analysis_id"),
                    first_result.get("candidate_id"),
                    first_result.get("candidate_label"),
                    first_result.get("global_score"),
                    len(first_result.get("strengths", [])),
                    len(first_result.get("risks", [])),
                    len(first_result.get("questions", [])),
                    "yes" if first_result.get("enrichment") else "no"
                )
            
            # Get hard blockers from session
            hard_blockers = session["data"].get("hard_blockers", [])
            
            return JSONResponse({
                "status": "success",
                "total_candidates": len(sorted_results),
                "results": sorted_results,
                "executive_recommendation": executive_recommendation,
                "hard_blockers": hard_blockers,  # Include hard blockers (must-have requirements) in response
                "message": f"Analysis complete for {len(sorted_results)} candidates.",
                "report_code": report_code_in_session,
                "source": "session"
            })
        
        # Fallback: query database (legacy)
        job_posting_id = session["data"].get("job_posting_id")
        analyses = await analysis_service.get_by_job_posting(UUID(job_posting_id))
        
        # Format results
        results = []
        def _ensure_list(value: Any) -> List[Any]:
            if isinstance(value, list):
                return value
            if isinstance(value, dict):
                items = value.get("items")
                if isinstance(items, list):
                    return items
                flags = value.get("flags")
                if isinstance(flags, list):
                    return flags
                values = value.get("value") or value.get("values")
                if isinstance(values, list):
                    return values
            if value is None:
                return []
            return [value]

        for analysis in analyses:
            results.append({
                "analysis_id": analysis["id"],
                "candidate_id": analysis["candidate_id"],
                "global_score": analysis["global_score"],
                "categories": analysis["categories"],
                "strengths": _ensure_list(analysis.get("strengths")),
                "risks": _ensure_list(analysis.get("risks")),
                "questions": _ensure_list(analysis.get("questions")),
                "hard_blocker_flags": _ensure_list(analysis.get("hard_blocker_flags")),
                "provider": analysis.get("provider")
            })
        
        # SORT by global_score DESCENDING (best candidates first)
        sorted_results = sorted(
            results,
            key=lambda x: x.get('global_score', 0),
            reverse=True
        )
        
        logger.info(f"Results retrieved: {len(sorted_results)} candidates for session: {session_id}")
        
        # Get executive recommendation from session (if available)
        executive_recommendation = session["data"].get("executive_recommendation")
        
        return JSONResponse({
            "status": "success",
            "total_candidates": len(sorted_results),
            "results": sorted_results,
            "executive_recommendation": executive_recommendation,
            "hard_blockers": hard_blockers,  # Include hard blockers (must-have requirements) in response
            "message": f"Analysis complete for {len(sorted_results)} candidates.",
            "report_code": report_code_in_session,
            "source": "session-db"
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
    Step 8: Download PDF report.
    
    Generates and returns a comprehensive PDF report of the analysis.
    Includes job details, evaluation criteria, executive recommendation, and candidate rankings.
    """
    from services.database import get_session_service
    from services.pdf import get_pdf_report_generator
    from fastapi.responses import Response
    
    try:
        session_service = get_session_service()
        pdf_generator = get_pdf_report_generator()
        
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if analysis is complete
        if not session["data"].get("analysis_complete"):
            raise HTTPException(
                status_code=400,
                detail="Analysis not complete. Complete step 6 first."
            )
        
        # Get results and executive recommendation
        results = session["data"].get("analysis_results", [])
        executive_recommendation = session["data"].get("executive_recommendation")
        
        if not results:
            raise HTTPException(
                status_code=400,
                detail="No analysis results found"
            )
        
        # Generate PDF
        logger.info(f"Generating PDF report for session: {session_id}")
        pdf_bytes = pdf_generator.generate_interviewer_report(
            session_data=session,
            results=results,
            executive_recommendation=executive_recommendation
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"candidate_analysis_report_{timestamp}.pdf"
        
        logger.info(f"PDF report generated successfully: {len(pdf_bytes)} bytes")
        
        # Return PDF file
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}",
                "Content-Length": str(len(pdf_bytes))
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating PDF report: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF report: {str(e)}"
        )

