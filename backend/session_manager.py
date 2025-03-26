from typing import Dict, Any
import time
from datetime import datetime

class SessionManager:
    """
    Manages user sessions and their associated context/state.
    For V0, this is a simple in-memory implementation.
    """
    
    def __init__(self, session_timeout: int = 3600):
        """
        Initialize the session manager.
        
        Parameters:
        - session_timeout: Time in seconds before a session expires (default: 1 hour)
        """
        self.sessions: Dict[str, Dict[str, Any]] = {}
        self.session_timeout = session_timeout
    
    def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a session by ID, or create a new one if it doesn't exist.
        
        Parameters:
        - session_id: Unique identifier for the session
        
        Returns:
        - Session context dictionary
        """
        # Clean expired sessions
        self._clean_expired_sessions()
        
        # Create new session if it doesn't exist
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "created_at": time.time(),
                "last_accessed": time.time(),
                "messages": [],
                "identified_goals": [],
                "recommended_supplements": []
            }
        else:
            # Update last accessed time
            self.sessions[session_id]["last_accessed"] = time.time()
        
        return self.sessions[session_id]
    
    def update_session(self, session_id: str, context: Dict[str, Any]) -> None:
        """
        Update a session with new context.
        
        Parameters:
        - session_id: Unique identifier for the session
        - context: Updated session context
        """
        context["last_accessed"] = time.time()
        self.sessions[session_id] = context
    
    def _clean_expired_sessions(self) -> None:
        """
        Remove sessions that have exceeded the timeout period.
        """
        current_time = time.time()
        expired_sessions = [
            session_id for session_id, session in self.sessions.items()
            if current_time - session["last_accessed"] > self.session_timeout
        ]
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
    
    def get_all_active_sessions(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all active (non-expired) sessions.
        
        Returns:
        - Dictionary of session_id to session context
        """
        self._clean_expired_sessions()
        return self.sessions
