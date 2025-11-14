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
    language: str = Form("en"),  # Keep for backward compatibility, but use session language
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
        
        # Use language from session (set in step1), fallback to form parameter
        session_language = session["data"].get("language", language)
        
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
        
        # Validate required data from session
        interviewer_id = session["data"].get("interviewer_id")
        if not interviewer_id:
            logger.error(
                f"Session {session_id} missing interviewer_id. "
                f"Session data keys: {list(session.get('data', {}).keys())}"
            )
            raise HTTPException(
                status_code=400,
                detail="Session missing interviewer_id. Please complete step 1 first."
            )
        
        # Validate job posting text
        if not final_text or not final_text.strip():
            logger.error(f"Empty job posting text for session {session_id}")
            raise HTTPException(
                status_code=400,
                detail="Job posting text cannot be empty"
            )
        
        # Create job posting record
        try:
            logger.info(
                f"Creating job posting for session {session_id}: "
                f"text_length={len(final_text)}, "
                f"company_id={session['data'].get('company_id')}, "
                f"interviewer_id={interviewer_id}, "
                f"language={session_language}"
            )
            
            job_posting = await job_posting_service.create(
                raw_text=final_text,
                company_id=session["data"].get("company_id"),
                interviewer_id=UUID(interviewer_id) if isinstance(interviewer_id, str) else interviewer_id,
                file_url=file_url,
                language=session_language
            )
            
            if not job_posting:
                logger.error(
                    f"job_posting_service.create() returned None for session: {session_id}. "
                    f"company_id={session['data'].get('company_id')}, "
                    f"interviewer_id={interviewer_id}"
                )
                raise HTTPException(
                    status_code=500,
                    detail="Failed to create job posting record. Please try again."
                )
        except ValueError as ve:
            # Validation error from service
            logger.error(
                f"Validation error creating job posting for session {session_id}: {ve}",
                exc_info=True
            )
            raise HTTPException(
                status_code=400,
                detail=f"Invalid job posting data: {str(ve)}"
            )
        except HTTPException:
            raise
        except Exception as e:
            logger.error(
                f"Exception in job_posting_service.create() for session {session_id}: {type(e).__name__}: {e}",
                exc_info=True
            )
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create job posting record: {str(e)}"
            )
        
        # ALWAYS use AI to extract key points from job posting
        # Gemini is default, others are fallbacks
        suggested_key_points = None
        from services.ai_analysis import get_ai_analysis_service
        
        ai_service = get_ai_analysis_service()
        
        # Normalize job posting to extract structured requirements with AI
        # Note: First normalization without company_name (it will be extracted from the result)
        logger.info(f"Using AI to analyze job posting (provider: {ai_service.ai_manager.default_provider}, language: {session_language})")
        normalized = await ai_service.normalize_job_posting(final_text, session_language)
        
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


async def _run_cv_upload_background(session_id: UUID, files_data: List[Dict[str, Any]], 
                                    session_service, cv_service, candidate_service,
                                    storage_service, ai_service):
    """
    Background task to process CV uploads sequentially.
    Updates progress in session as it goes.
    """
    from utils import FileProcessor
    from uuid import UUID
    
    try:
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found in background task")
            return
        
        session_data = session.get("data", {})
        language = session_data.get("language", "en")
        total_files = len(files_data)
        
        processed_cvs = []
        errors = []
        
        # Initialize progress
        session_service.update_session(
            session_id,
            {
                "upload_status": "running",
                "upload_progress": {
                    "current": 0,
                    "total": total_files,
                    "status": "Starting upload...",
                    "current_filename": None
                }
            }
        )
        
        # Process each CV file SEQUENTIALLY
        for idx, file_data in enumerate(files_data, 1):
            filename = file_data["filename"]
            file_content = file_data["content"]
            
            try:
                # Update progress
                session_service.update_session(
                    session_id,
                    {
                        "upload_progress": {
                            "current": idx,
                            "total": total_files,
                            "status": f"Processing CV {idx} of {total_files}: {filename}",
                            "current_filename": filename
                        }
                    }
                )
                
                logger.info(f"🔄 Processing CV {idx}/{total_files}: {filename} ({len(file_content)} bytes)")
                
                # Validate file
                is_valid, error = FileProcessor.validate_file_type(filename)
                if not is_valid:
                    errors.append(f"{filename}: {error}")
                    continue
                
                # Validate size
                is_valid, error = FileProcessor.validate_file_size(len(file_content))
                if not is_valid:
                    errors.append(f"{filename}: {error}")
                    continue
                
                # Extract text
                success, extracted_text, error = FileProcessor.extract_text(
                    file_content,
                    filename
                )
                
                if not success or not extracted_text:
                    extracted_text = ""
                    logger.warning(f"No text extracted from {filename}")
                
                # Generate unique email to avoid duplicates during batch upload
                generated_email = f"interviewer_session_{session_id}_{idx}@shortlistai.test"
                try:
                    candidate = await candidate_service.create(
                        email=generated_email,
                        name=f"Candidate {idx}",
                        consent_given=False  # Consent from interviewer, not candidate
                    )
                except Exception as e:
                    error_detail = str(e)
                    logger.error(
                        f"Failed to create candidate for {filename}: {error_detail}",
                        exc_info=True
                    )
                    errors.append(f"{filename}: Failed to create candidate - {error_detail}")
                    continue
                
                if not candidate:
                    error_msg = f"candidate_service.create() returned None for {filename}"
                    logger.error(error_msg)
                    errors.append(f"{filename}: Failed to create candidate (service returned None)")
                    continue
                
                # Upload CV file FIRST (before AI processing to avoid memory issues)
                success, file_url, error = await storage_service.upload_cv(
                    file_content,
                    filename,
                    candidate["id"]
                )
                
                if not success:
                    errors.append(f"{filename}: {error}")
                    continue
                
                # Create CV record
                cv = await cv_service.create(
                    candidate_id=UUID(candidate["id"]),
                    file_url=file_url,
                    uploaded_by_flow="interviewer",
                    extracted_text=extracted_text
                )
                
                if not cv:
                    errors.append(f"{filename}: Failed to create CV record")
                    continue
                
                # Summarize CV with AI AFTER upload (if we have extracted text)
                summary = None
                if extracted_text:
                    try:
                        # Limit text length for summary to avoid token issues
                        summary_text = extracted_text[:5000] if len(extracted_text) > 5000 else extracted_text
                        summary = await ai_service.summarize_cv(
                            summary_text,
                            filename,
                            language
                        )
                        logger.info(f"Summary generated for {filename}")
                    except Exception as summary_error:
                        logger.warning(f"Failed to generate summary for {filename}: {summary_error}")
                        summary = None
                else:
                    logger.warning(f"No extracted text available for {filename}, skipping AI summary")
                
                processed_cvs.append({
                    "cv_id": cv["id"],
                    "candidate_id": candidate["id"],
                    "filename": filename,
                    "summary": summary
                })
                logger.info(f"✅ CV {idx}/{total_files} processed: {filename} -> {cv['id']}")
                
                # Clear file_content from memory after processing
                del file_content
                
            except Exception as e:
                errors.append(f"{filename}: {str(e)}")
                logger.error(f"Error processing CV {filename}: {e}", exc_info=True)
        
        # Update session with results
        if len(processed_cvs) > 0:
            # Log summary
            logger.info(f"✅ Upload completed: {len(processed_cvs)}/{total_files} CVs processed successfully for session: {session_id}")
            if errors:
                logger.warning(f"⚠️ {len(errors)} CV(s) failed during upload: {errors}")
            
            session_service.update_session(
                session_id,
                {
                    "cv_ids": [cv["cv_id"] for cv in processed_cvs],
                    "cv_count": len(processed_cvs),
                    "candidates_info": processed_cvs,
                    "analysis_complete": False,
                    "analysis_results": [],
                    "upload_status": "complete",
                    "upload_progress": {
                        "current": total_files,
                        "total": total_files,
                        "status": f"Completed: {len(processed_cvs)}/{total_files} CV(s) processed successfully",
                        "current_filename": None
                    },
                    "upload_errors": errors if errors else [],
                    "upload_summary": {
                        "total_files": total_files,
                        "processed": len(processed_cvs),
                        "failed": len(errors),
                        "errors": errors if errors else []
                    }
                },
                step=5
            )
        else:
            # All failed
            logger.error(f"❌ Upload failed: No CVs processed for session: {session_id}. Errors: {errors}")
            session_service.update_session(
                session_id,
                {
                    "upload_status": "failed",
                    "upload_progress": {
                        "current": 0,
                        "total": total_files,
                        "status": f"Upload failed: No CVs could be processed ({len(errors)} error(s))",
                        "current_filename": None
                    },
                    "upload_errors": errors,
                    "upload_summary": {
                        "total_files": total_files,
                        "processed": 0,
                        "failed": len(errors),
                        "errors": errors
                    }
                }
            )
        
    except Exception as e:
        logger.error(f"Error in _run_cv_upload_background for session {session_id}: {e}", exc_info=True)
        try:
            session_service.update_session(
                session_id,
                {
                    "upload_status": "failed",
                    "upload_progress": {
                        "status": f"Error: {str(e)}",
                        "current_filename": None
                    }
                }
            )
        except:
            pass


@router.post("/step5")
async def step5_upload_cvs(
    session_id: str = Form(...),
    files: List[UploadFile] = File(...)
):
    """
    Step 5: CV upload (batch) - async processing.
    
    Accepts multiple CV files and processes them in the background.
    Returns immediately. Use GET /step5/progress/{session_id} to check progress.
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
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if upload is already running
        if session["data"].get("upload_status") == "running":
            return JSONResponse({
                "status": "already_running",
                "message": "CV upload is already in progress",
                "total_files": len(files)
            })
        
        # Read all files into memory (we need to pass them to background task)
        # This is acceptable since we're processing sequentially in background
        files_data = []
        for file in files:
            try:
                file_content = await file.read()
                if len(file_content) == 0:
                    logger.warning(f"File {file.filename} is empty, skipping")
                    continue
                files_data.append({
                    "filename": file.filename,
                    "content": file_content
                })
                logger.info(f"✅ File {file.filename} read successfully ({len(file_content)} bytes)")
            except Exception as e:
                logger.error(f"❌ Error reading file {file.filename}: {e}", exc_info=True)
        
        if len(files_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="No files could be read"
            )
        
        # Get services for background task
        cv_service = get_cv_service()
        candidate_service = get_candidate_service()
        storage_service = get_storage_service()
        ai_service = get_ai_analysis_service()
        
        # Start background task
        asyncio.create_task(_run_cv_upload_background(
            UUID(session_id),
            files_data,
            session_service,
            cv_service,
            candidate_service,
            storage_service,
            ai_service
        ))
        
        return JSONResponse({
            "status": "started",
            "message": f"Upload started for {len(files_data)} CV(s). Processing in background...",
            "total_files": len(files_data)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step5_upload_cvs: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error starting CV upload"
        )


async def _run_analysis_background(session_id: UUID, session_service, job_posting_service, cv_service, 
                                    analysis_service, ai_service, candidate_service, report_service):
    """
    Background task to run AI analysis sequentially for all CVs.
    Updates progress in session as it goes.
    """
    try:
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found in background task")
            return
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        if not job_posting_id:
            logger.error(f"Job posting not found for session {session_id}")
            return
        
        job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
        job_posting_markdown = ""
        if job_posting and job_posting.get("raw_text"):
            from utils import FileProcessor
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
        total_cvs = len(cv_ids)
        
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
        errors = []
        
        # Initialize progress
        session_service.update_session(
            session_id,
            {
                "analysis_status": "running",
                "analysis_progress": {
                    "current": 0,
                    "total": total_cvs,
                    "status": "Starting analysis..."
                }
            }
        )
        
        for idx, cv_id in enumerate(cv_ids, 1):
            cv = None
            candidate_info = candidate_lookup.get(cv_id, {})
            try:
                # Update progress
                session_service.update_session(
                    session_id,
                    {
                        "analysis_progress": {
                            "current": idx,
                            "total": total_cvs,
                            "status": f"Analyzing CV {idx} of {total_cvs}...",
                            "current_cv_id": cv_id
                        }
                    }
                )
                
                cv = await cv_service.get_by_id(UUID(cv_id))
                if not cv:
                    logger.warning(f"CV {cv_id} not found, adding to results with error")
                    error_msg = f"CV {idx}: CV record not found in database"
                    errors.append(error_msg)
                    # Still add to results so it appears in step7
                    summary = candidate_info.get("summary") or {}
                    candidate_label = (
                        summary.get("full_name")
                        or summary.get("current_role")
                        or candidate_info.get("filename")
                        or f"Candidate {idx}"
                    )
                    session_results.append({
                        "analysis_id": None,
                        "candidate_id": str(cv_id),
                        "candidate_label": candidate_label,
                        "file_name": candidate_info.get("filename"),
                        "summary": summary,
                        "global_score": 0,
                        "categories": {},
                        "strengths": [],
                        "risks": [error_msg],
                        "questions": [],
                        "hard_blocker_flags": [],
                        "recommendation": "CV record not found",
                        "intro_pitch": "",
                        "gap_strategies": [],
                        "preparation_tips": [],
                        "provider": None,
                        "enrichment": None,
                        "error": error_msg
                    })
                    continue
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

                from utils import FileProcessor
                cv_markdown = FileProcessor.text_to_markdown(extracted_text) if extracted_text else ""

                if not cv_markdown or not job_posting_markdown:
                    logger.error(f"Missing CV or job posting text for analysis. CV ID: {cv_id}")
                    error_msg = f"CV {idx}: Missing text content"
                    errors.append(error_msg)
                    # Still add to results so it appears in step7
                    summary = candidate_info.get("summary") or {}
                    candidate_label = (
                        summary.get("full_name")
                        or summary.get("current_role")
                        or candidate_info.get("filename")
                        or f"Candidate {idx}"
                    )
                    session_results.append({
                        "analysis_id": None,
                        "candidate_id": str(cv.get("candidate_id")) if cv and cv.get("candidate_id") else str(cv_id),
                        "candidate_label": candidate_label,
                        "file_name": candidate_info.get("filename"),
                        "summary": summary,
                        "global_score": 0,
                        "categories": {},
                        "strengths": [],
                        "risks": [error_msg],
                        "questions": [],
                        "hard_blocker_flags": [],
                        "recommendation": "Missing CV or job posting text",
                        "intro_pitch": "",
                        "gap_strategies": [],
                        "preparation_tips": [],
                        "provider": None,
                        "enrichment": None,
                        "error": error_msg
                    })
                    continue

                # Run AI analysis
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
                    timeout=300  # 5 minutes per CV
                )

                if not ai_result or not ai_result.get("data"):
                    error_msg = f"CV {idx}: AI failed to analyze"
                    errors.append(error_msg)
                    # Still add to results so it appears in step7
                    summary = candidate_info.get("summary") or {}
                    candidate_label = (
                        summary.get("full_name")
                        or summary.get("current_role")
                        or candidate_info.get("filename")
                        or f"Candidate {idx}"
                    )
                    candidate_id_str = str(cv.get("candidate_id")) if cv and cv.get("candidate_id") else str(cv_id)
                    # Create partial analysis record even when AI fails, so it appears in step7
                    try:
                        partial_analysis = await analysis_service.create(
                            mode="interviewer",
                            job_posting_id=UUID(job_posting_id),
                            cv_id=UUID(cv_id),
                            candidate_id=UUID(candidate_id_str),
                            provider="error",
                            categories={},
                            global_score=0,
                            strengths=[],
                            risks=[error_msg],
                            questions={"items": []},
                            intro_pitch="",
                            hard_blocker_flags=[],
                            language=language,
                            detailed_analysis={"error": error_msg, "status": "failed"}
                        )
                        analysis_id = partial_analysis["id"] if partial_analysis else None
                    except Exception as analysis_err:
                        logger.error(f"Failed to create partial analysis for CV {cv_id}: {analysis_err}", exc_info=True)
                        analysis_id = None
                    
                    session_results.append({
                        "analysis_id": str(analysis_id) if analysis_id else None,
                        "candidate_id": str(cv.get("candidate_id")) if cv and cv.get("candidate_id") else str(cv_id),
                        "candidate_label": candidate_label,
                        "file_name": candidate_info.get("filename"),
                        "summary": summary,
                        "global_score": 0,
                        "categories": {},
                        "strengths": [],
                        "risks": [error_msg],
                        "questions": [],
                        "hard_blocker_flags": [],
                        "recommendation": "AI analysis failed",
                        "intro_pitch": "",
                        "gap_strategies": [],
                        "preparation_tips": [],
                        "provider": None,
                        "enrichment": None,
                        "error": error_msg
                    })
                    continue

                data = ai_result.get("data", {})
                categories = data.get("categories", {})
                strengths = _normalize_list(data.get("strengths"))
                risks = _normalize_list(data.get("risks"))
                questions = _normalize_list(data.get("custom_questions") or data.get("questions"))
                blocker_flags = _normalize_list(data.get("hard_blocker_violations") or data.get("hard_blocker_flags"))
                recommendation = data.get("recommendation") or ""
                intro_pitch = data.get("intro_pitch") or ""
                gap_strategies = _normalize_list(data.get("gap_strategies") or [])
                preparation_tips = _normalize_list(data.get("preparation_tips") or [])
                provider_used = ai_result.get("provider") or ai_result.get("model") or "ai"
                
                # Extract detailed analysis fields
                profile_summary = data.get("profile_summary") or ""
                swot_analysis = data.get("swot_analysis") or {}
                technical_skills_detailed = _normalize_list(data.get("technical_skills_detailed") or [])
                soft_skills_detailed = _normalize_list(data.get("soft_skills_detailed") or [])
                missing_critical_technical_skills = _normalize_list(data.get("missing_critical_technical_skills") or [])
                missing_important_soft_skills = _normalize_list(data.get("missing_important_soft_skills") or [])
                professional_experience_analysis = data.get("professional_experience_analysis") or {}
                education_and_certifications = data.get("education_and_certifications") or {}
                notable_achievements = _normalize_list(data.get("notable_achievements") or [])
                culture_fit_assessment = data.get("culture_fit_assessment") or {}
                score_breakdown = data.get("score_breakdown") or {}
                
                # Use global_score from score_breakdown if available
                if score_breakdown and score_breakdown.get("global_score") is not None:
                    global_score = score_breakdown.get("global_score") / 100.0 * 5.0
                else:
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

                # Fetch enrichment data
                enrichment_data = {}
                try:
                    from services.database.enrichment_service import (
                        CompanyEnrichmentService,
                        CandidateEnrichmentService
                    )
                    
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

                report_id = session["data"].get("report_id")
                
                detailed_analysis_data = {
                    "profile_summary": profile_summary,
                    "swot_analysis": swot_analysis,
                    "technical_skills_detailed": technical_skills_detailed,
                    "soft_skills_detailed": soft_skills_detailed,
                    "missing_critical_technical_skills": missing_critical_technical_skills,
                    "missing_important_soft_skills": missing_important_soft_skills,
                    "professional_experience_analysis": professional_experience_analysis,
                    "education_and_certifications": education_and_certifications,
                    "notable_achievements": notable_achievements,
                    "culture_fit_assessment": culture_fit_assessment,
                    "score_breakdown": score_breakdown
                }
                
                prompt_id_value = None
                try:
                    from services.database.prompt_service import get_prompt_service
                    prompt_service = get_prompt_service()
                    prompt_data = await prompt_service.get_prompt_by_key("interviewer_analysis", language)
                    if prompt_data:
                        prompt_id_value = UUID(prompt_data["id"])
                except Exception as prompt_err:
                    logger.warning(f"Failed to get prompt_id: {prompt_err}")
                
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
                    report_id=UUID(report_id) if report_id else None,
                    prompt_id=prompt_id_value,
                    detailed_analysis=detailed_analysis_data
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
                    "recommendation": recommendation,
                    "intro_pitch": intro_pitch,
                    "gap_strategies": gap_strategies,
                    "preparation_tips": preparation_tips,
                    "provider": provider_used,
                    "enrichment": enrichment_data if enrichment_data else None,
                    "profile_summary": profile_summary,
                    "swot_analysis": swot_analysis,
                    "technical_skills_detailed": technical_skills_detailed,
                    "soft_skills_detailed": soft_skills_detailed,
                    "missing_critical_technical_skills": missing_critical_technical_skills,
                    "missing_important_soft_skills": missing_important_soft_skills,
                    "professional_experience_analysis": professional_experience_analysis,
                    "education_and_certifications": education_and_certifications,
                    "notable_achievements": notable_achievements,
                    "culture_fit_assessment": culture_fit_assessment,
                    "score_breakdown": score_breakdown
                })

                if analysis:
                    analyses.append(analysis)
                    
            except asyncio.TimeoutError:
                error_msg = f"CV {idx}: Analysis timed out"
                logger.error(f"AI analysis timed out for CV {cv_id}")
                errors.append(error_msg)
                # Still add to results with error info so it appears in step7
                summary = candidate_info.get("summary") or {}
                candidate_label = (
                    summary.get("full_name")
                    or summary.get("current_role")
                    or candidate_info.get("filename")
                    or f"Candidate {idx}"
                )
                candidate_id_str = str(cv.get("candidate_id")) if cv and cv.get("candidate_id") else str(cv_id)
                
                # Create partial analysis record even when timeout, so it appears in step7
                try:
                    partial_analysis = await analysis_service.create(
                        mode="interviewer",
                        job_posting_id=UUID(job_posting_id),
                        cv_id=UUID(cv_id),
                        candidate_id=UUID(candidate_id_str),
                        provider="timeout",
                        categories={},
                        global_score=0,
                        strengths=[],
                        risks=[error_msg],
                        questions={"items": []},
                        intro_pitch="",
                        hard_blocker_flags=[],
                        language=language,
                        detailed_analysis={"error": error_msg, "status": "timeout"}
                    )
                    analysis_id = partial_analysis["id"] if partial_analysis else None
                except Exception as analysis_err:
                    logger.error(f"Failed to create partial analysis for CV {cv_id}: {analysis_err}", exc_info=True)
                    analysis_id = None
                
                session_results.append({
                    "analysis_id": str(analysis_id) if analysis_id else None,
                    "candidate_id": candidate_id_str,
                    "candidate_label": candidate_label,
                    "file_name": candidate_info.get("filename"),
                    "summary": summary,
                    "global_score": 0,
                    "categories": {},
                    "strengths": [],
                    "risks": [error_msg],
                    "questions": [],
                    "hard_blocker_flags": [],
                    "recommendation": "Analysis failed - timeout",
                    "intro_pitch": "",
                    "gap_strategies": [],
                    "preparation_tips": [],
                    "provider": None,
                    "enrichment": None,
                    "error": error_msg
                })
            except Exception as cv_err:
                error_msg = f"CV {idx}: {str(cv_err)}"
                logger.error(f"Error analyzing CV {cv_id}: {cv_err}", exc_info=True)
                errors.append(error_msg)
                # Still add to results with error info so it appears in step7
                summary = candidate_info.get("summary") or {}
                candidate_label = (
                    summary.get("full_name")
                    or summary.get("current_role")
                    or candidate_info.get("filename")
                    or f"Candidate {idx}"
                )
                candidate_id_str = str(cv.get("candidate_id")) if cv and cv.get("candidate_id") else str(cv_id)
                
                # Create partial analysis record even when error, so it appears in step7
                try:
                    partial_analysis = await analysis_service.create(
                        mode="interviewer",
                        job_posting_id=UUID(job_posting_id),
                        cv_id=UUID(cv_id),
                        candidate_id=UUID(candidate_id_str),
                        provider="error",
                        categories={},
                        global_score=0,
                        strengths=[],
                        risks=[error_msg],
                        questions={"items": []},
                        intro_pitch="",
                        hard_blocker_flags=[],
                        language=language,
                        detailed_analysis={"error": error_msg, "status": "failed", "exception": str(cv_err)[:500]}
                    )
                    analysis_id = partial_analysis["id"] if partial_analysis else None
                except Exception as analysis_err:
                    logger.error(f"Failed to create partial analysis for CV {cv_id}: {analysis_err}", exc_info=True)
                    analysis_id = None
                
                session_results.append({
                    "analysis_id": str(analysis_id) if analysis_id else None,
                    "candidate_id": candidate_id_str,
                    "candidate_label": candidate_label,
                    "file_name": candidate_info.get("filename"),
                    "summary": summary,
                    "global_score": 0,
                    "categories": {},
                    "strengths": [],
                    "risks": [error_msg],
                    "questions": [],
                    "hard_blocker_flags": [],
                    "recommendation": f"Analysis failed: {str(cv_err)[:100]}",
                    "intro_pitch": "",
                    "gap_strategies": [],
                    "preparation_tips": [],
                    "provider": None,
                    "enrichment": None,
                    "error": error_msg
                })
        
        # Log summary
        logger.info(f"✅ Analysis completed: {len(session_results)}/{total_cvs} CVs analyzed successfully for session: {session_id}")
        if errors:
            logger.warning(f"⚠️ {len(errors)} CV(s) had errors during analysis: {errors}")
        
        # Generate executive recommendation (LAST STEP - only if we have successful analyses)
        executive_recommendation = None
        if len(session_results) > 0:
            try:
                # Update progress to show we're generating executive recommendation
                session_service.update_session(
                    session_id,
                    {
                        "analysis_progress": {
                            "current": total_cvs,
                            "total": total_cvs,
                            "status": "Generating executive recommendation...",
                            "errors": errors if errors else None
                        }
                    }
                )
                
                logger.info(f"Generating executive recommendation for session {session_id} with {len(session_results)} candidates")
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
                # Continue without recommendation - not critical for completion
        else:
            logger.warning(f"No successful analyses to generate executive recommendation for session {session_id}")
        
        # Update persistent report (if exists)
        report_id = session["data"].get("report_id")
        if report_id:
            try:
                if executive_recommendation:
                    await report_service.update_executive_recommendation(
                        UUID(report_id),
                        executive_recommendation
                    )
                await report_service.increment_candidate_count(UUID(report_id), len(analyses))
                logger.info(f"Updated report {report_id} with {len(analyses)} analyses")
            except Exception as report_err:
                logger.error(f"Failed to update report: {report_err}")
        
        # Mark as complete (LAST STEP)
        session_service.update_session(
            session_id,
            {
                "analysis_ids": [a["id"] for a in analyses],
                "analysis_complete": True,
                "analysis_status": "completed",
                "analysis_results": session_results,
                "executive_recommendation": executive_recommendation,
                "analysis_progress": {
                    "current": total_cvs,
                    "total": total_cvs,
                    "status": "Analysis complete!",
                    "errors": errors if errors else None
                }
            },
            step=6
        )
        
        logger.info(f"Background analysis complete: {len(analyses)} analyses created for session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error in background analysis task: {e}", exc_info=True)
        # Update session with error
        try:
            session = session_service.get_session(session_id)
            if session:
                session_service.update_session(
                    session_id,
                    {
                        "analysis_status": "error",
                        "analysis_progress": {
                            "status": f"Error: {str(e)}"
                        }
                    }
                )
        except:
            pass


@router.post("/step6")
async def step6_analysis(session_id: str):
    """
    Step 6: Trigger AI analysis (async).
    
    Starts AI analysis for all uploaded CVs in the background.
    Returns immediately. Use GET /step6/progress/{session_id} to check progress.
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
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if analysis is already running
        if session["data"].get("analysis_status") == "running":
            return JSONResponse({
                "status": "already_running",
                "message": "Analysis is already in progress"
            })
        
        # Get CV IDs
        cv_ids = session["data"].get("cv_ids", [])
        if len(cv_ids) == 0:
            raise HTTPException(status_code=400, detail="No CVs uploaded. Complete step 5 first.")
        
        # Get services
        job_posting_service = get_job_posting_service()
        cv_service = get_cv_service()
        analysis_service = get_analysis_service()
        ai_service = get_ai_analysis_service()
        candidate_service = get_candidate_service()
        report_service = get_report_service()
        
        # Start background task
        asyncio.create_task(_run_analysis_background(
            UUID(session_id),
            session_service,
            job_posting_service,
            cv_service,
            analysis_service,
            ai_service,
            candidate_service,
            report_service
        ))
        
        return JSONResponse({
            "status": "started",
            "message": "Analysis started in background",
            "total_cvs": len(cv_ids)
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error starting analysis"
        )


@router.get("/step5/progress/{session_id}")
async def step5_progress(session_id: UUID):
    """
    Get CV upload progress for a session.
    
    Returns current progress, status, and completion state.
    """
    from services.database import get_session_service
    
    try:
        session_service = get_session_service()
        session = session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Safely access session data with defaults
        session_data = session.get("data", {})
        progress = session_data.get("upload_progress", {})
        status = session_data.get("upload_status", "not_started")
        is_complete = status == "complete"
        errors = session_data.get("upload_errors", [])
        cv_count = session_data.get("cv_count", 0)
        upload_summary = session_data.get("upload_summary", {})
        
        return JSONResponse({
            "status": status,
            "complete": is_complete,
            "progress": progress,
            "cv_count": cv_count,
            "errors": errors if errors else None,
            "summary": upload_summary if upload_summary else None
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting upload progress for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting upload progress"
        )


@router.get("/step6/progress/{session_id}")
async def step6_progress(session_id: UUID):
    """
    Get analysis progress for a session.
    
    Returns current progress, status, and completion state.
    """
    from services.database import get_session_service
    
    try:
        session_service = get_session_service()
        session = session_service.get_session(session_id)
        
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Safely access session data with defaults
        session_data = session.get("data", {})
        progress = session_data.get("analysis_progress", {})
        status = session_data.get("analysis_status", "not_started")
        is_complete = session_data.get("analysis_complete", False)
        
        return JSONResponse({
            "status": status,
            "complete": is_complete,
            "progress": progress,
            "has_results": bool(session_data.get("analysis_results"))
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting progress for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting progress"
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
                
                detailed_analysis = analysis.get("detailed_analysis") or {}
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
                    "provider": analysis.get("provider"),
                    # Include detailed analysis fields if available
                    "profile_summary": detailed_analysis.get("profile_summary"),
                    "swot_analysis": detailed_analysis.get("swot_analysis", {}),
                    "technical_skills_detailed": detailed_analysis.get("technical_skills_detailed", []),
                    "soft_skills_detailed": detailed_analysis.get("soft_skills_detailed", []),
                    "missing_critical_technical_skills": detailed_analysis.get("missing_critical_technical_skills", []),
                    "missing_important_soft_skills": detailed_analysis.get("missing_important_soft_skills", []),
                    "professional_experience_analysis": detailed_analysis.get("professional_experience_analysis", {}),
                    "education_and_certifications": detailed_analysis.get("education_and_certifications", {}),
                    "notable_achievements": detailed_analysis.get("notable_achievements", []),
                    "culture_fit_assessment": detailed_analysis.get("culture_fit_assessment", {}),
                    "score_breakdown": detailed_analysis.get("score_breakdown", {})
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
        
        # Safely access session data
        session_data = session.get("data", {})
        
        # Check if analysis is complete
        analysis_complete = session_data.get("analysis_complete", False)
        report_code_in_session = session_data.get("report_code")
        
        # If analysis not complete but we have a report_code, try to load from report
        if not analysis_complete and report_code_in_session:
            logger.info(f"Analysis not complete in session, but report_code exists. Attempting to load from report: {report_code_in_session}")
            try:
                report_service = get_report_service()
                report = await report_service.get_by_code(report_code_in_session)
                
                if report:
                    analyses = await report_service.get_analyses_for_report(UUID(report["id"]))
                    
                    if analyses and len(analyses) > 0:
                        # We have results in the report, use them
                        logger.info(f"Found {len(analyses)} analyses in report {report_code_in_session}, using them")
                        # Update session to mark as complete
                        session_service.update_session(
                            session_id,
                            {
                                "analysis_complete": True,
                                "analysis_status": "completed"
                            },
                            step=7
                        )
                        # Reload session
                        session = session_service.get_session(session_id)
                        analysis_complete = True
                        # Use report data
                        executive_recommendation = report.get("executive_recommendation")
                        # Build results from analyses (same as fallback above)
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
                        
                        report_results: List[Dict[str, Any]] = []
                        for idx, analysis in enumerate(analyses, start=1):
                            candidate_label = None
                            try:
                                candidate = await candidate_service.get_by_id(UUID(analysis["candidate_id"]))
                                if candidate and candidate.get("name"):
                                    candidate_label = candidate["name"]
                            except Exception as candidate_err:
                                logger.warning(f"Failed to load candidate {analysis.get('candidate_id')}: {candidate_err}")
                            
                            detailed_analysis = analysis.get("detailed_analysis") or {}
                            report_results.append({
                                "analysis_id": analysis["id"],
                                "candidate_id": analysis["candidate_id"],
                                "candidate_label": candidate_label or f"Candidate {idx}",
                                "global_score": analysis.get("global_score", 0),
                                "categories": analysis.get("categories") or {},
                                "strengths": _ensure_list(analysis.get("strengths")),
                                "risks": _ensure_list(analysis.get("risks")),
                                "questions": _ensure_list(analysis.get("questions")),
                                "hard_blocker_flags": _ensure_list(analysis.get("hard_blocker_flags")),
                                "provider": analysis.get("provider"),
                                "profile_summary": detailed_analysis.get("profile_summary"),
                                "swot_analysis": detailed_analysis.get("swot_analysis", {}),
                                "technical_skills_detailed": detailed_analysis.get("technical_skills_detailed", []),
                                "soft_skills_detailed": detailed_analysis.get("soft_skills_detailed", []),
                                "missing_critical_technical_skills": detailed_analysis.get("missing_critical_technical_skills", []),
                                "missing_important_soft_skills": detailed_analysis.get("missing_important_soft_skills", []),
                                "professional_experience_analysis": detailed_analysis.get("professional_experience_analysis", {}),
                                "education_and_certifications": detailed_analysis.get("education_and_certifications", {}),
                                "notable_achievements": detailed_analysis.get("notable_achievements", []),
                                "culture_fit_assessment": detailed_analysis.get("culture_fit_assessment", {}),
                                "score_breakdown": detailed_analysis.get("score_breakdown", {})
                            })
                        
                        # Update session with results
                        session_service.update_session(
                            session_id,
                            {
                                "analysis_results": report_results
                            },
                            step=7
                        )
                        # Reload session again
                        session = session_service.get_session(session_id)
                        results = report_results
            except Exception as report_err:
                logger.warning(f"Failed to load from report_code fallback: {report_err}")
        
        if not analysis_complete:
            raise HTTPException(
                status_code=400,
                detail="Analysis not complete. Run step 6 first."
            )
        
        results = session_data.get("analysis_results")
        executive_recommendation = session_data.get("executive_recommendation")
        
        # Extract company name from structured job posting
        company_name = None
        structured_job_posting = session_data.get("structured_job_posting")
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
                # Ensure detailed analysis fields exist (can be empty/None)
                if "profile_summary" not in result:
                    result["profile_summary"] = ""
                if "swot_analysis" not in result or not isinstance(result.get("swot_analysis"), dict):
                    result["swot_analysis"] = {}
                if not isinstance(result.get("technical_skills_detailed"), list):
                    result["technical_skills_detailed"] = []
                if not isinstance(result.get("soft_skills_detailed"), list):
                    result["soft_skills_detailed"] = []
                if not isinstance(result.get("missing_critical_technical_skills"), list):
                    result["missing_critical_technical_skills"] = []
                if not isinstance(result.get("missing_important_soft_skills"), list):
                    result["missing_important_soft_skills"] = []
                if "professional_experience_analysis" not in result or not isinstance(result.get("professional_experience_analysis"), dict):
                    result["professional_experience_analysis"] = {}
                if "education_and_certifications" not in result or not isinstance(result.get("education_and_certifications"), dict):
                    result["education_and_certifications"] = {}
                if not isinstance(result.get("notable_achievements"), list):
                    result["notable_achievements"] = []
                if "culture_fit_assessment" not in result or not isinstance(result.get("culture_fit_assessment"), dict):
                    result["culture_fit_assessment"] = {}
                if "score_breakdown" not in result or not isinstance(result.get("score_breakdown"), dict):
                    result["score_breakdown"] = {}
                
                # Fetch or update enrichment data for this candidate
                enrichment_data = {}
                
                # Check if already has enrichment from step6
                if result.get("enrichment") and isinstance(result.get("enrichment"), dict):
                    enrichment_data = result.get("enrichment")
                    logger.info(f"Candidate {result.get('candidate_id')}: Using enrichment from step6")
                else:
                    logger.info(f"Candidate {result.get('candidate_id')}: Fetching enrichment from database")
                
                # Fetch candidate enrichment if not already present
                if "candidate" not in enrichment_data:
                    try:
                        candidate_id = result.get("candidate_id")
                        if candidate_id:
                            candidate_enrichment = await candidate_enrichment_service.get_latest(UUID(candidate_id))
                            if candidate_enrichment:
                                logger.info(f"Found candidate enrichment in database for {candidate_id}")
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
                        logger.warning(f"Failed to fetch candidate enrichment: {enrichment_err}")
                
                # Add company enrichment if available
                if company_enrichment_data:
                    enrichment_data["company"] = company_enrichment_data
                
                # Update result with enrichment
                if enrichment_data:
                    result["enrichment"] = enrichment_data
            
            return JSONResponse({
                "status": "success",
                "total_candidates": len(sorted_results),
                "results": sorted_results,
                "executive_recommendation": executive_recommendation,
                "hard_blockers": session_data.get("hard_blockers", []),
                "report_code": report_code_in_session,
                "source": "session"
            })
        else:
            raise HTTPException(
                status_code=404,
                detail="No analysis results found"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving results: {e}", exc_info=True)
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
        logger.info(f"Session data keys: {list(session.keys())}")
        logger.info(f"Results count: {len(results) if results else 0}")
        logger.info(f"Has executive recommendation: {bool(executive_recommendation)}")
        
        try:
            pdf_bytes = pdf_generator.generate_interviewer_report(
                session_data=session,
                results=results,
                executive_recommendation=executive_recommendation
            )
            
            if not pdf_bytes or len(pdf_bytes) == 0:
                raise ValueError("PDF generation returned empty bytes")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"candidate_analysis_report_{timestamp}.pdf"
            
            logger.info(f"PDF report generated successfully: {len(pdf_bytes)} bytes")
        except Exception as pdf_error:
            logger.error(f"Error in PDF generation: {pdf_error}", exc_info=True)
            raise HTTPException(
                status_code=500,
                detail=f"Error generating PDF report: {str(pdf_error)}"
            )
        
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

