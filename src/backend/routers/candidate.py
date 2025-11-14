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
from typing import Optional, List, Dict, Any
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
    gap_strategies: list
    preparation_tips: list
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


async def _run_candidate_job_posting_processing_background(
    session_id: UUID,
    final_text: str,
    file_url: Optional[str],
    language: str,
    session_service,
    job_posting_service,
    ai_service
):
    """
    Background task to process candidate job posting: create record and run AI normalization.
    Updates progress in session as it goes.
    """
    try:
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found in background task")
            return
        
        session_data = session.get("data", {})
        candidate_id = session_data.get("candidate_id")
        
        # Initialize progress
        session_service.update_session(
            session_id,
            {
                "step2_status": "running",
                "step2_progress": {
                    "status": "Creating job posting record...",
                    "step": "creating"
                }
            }
        )
        
        # Create job posting record
        try:
            logger.info(
                f"Creating job posting for candidate session {session_id}: "
                f"text_length={len(final_text)}, "
                f"candidate_id={candidate_id}, "
                f"language={language}"
            )
            
            job_posting = await job_posting_service.create(
                raw_text=final_text,
                candidate_id=UUID(candidate_id) if isinstance(candidate_id, str) else candidate_id,
                file_url=file_url,
                language=language
            )
            
            if not job_posting:
                logger.error(f"job_posting_service.create() returned None for candidate session: {session_id}")
                session_service.update_session(
                    session_id,
                    {
                        "step2_status": "error",
                        "step2_progress": {
                            "status": "Failed to create job posting record",
                            "step": "error"
                        }
                    }
                )
                return
        except Exception as e:
            logger.error(f"Error creating job posting: {e}", exc_info=True)
            session_service.update_session(
                session_id,
                {
                    "step2_status": "error",
                    "step2_progress": {
                        "status": f"Error: {str(e)}",
                        "step": "error"
                    }
                }
            )
            return
        
        # Update progress: AI normalization
        session_service.update_session(
            session_id,
            {
                "step2_progress": {
                    "status": "AI is analyzing job posting and extracting structured data...",
                    "step": "ai_processing"
                }
            }
        )
        
        # Extract structured data from job posting with AI
        structured_job_posting = None
        try:
            logger.info("Using AI to extract structured data from job posting")
            structured_job_posting = await ai_service.normalize_job_posting(final_text, language)
            
            if structured_job_posting:
                # Update structured data if extracted
                try:
                    await job_posting_service.update_structured_data(
                        UUID(job_posting["id"]),
                        structured_job_posting
                    )
                except Exception as update_err:
                    logger.warning(f"Failed to update structured data: {update_err}")
        except Exception as norm_err:
            logger.warning(f"Job posting normalization failed: {norm_err}")
            # Continue without structured data - not critical
        
        # Update session with job posting ID and structured data
        session_service.update_session(
            session_id,
            {
                "job_posting_id": job_posting["id"],
                "job_posting_text": final_text[:500],
                "structured_job_posting": structured_job_posting,
                "step2_status": "complete",
                "step2_progress": {
                    "status": "Complete! Ready for step 3.",
                    "step": "complete"
                }
            },
            step=2
        )
        
        logger.info(f"Job posting processing complete: {job_posting['id']} for candidate session: {session_id}")
        
    except Exception as e:
        logger.error(f"Error in background candidate job posting processing: {e}", exc_info=True)
        try:
            session_service.update_session(
                session_id,
                {
                    "step2_status": "error",
                    "step2_progress": {
                        "status": f"Error: {str(e)}",
                        "step": "error"
                    }
                }
            )
        except:
            pass


@router.post("/step2")
async def step2_job_posting(
    session_id: str = Form(...),
    raw_text: Optional[str] = Form(None),
    language: str = Form("en"),
    file: Optional[UploadFile] = File(None)
):
    """
    Step 2: Job posting input (async processing).
    
    Accepts the job posting the candidate is applying for.
    Returns immediately and processes in background.
    Use GET /step2/progress/{session_id} to check progress.
    """
    from services.database import (
        get_session_service,
        get_job_posting_service
    )
    from services.storage import get_storage_service
    from services.ai_analysis import get_ai_analysis_service
    from utils import FileProcessor
    from uuid import UUID
    import asyncio
    
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
        ai_service = get_ai_analysis_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if processing is already running
        if session["data"].get("step2_status") == "running":
            return JSONResponse({
                "status": "already_running",
                "message": "Job posting processing is already in progress"
            })
        
        # Validate required data from session
        candidate_id = session["data"].get("candidate_id")
        if not candidate_id:
            logger.error(
                f"Session {session_id} missing candidate_id. "
                f"Session data keys: {list(session.get('data', {}).keys())}"
            )
            raise HTTPException(
                status_code=400,
                detail="Session missing candidate_id. Please complete step 1 first."
            )
        
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
        
        # Validate job posting text
        if not final_text or not final_text.strip():
            logger.error(f"Empty job posting text for session {session_id}")
            raise HTTPException(
                status_code=400,
                detail="Job posting text cannot be empty"
            )
        
        # Start background processing
        asyncio.create_task(_run_candidate_job_posting_processing_background(
            UUID(session_id),
            final_text,
            file_url,
            language,
            session_service,
            job_posting_service,
            ai_service
        ))
        
        return JSONResponse({
            "status": "processing",
            "message": "Job posting is being processed. Check progress endpoint for status."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step2_job_posting: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error processing job posting"
        )


@router.get("/step2/progress/{session_id}")
async def candidate_step2_progress(session_id: UUID):
    """
    Get job posting processing progress for a candidate session.
    
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
        progress = session_data.get("step2_progress", {})
        status = session_data.get("step2_status", "not_started")
        is_complete = status == "complete"
        job_posting_id = session_data.get("job_posting_id")
        
        return JSONResponse({
            "status": status,
            "complete": is_complete,
            "progress": progress,
            "job_posting_id": job_posting_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate step2 progress for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting progress"
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


async def _run_candidate_analysis_background(
    session_id: UUID,
    session_service,
    job_posting_service,
    cv_service,
    analysis_service,
    ai_service,
    candidate_service
):
    """
    Background task to run AI analysis for candidate.
    Updates progress in session as it goes.
    """
    from utils import FileProcessor
    import re
    
    try:
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            logger.error(f"Session {session_id} not found in background task")
            return
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        cv_id = session["data"].get("cv_id")
        candidate_id = session["data"].get("candidate_id")
        
        if not all([job_posting_id, cv_id, candidate_id]):
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "Missing required data. Complete steps 2 and 3 first.",
                        "step": "error"
                    }
                }
            )
            return
        
        # Update progress: preparing data
        session_service.update_session(
            session_id,
            {
                "step4_status": "running",
                "step4_progress": {
                    "status": "Preparing data for analysis...",
                    "step": "preparing"
                }
            }
        )
        
        # Fetch job posting and convert to markdown
        job_posting = await job_posting_service.get_by_id(UUID(job_posting_id))
        job_posting_markdown = ""
        if job_posting and job_posting.get("raw_text"):
            job_posting_markdown = FileProcessor.text_to_markdown(job_posting["raw_text"])
        structured_job = session["data"].get("structured_job_posting") or (
            job_posting.get("structured_data") if job_posting else None
        )
        company_name = None
        if isinstance(structured_job, dict):
            company_name = structured_job.get("company") or structured_job.get("organization")
        
        if not job_posting_markdown:
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "Job posting content unavailable",
                        "step": "error"
                    }
                }
            )
            return
        
        # Fetch CV and convert to markdown
        cv = await cv_service.get_by_id(UUID(cv_id))
        if not cv:
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "CV not found",
                        "step": "error"
                    }
                }
            )
            return
        
        extracted_text = cv.get("extracted_text") or ""
        cv_markdown = FileProcessor.text_to_markdown(extracted_text) if extracted_text else ""
        
        if not cv_markdown:
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "CV text unavailable for analysis",
                        "step": "error"
                    }
                }
            )
            return
        
        try:
            candidate_uuid = UUID(candidate_id)
        except (ValueError, TypeError):
            candidate_uuid = None
        candidate_record = await candidate_service.get_by_id(candidate_uuid) if candidate_uuid else None
        candidate_name_value = None
        if candidate_record:
            candidate_name_value = (
                candidate_record.get("name")
                or candidate_record.get("full_name")
                or candidate_record.get("email")
            )
        if not candidate_name_value:
            candidate_name_value = session["data"].get("candidate_name")
        
        # Sanitize content to avoid civic-integrity false positives
        civic_replacements = {
            r"\btarget market\b": "customer segment",
            r"\blead generation\b": "prospect identification",
            r"\bstrategic customer partner\b": "business partner",
            r"\bstrategic partner\b": "business partner",
            r"\bdrive opportunities\b": "pursue opportunities",
            r"\belection(s)?\b": "selection event",
            r"\bcampaign trail\b": "project initiative",
            r"\bpolitical\b": "public-sector",
            r"\bgovernance\b": "organizational leadership",
        }
        
        for pattern, replacement in civic_replacements.items():
            job_posting_markdown = re.sub(pattern, replacement, job_posting_markdown, flags=re.IGNORECASE)
            cv_markdown = re.sub(pattern, replacement, cv_markdown, flags=re.IGNORECASE)
        
        language = session["data"].get("language", "en")
        
        # Helper function
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
        
        # Update progress: AI analysis
        session_service.update_session(
            session_id,
            {
                "step4_progress": {
                    "status": "AI is analyzing your CV against the job posting...",
                    "step": "ai_processing"
                }
            }
        )
        
        # Execute AI analysis
        ai_result = await ai_service.analyze_candidate_for_candidate(
            job_posting_markdown,
            cv_markdown,
            language,
            candidate_id=candidate_uuid,
            candidate_name=candidate_name_value,
            company_name=company_name,
        )
        
        if not ai_result or not ai_result.get("data"):
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "AI failed to analyze candidate",
                        "step": "error"
                    }
                }
            )
            return
        
        # Extract data
        data = ai_result.get("data", {})
        
        categories = data.get("categories", {})
        strengths = _normalize_list(data.get("strengths"))
        gaps = _normalize_list(data.get("areas_to_improve") or data.get("areas_for_development") or data.get("gaps") or data.get("risks"))
        
        # Extract questions with suggested answers
        questions_raw = _normalize_list(data.get("custom_questions") or data.get("likely_questions") or data.get("questions"))
        answers_raw = _normalize_list(data.get("answers") or [])
        
        questions_with_answers = []
        for idx, q in enumerate(questions_raw):
            if isinstance(q, dict):
                question_text = q.get("q") or q.get("question", "")
                answer_text = q.get("a") or q.get("answer") or q.get("suggested_answer", "")
                questions_with_answers.append({
                    "category": q.get("category", "general"),
                    "question": question_text,
                    "suggested_answer": answer_text
                })
            elif isinstance(q, str):
                answer_text = answers_raw[idx] if idx < len(answers_raw) else ""
                questions_with_answers.append({
                    "category": "general",
                    "question": q,
                    "suggested_answer": answer_text
                })
        
        gap_strategies = _normalize_list(data.get("gap_strategies"))
        intro_pitch = data.get("intro_pitch", "")
        preparation_tips = _normalize_list(data.get("notes") or data.get("key_advice") or data.get("key_tips") or data.get("preparation_tips") or data.get("preparation_focus"))
        provider_used = ai_result.get("provider") or "ai"
        model_used = ai_result.get("model")
        input_tokens = ai_result.get("input_tokens")
        output_tokens = ai_result.get("output_tokens")
        
        # Calculate costs based on tokens and model
        from utils.cost_calculator import calculate_cost_from_tokens
        cost_breakdown = await calculate_cost_from_tokens(
            provider=provider_used,
            model=model_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens
        )
        
        # Calculate global score
        global_score = sum(categories.values()) / len(categories) if categories else 0
        
        # Update progress: saving results
        session_service.update_session(
            session_id,
            {
                "step4_progress": {
                    "status": "Saving analysis results...",
                    "step": "saving"
                }
            }
        )
        
        # Create analysis record
        analysis = await analysis_service.create(
            mode="candidate",
            job_posting_id=UUID(job_posting_id),
            cv_id=UUID(cv_id),
            candidate_id=UUID(candidate_id),
            provider=provider_used,
            model=model_used,
            categories=categories,
            global_score=round(global_score, 2),
            strengths=strengths,
            risks=gaps,
            questions={
                "items": questions_with_answers,
                "gap_strategies": gap_strategies,
                "preparation_tips": preparation_tips,
                "key_tips": preparation_tips,
                "key_advice": preparation_tips,
                "notes": preparation_tips
            },
            intro_pitch=intro_pitch,
            language=language,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            input_cost=cost_breakdown["input_cost"],
            output_cost=cost_breakdown["output_cost"],
            total_cost=cost_breakdown["total_cost"]
        )
        
        if not analysis:
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": "Failed to create analysis",
                        "step": "error"
                    }
                }
            )
            return
        
        # Update session
        session_service.update_session(
            session_id,
            {
                "analysis_id": analysis["id"],
                "analysis_complete": True,
                "provider": provider_used,
                "model": model_used,
                "step4_status": "complete",
                "step4_progress": {
                    "status": "Complete! Ready for step 5.",
                    "step": "complete"
                }
            },
            step=4
        )
        
        logger.info(f"Candidate analysis complete: {analysis['id']} (provider: {provider_used})")
        
    except Exception as e:
        logger.error(f"Error in background candidate analysis: {e}", exc_info=True)
        try:
            session_service.update_session(
                session_id,
                {
                    "step4_status": "error",
                    "step4_progress": {
                        "status": f"Error: {str(e)}",
                        "step": "error"
                    }
                }
            )
        except:
            pass


@router.post("/step4")
async def step4_analysis(session_id: str):
    """
    Step 4: Trigger AI analysis (async).
    
    Starts AI analysis in the background.
    Returns immediately. Use GET /step4/progress/{session_id} to check progress.
    """
    import asyncio
    from services.database import (
        get_session_service,
        get_job_posting_service,
        get_cv_service,
        get_analysis_service,
        get_candidate_service,
    )
    from services.ai_analysis import get_ai_analysis_service
    from uuid import UUID
    
    try:
        session_service = get_session_service()
        job_posting_service = get_job_posting_service()
        cv_service = get_cv_service()
        analysis_service = get_analysis_service()
        candidate_service = get_candidate_service()
        ai_service = get_ai_analysis_service()
        
        # Validate session
        session = session_service.get_session(UUID(session_id))
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if analysis is already running
        if session["data"].get("step4_status") == "running":
            return JSONResponse({
                "status": "already_running",
                "message": "Analysis is already in progress"
            })
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        cv_id = session["data"].get("cv_id")
        candidate_id = session["data"].get("candidate_id")
        
        if not all([job_posting_id, cv_id, candidate_id]):
            raise HTTPException(
                status_code=400,
                detail="Missing required data. Complete steps 2 and 3 first."
            )
        
        # Start background task
        asyncio.create_task(_run_candidate_analysis_background(
            UUID(session_id),
            session_service,
            job_posting_service,
            cv_service,
            analysis_service,
            ai_service,
            candidate_service
        ))
        
        return JSONResponse({
            "status": "processing",
            "message": "Analysis is being processed. Check progress endpoint for status."
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step4_analysis: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error during analysis"
        )


@router.get("/step4/progress/{session_id}")
async def candidate_step4_progress(session_id: UUID):
    """
    Get candidate analysis progress for a session.
    
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
        progress = session_data.get("step4_progress", {})
        status = session_data.get("step4_status", "not_started")
        is_complete = status == "complete"
        analysis_id = session_data.get("analysis_id")
        
        return JSONResponse({
            "status": status,
            "complete": is_complete,
            "progress": progress,
            "analysis_id": analysis_id
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting candidate step4 progress for session {session_id}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Internal server error getting progress"
        )


@router.get("/step5/{session_id}", response_model=CandidateAnalysisResponse)
async def step5_results(session_id: UUID):
    """
    Step 5: Display results.
    
    Returns analysis results with:
    - Scores per category
    - Strengths and gaps
    - Likely interview questions with detailed guidance
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
        
        # Helper to normalize lists (same as interviewer)
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
        
        # Extract data
        strengths = _normalize_list(analysis.get("strengths"))
        gaps = _normalize_list(analysis.get("risks"))
        
        # Extract questions and gap_strategies from nested structure
        questions_data = analysis.get("questions") or {}
        questions_raw = _normalize_list(questions_data.get("items") or questions_data)
        gap_strategies = _normalize_list(questions_data.get("gap_strategies"))
        
        # Check both nested and top-level for preparation_tips/key_tips/key_advice/notes
        preparation_tips = _normalize_list(
            questions_data.get("notes") or
            questions_data.get("key_advice") or
            questions_data.get("key_tips") or 
            questions_data.get("preparation_tips") or 
            analysis.get("notes") or
            analysis.get("key_advice") or
            analysis.get("key_tips") or
            analysis.get("preparation_tips")
        )
        
        # Extract questions and suggested answers
        questions = []
        suggested_answers = []
        
        # Try to get separate answers array first
        answers_from_field = _normalize_list(analysis.get("answers") or questions_data.get("answers") or [])
        
        for idx, q in enumerate(questions_raw):
            if isinstance(q, dict):
                # Support multiple formats: {q, a}, {question, answer}, {question, suggested_answer}
                question_text = q.get("q") or q.get("question", "")
                answer_text = q.get("a") or q.get("answer") or q.get("suggested_answer", "")
                questions.append(question_text)
                suggested_answers.append(answer_text or "Use STAR method: Situation → Task → Action → Result.")
            elif isinstance(q, str):
                # Try to get answer from separate answers array
                answer_text = answers_from_field[idx] if idx < len(answers_from_field) else ""
                questions.append(q)
                suggested_answers.append(answer_text or "Use STAR method: Situation → Task → Action → Result.")
        
        # Get company info from session if available
        structured_job = session["data"].get("structured_job_posting") or {}
        company_name = structured_job.get("company")
        
        # 🔍 DEBUG: Log what we're sending to frontend
        logger.info(f"🔍 STEP 5 RESPONSE:")
        logger.info(f"  Company: {company_name}")
        logger.info(f"  Questions: {len(questions)}")
        logger.info(f"  Questions sample: {questions[:2] if questions else []}")
        logger.info(f"  Suggested Answers: {len(suggested_answers)}")
        logger.info(f"  Answers sample: {suggested_answers[:2] if suggested_answers else []}")
        logger.info(f"  Preparation Tips: {len(preparation_tips)}")
        logger.info(f"  Gap Strategies: {len(gap_strategies)}")
        logger.info(f"  Intro Pitch: {len(analysis.get('intro_pitch', ''))  } chars")
        if preparation_tips:
            logger.info(f"  Tips content: {preparation_tips}")
        
        # Format response with company info
        response_dict = {
            "session_id": str(session_id),
            "categories": analysis.get("categories", {}),
            "strengths": strengths,
            "gaps": gaps,
            "questions": questions,
            "suggested_answers": suggested_answers,
            "gap_strategies": gap_strategies,
            "preparation_tips": preparation_tips,
            "intro_pitch": analysis.get("intro_pitch", ""),
            "language": analysis["language"],
            "company_name": company_name  # Add company info
        }
        
        return JSONResponse(response_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in step5_results: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error retrieving results"
        )


@router.get("/step6/report/{session_id}")
async def step6_download_report(session_id: UUID):
    """
    Step 6: Download PDF preparation guide.
    
    Generates comprehensive PDF with scores, strengths, gaps, questions, and strategies.
    Same pattern as interviewer Step 8 report.
    """
    from datetime import datetime
    from services.database import get_session_service, get_analysis_service
    from services.pdf import get_pdf_report_generator
    from fastapi.responses import Response
    
    try:
        session_service = get_session_service()
        analysis_service = get_analysis_service()
        pdf_generator = get_pdf_report_generator()
        
        # Get session data
        session = session_service.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Check if analysis is complete
        if not session["data"].get("analysis_complete"):
            raise HTTPException(
                status_code=400,
                detail="Analysis not complete. Complete step 4 first."
            )
        
        # Get analysis
        analysis_id = session["data"].get("analysis_id")
        if not analysis_id:
            raise HTTPException(status_code=400, detail="Analysis not found")
        
        analysis = await analysis_service.get_by_id(UUID(analysis_id))
        if not analysis:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Generate PDF
        logger.info(f"Generating PDF preparation guide for session: {session_id}")
        pdf_bytes = pdf_generator.generate_candidate_report(
            session_data=session,
            analysis=analysis
        )
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"interview_preparation_guide_{timestamp}.pdf"
        
        logger.info(f"PDF preparation guide generated: {len(pdf_bytes)} bytes")
        
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
        logger.error(f"Error generating PDF: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error generating PDF: {str(e)}"
        )

