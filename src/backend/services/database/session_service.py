"""
Session management service.

Handles temporary session storage for multi-step flows.
Sessions store intermediate data as users progress through steps.

Note: For MVP, we use a simple in-memory dict. In production,
this should be Redis or similar persistent session store.
"""

from typing import Optional, Dict, Any
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class SessionService:
    """
    Service for managing temporary sessions during multi-step flows.
    
    Sessions expire after a configurable timeout (default: 2 hours).
    """
    
    def __init__(self, session_timeout_hours: int = 2):
        """
        Initialize session service.
        
        Args:
            session_timeout_hours: Hours before session expires
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self.timeout = timedelta(hours=session_timeout_hours)
    
    def create_session(
        self,
        flow_type: str,  # 'interviewer' or 'candidate'
        user_id: UUID,
        initial_data: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """
        Create a new session.
        
        Args:
            flow_type: Type of flow ('interviewer' or 'candidate')
            user_id: ID of the user (interviewer_id or candidate_id)
            initial_data: Optional initial session data
            
        Returns:
            Session UUID
        """
        session_id = uuid4()
        
        self._sessions[str(session_id)] = {
            "id": str(session_id),
            "flow_type": flow_type,
            "user_id": str(user_id),
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + self.timeout).isoformat(),
            "current_step": 1,
            "data": initial_data or {}
        }
        
        logger.info(f"Created session {session_id} for {flow_type} flow")
        return session_id
    
    def get_session(self, session_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get session data.
        
        Args:
            session_id: Session UUID
            
        Returns:
            Session dict or None if not found/expired
        """
        session = self._sessions.get(str(session_id))
        
        if not session:
            return None
        
        # Check expiration
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.utcnow() > expires_at:
            logger.warning(f"Session {session_id} has expired")
            self.delete_session(session_id)
            return None
        
        return session
    
    def update_session(
        self,
        session_id: UUID,
        data: Dict[str, Any],
        step: Optional[int] = None
    ) -> bool:
        """
        Update session data.
        
        Args:
            session_id: Session UUID
            data: Data to merge into session
            step: Optional new current step
            
        Returns:
            True if updated successfully
        """
        session = self.get_session(session_id)
        
        if not session:
            logger.error(f"Session {session_id} not found")
            return False
        
        # Merge new data
        session["data"].update(data)
        
        # Update step if provided
        if step is not None:
            session["current_step"] = step
        
        logger.info(f"Updated session {session_id}, step: {session['current_step']}")
        return True
    
    def delete_session(self, session_id: UUID) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session UUID
            
        Returns:
            True if deleted
        """
        if str(session_id) in self._sessions:
            del self._sessions[str(session_id)]
            logger.info(f"Deleted session {session_id}")
            return True
        
        return False
    
    def cleanup_expired_sessions(self) -> int:
        """
        Remove all expired sessions.
        
        Returns:
            Number of sessions cleaned up
        """
        now = datetime.utcnow()
        expired_keys = []
        
        for session_id, session in self._sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            if now > expires_at:
                expired_keys.append(session_id)
        
        for key in expired_keys:
            del self._sessions[key]
        
        if expired_keys:
            logger.info(f"Cleaned up {len(expired_keys)} expired sessions")
        
        return len(expired_keys)


# Global service instance
_session_service: Optional[SessionService] = None


def get_session_service() -> SessionService:
    """Get global session service instance."""
    global _session_service
    if _session_service is None:
        _session_service = SessionService()
    return _session_service

