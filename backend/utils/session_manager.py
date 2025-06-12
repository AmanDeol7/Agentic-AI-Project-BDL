"""
Session manager for multi-client instance support.
Handles isolated sessions for different clients with separate conversation contexts.
"""

import uuid
import time
import threading
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class ClientSession:
    """Represents a client session with isolated context."""
    session_id: str
    client_id: Optional[str] = None
    assistant_instance: Optional[Any] = None
    conversation_history: list = field(default_factory=list)
    uploaded_files: list = field(default_factory=list)
    last_activity: datetime = field(default_factory=datetime.now)
    created_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)

class SessionManager:
    """
    Manages multiple client sessions with isolated assistant instances.
    Provides session isolation for conversations, file uploads, and context.
    """
    
    def __init__(self, session_timeout_minutes: int = 60):
        self.sessions: Dict[str, ClientSession] = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        self._lock = threading.RLock()
        
        # Start cleanup thread
        self._cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        self._cleanup_thread.start()
        
        logger.info(f"SessionManager initialized with {session_timeout_minutes}min timeout")
    
    def create_session(self, client_id: Optional[str] = None) -> str:
        """Create a new session and return the session ID."""
        session_id = str(uuid.uuid4())
        
        with self._lock:
            session = ClientSession(
                session_id=session_id,
                client_id=client_id,
                metadata={
                    "user_agent": client_id,
                    "created_timestamp": datetime.now().isoformat()
                }
            )
            self.sessions[session_id] = session
            
        logger.info(f"Created new session {session_id} for client {client_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ClientSession]:
        """Get a session by ID, updating last activity."""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                session.last_activity = datetime.now()
                return session
            return None
    
    def get_or_create_session(self, session_id: Optional[str] = None, client_id: Optional[str] = None) -> ClientSession:
        """Get existing session or create a new one."""
        if session_id:
            session = self.get_session(session_id)
            if session:
                return session
        
        # Create new session
        new_session_id = self.create_session(client_id)
        return self.get_session(new_session_id)
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session and clean up its resources."""
        with self._lock:
            session = self.sessions.get(session_id)
            if session:
                # Clean up assistant instance
                if session.assistant_instance and hasattr(session.assistant_instance, 'clear_context'):
                    try:
                        session.assistant_instance.clear_context()
                    except Exception as e:
                        logger.warning(f"Error clearing context for session {session_id}: {e}")
                
                # Remove session
                del self.sessions[session_id]
                logger.info(f"Deleted session {session_id}")
                return True
        return False
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get statistics about current sessions."""
        with self._lock:
            total_sessions = len(self.sessions)
            active_sessions = sum(1 for s in self.sessions.values() 
                                if datetime.now() - s.last_activity < timedelta(minutes=30))
            
            return {
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "session_timeout_minutes": self.session_timeout.total_seconds() / 60,
                "oldest_session": min((s.created_at for s in self.sessions.values()), default=None),
                "newest_session": max((s.created_at for s in self.sessions.values()), default=None)
            }
    
    def list_sessions(self) -> Dict[str, Dict[str, Any]]:
        """List all sessions with their basic info."""
        with self._lock:
            return {
                session_id: {
                    "client_id": session.client_id,
                    "created_at": session.created_at.isoformat(),
                    "last_activity": session.last_activity.isoformat(),
                    "conversation_length": len(session.conversation_history),
                    "uploaded_files_count": len(session.uploaded_files),
                    "has_assistant": session.assistant_instance is not None
                }
                for session_id, session in self.sessions.items()
            }
    
    def clear_session_context(self, session_id: str) -> bool:
        """Clear the context for a specific session."""
        session = self.get_session(session_id)
        if session:
            # Clear conversation history
            session.conversation_history.clear()
            session.uploaded_files.clear()
            
            # Clear assistant context if exists
            if session.assistant_instance and hasattr(session.assistant_instance, 'clear_context'):
                try:
                    session.assistant_instance.clear_context()
                    logger.info(f"Cleared context for session {session_id}")
                    return True
                except Exception as e:
                    logger.error(f"Error clearing context for session {session_id}: {e}")
        return False
    
    def _cleanup_expired_sessions(self):
        """Background thread to cleanup expired sessions."""
        while True:
            try:
                time.sleep(300)  # Check every 5 minutes
                
                expired_sessions = []
                with self._lock:
                    current_time = datetime.now()
                    for session_id, session in self.sessions.items():
                        if current_time - session.last_activity > self.session_timeout:
                            expired_sessions.append(session_id)
                
                # Clean up expired sessions
                for session_id in expired_sessions:
                    self.delete_session(session_id)
                    logger.info(f"Cleaned up expired session {session_id}")
                    
            except Exception as e:
                logger.error(f"Error in session cleanup: {e}")
    
    def shutdown(self):
        """Shutdown session manager and clean up all sessions."""
        logger.info("Shutting down session manager...")
        with self._lock:
            session_ids = list(self.sessions.keys())
            for session_id in session_ids:
                self.delete_session(session_id)

# Global session manager instance
_session_manager = None

def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager

def shutdown_session_manager():
    """Shutdown the global session manager."""
    global _session_manager
    if _session_manager:
        _session_manager.shutdown()
        _session_manager = None
