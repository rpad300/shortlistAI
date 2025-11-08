"""
Additional endpoint to get AI-suggested key points for Step 3.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from uuid import UUID
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/interviewer", tags=["interviewer"])


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

