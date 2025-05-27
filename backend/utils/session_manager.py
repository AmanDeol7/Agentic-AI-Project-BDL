"""
Manager for handling chat sessions.
"""
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from pathlib import Path
import uuid
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

class SessionManager:
    """Simple in-memory session manager."""
    
    def __init__(self):
        """Initialize the session manager."""
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
    
    def create_session(self, name: str = None) -> str:
        """Create a new session."""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            "id": session_id,
            "name": name or f"Session {len(self.active_sessions) + 1}",
            "created_at": datetime.utcnow(),
            "last_accessed": datetime.utcnow(),
            "messages": [],
            "documents": []
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        if session_id in self.active_sessions:
            # Update last accessed time
            self.active_sessions[session_id]["last_accessed"] = datetime.utcnow()
            return self.active_sessions[session_id]
        return None
    
    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all sessions."""
        return [
            {
                "id": session_id,
                "name": session["name"],
                "created_at": session["created_at"],
                "last_accessed": session["last_accessed"],
                "message_count": len(session["messages"]),
                "document_count": len(session["documents"])
            }
            for session_id, session in self.active_sessions.items()
        ]
    
    def add_message(
        self, 
        session_id: str, 
        message: Union[HumanMessage, AIMessage], 
        role: Optional[str] = None
    ) -> None:
        """Add a message to a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        # Determine role if not provided
        if role is None:
            if isinstance(message, HumanMessage):
                role = "user"
            elif isinstance(message, AIMessage):
                role = "code_agent"  # Default to code agent if not specified
        
        self.active_sessions[session_id]["messages"].append({
            "id": str(uuid.uuid4()),
            "role": role,
            "content": message.content,
            "created_at": datetime.utcnow()
        })
    
    def get_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.active_sessions[session_id]["messages"]
    
    def add_document(self, session_id: str, filename: str, file_path: str, file_type: str) -> Dict[str, Any]:
        """Add a document to a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        document = {
            "id": str(uuid.uuid4()),
            "filename": filename,
            "file_path": file_path,
            "file_type": file_type,
            "uploaded_at": datetime.utcnow()
        }
        self.active_sessions[session_id]["documents"].append(document)
        return document
    
    def get_documents(self, session_id: str) -> List[Dict[str, Any]]:
        """Get all documents for a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        return self.active_sessions[session_id]["documents"]
    
    def delete_document(self, session_id: str, document_id: str) -> bool:
        """Delete a document from a session."""
        if session_id not in self.active_sessions:
            raise ValueError(f"Session {session_id} not found")
        
        documents = self.active_sessions[session_id]["documents"]
        for i, doc in enumerate(documents):
            if doc["id"] == document_id:
                documents.pop(i)
                return True
        return False
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False