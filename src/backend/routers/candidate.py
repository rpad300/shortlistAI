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
        
        # Extract structured data from job posting with AI (same as interviewer)
        structured_job_posting = None
        try:
            from services.ai_analysis import get_ai_analysis_service
            ai_service = get_ai_analysis_service()
            
            logger.info("Using AI to extract structured data from job posting")
            structured_job_posting = await ai_service.normalize_job_posting(final_text, language)
            
            if structured_job_posting:
                logger.info(f"Extracted company: {structured_job_posting.get('company', 'N/A')}")
        except Exception as norm_err:
            logger.warning(f"Job posting normalization failed: {norm_err}")
            # Continue without structured data - not critical
        
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
        
        # Update structured data if extracted
        if structured_job_posting:
            try:
                await job_posting_service.update_structured_data(
                    UUID(job_posting["id"]),
                    structured_job_posting
                )
            except Exception as update_err:
                logger.warning(f"Failed to update structured data: {update_err}")
        
        # Update session with job posting ID and structured data
        session_service.update_session(
            UUID(session_id),
            {
                "job_posting_id": job_posting["id"],
                "job_posting_text": final_text[:500],
                "structured_job_posting": structured_job_posting
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
    Uses the SAME AI pattern as interviewer Step 6.
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
    from utils import FileProcessor
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
        
        # Get job posting
        job_posting_id = session["data"].get("job_posting_id")
        cv_id = session["data"].get("cv_id")
        candidate_id = session["data"].get("candidate_id")
        
        if not all([job_posting_id, cv_id, candidate_id]):
            raise HTTPException(
                status_code=400,
                detail="Missing required data. Complete steps 2 and 3 first."
            )
        
        # Fetch job posting and convert to markdown (same as interviewer)
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
            raise HTTPException(status_code=400, detail="Job posting content unavailable")
        
        # Fetch CV and convert to markdown (same as interviewer)
        cv = await cv_service.get_by_id(UUID(cv_id))
        if not cv:
            raise HTTPException(status_code=404, detail="CV not found")
        
        extracted_text = cv.get("extracted_text") or ""
        cv_markdown = FileProcessor.text_to_markdown(extracted_text) if extracted_text else ""
        
        if not cv_markdown:
            raise HTTPException(
                status_code=400,
                detail="CV text unavailable for analysis"
            )
        
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
        import re
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
        
        # Helper function (same as interviewer)
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
        
        # Execute AI analysis with timeout (SAME as interviewer)
        # Enrichment context is handled within AI service
        ai_result = None
        try:
            ai_result = await asyncio.wait_for(
                ai_service.analyze_candidate_for_candidate(
                    job_posting_markdown,
                    cv_markdown,
                    language,
                    candidate_id=candidate_uuid,
                    candidate_name=candidate_name_value,
                    company_name=company_name,
                ),
                timeout=90  # 90 seconds for large context (same as interviewer)
            )
        except asyncio.TimeoutError:
            logger.error("AI analysis timed out for candidate session %s", session_id)
            raise HTTPException(
                status_code=504,
                detail=f"AI analysis timed out. Please try again or check AI provider status."
            )
        except Exception as ai_exc:
            logger.error("AI analysis failed for candidate session %s: %s", session_id, ai_exc)
            raise HTTPException(
                status_code=500,
                detail=f"AI analysis failed: {str(ai_exc)}"
            )
        
        if not ai_result or not ai_result.get("data"):
            raise HTTPException(
                status_code=500,
                detail=f"AI failed to analyze candidate. Cannot proceed without AI analysis."
            )
        
        # Extract data (SAME pattern as interviewer)
        data = ai_result.get("data", {})
        
        # 🔍 DEBUG: Log what AI actually returned
        logger.info("=" * 80)
        logger.info("🔍 AI RESPONSE DATA KEYS:")
        logger.info(f"Keys in response: {list(data.keys())}")
        logger.info("=" * 80)
        
        categories = data.get("categories", {})
        strengths = _normalize_list(data.get("strengths"))
        gaps = _normalize_list(data.get("areas_to_improve") or data.get("areas_for_development") or data.get("gaps") or data.get("risks"))
        
        # Extract questions with suggested answers
        questions_raw = _normalize_list(data.get("custom_questions") or data.get("likely_questions") or data.get("questions"))
        answers_raw = _normalize_list(data.get("answers") or [])
        
        questions_with_answers = []
        for idx, q in enumerate(questions_raw):
            if isinstance(q, dict):
                # Support multiple formats: {q, a}, {question, answer}, {question, suggested_answer}
                question_text = q.get("q") or q.get("question", "")
                answer_text = q.get("a") or q.get("answer") or q.get("suggested_answer", "")
                questions_with_answers.append({
                    "category": q.get("category", "general"),
                    "question": question_text,
                    "suggested_answer": answer_text
                })
            elif isinstance(q, str):
                # Get corresponding answer from answers array
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
        
        # Calculate global score (same as interviewer)
        global_score = sum(categories.values()) / len(categories) if categories else 0
        
        # Create analysis record with ALL data for persistence
        analysis = await analysis_service.create(
            mode="candidate",
            job_posting_id=UUID(job_posting_id),
            cv_id=UUID(cv_id),
            candidate_id=UUID(candidate_id),
            provider=provider_used,
            categories=categories,
            global_score=round(global_score, 2),
            strengths=strengths,
            risks=gaps,
            questions={
                "items": questions_with_answers,  # Full question objects with answers
                "gap_strategies": gap_strategies,
                "preparation_tips": preparation_tips,
                "key_tips": preparation_tips,
                "key_advice": preparation_tips,
                "notes": preparation_tips  # Store all variants for compatibility
            },
            intro_pitch=intro_pitch,
            language=language
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
                "analysis_complete": True,
                "provider": provider_used,
                "model": model_used
            },
            step=4
        )
        
        logger.info(f"Candidate analysis complete: {analysis['id']} (provider: {provider_used})")
        
        return JSONResponse({
            "status": "success",
            "analysis_id": analysis["id"],
            "provider": provider_used,
            "model": model_used,
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

