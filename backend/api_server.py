"""
FastAPI backend server for the Agentic AI Project.
Provides REST API endpoints for the agentic code assistant with multi-client session support.
"""

import os
import sys
import logging
from typing import Dict, Any, List, Optional
from pathlib import Path
import tempfile
import shutil
from datetime import datetime

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import backend components
from backend.main import get_assistant, clear_assistant_instance
from backend.utils.session_manager import get_session_manager, ClientSession
from config.app_config import BASE_DIR, PATHS

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Agentic AI Assistant API",
    description="Backend API for the Agentic Code Assistant with document processing and code execution capabilities",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[ChatMessage]] = []
    agent_type: Optional[str] = None
    uploaded_files: Optional[List[str]] = []  # Add uploaded files list
    session_id: Optional[str] = None  # Session ID for multi-client support

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    conversation_history: List[ChatMessage]
    tool_results: Optional[List[Dict[str, Any]]] = []
    timestamp: str
    session_id: str  # Include session ID in response

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class FileProcessRequest(BaseModel):
    query: str
    operation: str = "summarize"  # summarize, extract, analyze
    session_id: Optional[str] = None  # Session ID for multi-client support

class SessionInfo(BaseModel):
    session_id: str
    client_id: Optional[str] = None
    created_at: str
    last_activity: str
    conversation_length: int
    uploaded_files_count: int
    has_assistant: bool

class SessionStats(BaseModel):
    total_sessions: int
    active_sessions: int
    session_timeout_minutes: float
    oldest_session: Optional[str] = None
    newest_session: Optional[str] = None

# Session management dependency
def get_session_from_header(
    x_session_id: Optional[str] = Header(None),
    x_client_id: Optional[str] = Header(None)
) -> ClientSession:
    """Get or create a session based on headers."""
    session_manager = get_session_manager()
    session = session_manager.get_or_create_session(
        session_id=x_session_id,
        client_id=x_client_id
    )
    return session

def get_assistant_for_session(session: ClientSession = Depends(get_session_from_header)):
    """Get or create an assistant instance for a specific session."""
    try:
        if session.assistant_instance is None:
            logger.info(f"Initializing assistant instance for session {session.session_id}...")
            session.assistant_instance = get_assistant()
            logger.info(f"Assistant instance initialized for session {session.session_id}")
        return session.assistant_instance
    except Exception as e:
        logger.error(f"Failed to initialize assistant for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assistant initialization failed: {str(e)}")

# Global assistant instance management (for backward compatibility)
assistant_instance = None

def get_assistant_instance():
    """Get or create the global assistant instance (deprecated - use session-based approach)."""
    global assistant_instance
    try:
        if assistant_instance is None:
            logger.info("Initializing global assistant instance...")
            assistant_instance = get_assistant()
            logger.info("Global assistant instance initialized successfully")
        return assistant_instance
    except Exception as e:
        logger.error(f"Failed to initialize global assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assistant initialization failed: {str(e)}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Agentic AI Assistant API with Multi-Client Support",
        "version": "2.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }

# Session Management Endpoints
@app.post("/sessions", response_model=Dict[str, str])
async def create_session(client_id: Optional[str] = None):
    """Create a new session for a client."""
    session_manager = get_session_manager()
    session_id = session_manager.create_session(client_id)
    return {
        "session_id": session_id,
        "message": "Session created successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions/{session_id}", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get information about a specific session."""
    session_manager = get_session_manager()
    session = session_manager.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return SessionInfo(
        session_id=session.session_id,
        client_id=session.client_id,
        created_at=session.created_at.isoformat(),
        last_activity=session.last_activity.isoformat(),
        conversation_length=len(session.conversation_history),
        uploaded_files_count=len(session.uploaded_files),
        has_assistant=session.assistant_instance is not None
    )

@app.delete("/sessions/{session_id}", response_model=Dict[str, str])
async def delete_session(session_id: str):
    """Delete a specific session and clean up its resources."""
    session_manager = get_session_manager()
    success = session_manager.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "message": f"Session {session_id} deleted successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/sessions", response_model=Dict[str, Any])
async def list_sessions():
    """List all active sessions."""
    session_manager = get_session_manager()
    return {
        "sessions": session_manager.list_sessions(),
        "stats": session_manager.get_session_stats(),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/sessions/{session_id}/clear", response_model=Dict[str, str])
async def clear_session_context(session_id: str):
    """Clear the context for a specific session."""
    session_manager = get_session_manager()
    success = session_manager.clear_session_context(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "message": f"Session {session_id} context cleared successfully",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for monitoring and load balancers."""
    try:
        # Check if assistant can be initialized (lightweight check)
        assistant = get_assistant_instance()
        assistant_status = "healthy" if assistant is not None else "degraded"
        
        # Check LLM provider status (lightweight check without making actual calls)
        llm_status = "unknown"
        try:
            if hasattr(assistant, 'llm_provider'):
                if hasattr(assistant.llm_provider, 'is_available'):
                    llm_status = "healthy" if assistant.llm_provider.is_available() else "unhealthy"
                else:
                    llm_status = "healthy"  # Assume healthy if no check method
        except Exception:
            llm_status = "unhealthy"
        
        overall_status = "healthy" if assistant_status == "healthy" and llm_status in ["healthy", "unknown"] else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components={
                "assistant": assistant_status,
                "llm_provider": llm_status,
                "api": "healthy"
            }
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.now().isoformat(),
            version="1.0.0",
            components={
                "assistant": "unhealthy",
                "llm_provider": "unknown",
                "api": "degraded",
                "error": str(e)
            }
        )

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    session: ClientSession = Depends(get_session_from_header),
    assistant: Any = Depends(get_assistant_for_session)
):
    """
    Main chat endpoint for conversing with the agentic assistant.
    Supports both code and document-related queries with session isolation.
    """
    try:
        logger.info(f"Processing chat request for session {session.session_id}: {request.message[:100]}...")
        
        # Use session's conversation history if no history provided in request
        conversation_history = []
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.conversation_history
            ]
        else:
            # Use session's stored conversation history
            conversation_history = session.conversation_history.copy()
        
        # Process the message through the assistant
        result = assistant.process_message(
            message=request.message,
            conversation_history=conversation_history,
            uploaded_files=request.uploaded_files or session.uploaded_files
        )
        
        # Update session's conversation history
        if result.get("conversation_history"):
            session.conversation_history = result["conversation_history"]
        
        # Convert response back to Pydantic models
        response_history = []
        if result.get("conversation_history"):
            response_history = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in result["conversation_history"]
            ]
        
        return ChatResponse(
            response=result.get("response", "No response generated"),
            agent_used=result.get("agent_used", "unknown"),
            conversation_history=response_history,
            tool_results=result.get("tool_results", []),
            timestamp=datetime.now().isoformat(),
            session_id=session.session_id
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/upload", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    session: ClientSession = Depends(get_session_from_header),
    assistant: Any = Depends(get_assistant_for_session)
):
    """
    Upload a file for processing with session isolation.
    Files are associated with the specific client session.
    """
    try:
        logger.info(f"Uploading file {file.filename} for session {session.session_id}")
        
        # Check file type
        allowed_extensions = {'.pdf', '.txt', '.md', '.doc', '.docx', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create session-specific uploads directory
        session_uploads_dir = PATHS["uploads"] / f"session_{session.session_id}"
        session_uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the file with session prefix
        file_path = session_uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to session's uploaded files
        file_path_str = str(file_path)
        if file_path_str not in session.uploaded_files:
            session.uploaded_files.append(file_path_str)
        
        logger.info(f"File uploaded successfully for session {session.session_id}: {file_path}")
        
        return {
            "message": f"File {file.filename} uploaded successfully",
            "filename": file.filename,
            "file_path": file_path_str,
            "session_id": session.session_id,
            "size": file_path.stat().st_size,
            "type": file_ext,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"File upload failed for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/process-file", response_model=ChatResponse)
async def process_file(
    request: FileProcessRequest,
    file: UploadFile = File(...),
    session: ClientSession = Depends(get_session_from_header),
    assistant: Any = Depends(get_assistant_for_session)
):
    """
    Upload and process a file with a specific query within a session context.
    Combines file upload and processing in one endpoint.
    """
    try:
        logger.info(f"Processing file {file.filename} for session {session.session_id}")
        
        # Create session-specific uploads directory
        session_uploads_dir = PATHS["uploads"] / f"session_{session.session_id}"
        session_uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_path = session_uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Add to session's uploaded files
        file_path_str = str(file_path)
        if file_path_str not in session.uploaded_files:
            session.uploaded_files.append(file_path_str)
        
        # Process the file with the query
        result = assistant.process_message(
            message=request.query,
            conversation_history=session.conversation_history.copy(),
            uploaded_files=[file_path_str]
        )
        
        # Update session's conversation history
        if result.get("conversation_history"):
            session.conversation_history = result["conversation_history"]
        
        # Convert response
        response_history = []
        if result.get("conversation_history"):
            response_history = [
                ChatMessage(role=msg["role"], content=msg["content"])
                for msg in result["conversation_history"]
            ]
        
        return ChatResponse(
            response=result.get("response", "No response generated"),
            agent_used=result.get("agent_used", "unknown"),
            conversation_history=response_history,
            tool_results=result.get("tool_results", []),
            timestamp=datetime.now().isoformat(),
            session_id=session.session_id
        )
        
    except Exception as e:
        logger.error(f"File processing failed for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.post("/execute-code", response_model=Dict[str, Any])
async def execute_code(
    code: str = Form(...),
    language: str = Form(default="python"),
    session: ClientSession = Depends(get_session_from_header),
    assistant: Any = Depends(get_assistant_for_session)
):
    """
    Execute code directly through the code agent with session isolation.
    Supports Python and C/C++ code execution.
    """
    try:
        logger.info(f"Executing {language} code for session {session.session_id}")
        
        # Create a message that requests code execution
        message = f"Execute this {language} code:\n```{language}\n{code}\n```"
        
        result = assistant.process_message(
            message=message,
            conversation_history=session.conversation_history.copy(),
            uploaded_files=session.uploaded_files
        )
        
        # Update session's conversation history
        if result.get("conversation_history"):
            session.conversation_history = result["conversation_history"]
        
        return {
            "result": result.get("response", "No output"),
            "agent_used": result.get("agent_used", "unknown"),
            "tool_results": result.get("tool_results", []),
            "session_id": session.session_id,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Code execution failed for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")

@app.post("/clear-context", response_model=Dict[str, str])
async def clear_context(
    session: ClientSession = Depends(get_session_from_header),
    assistant: Any = Depends(get_assistant_for_session)
):
    """
    Clear the assistant's context and memory for a specific session.
    Useful for starting fresh conversations.
    """
    try:
        # Clear session context
        session_manager = get_session_manager()
        success = session_manager.clear_session_context(session.session_id)
        
        if success:
            return {
                "message": f"Context cleared successfully for session {session.session_id}",
                "session_id": session.session_id,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to clear session context")
            
    except Exception as e:
        logger.error(f"Context clearing failed for session {session.session_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Context clearing failed: {str(e)}")

@app.post("/reset-assistant", response_model=Dict[str, str])
async def reset_assistant():
    """
    Reset the entire assistant instance.
    Forces complete reinitialization on next request.
    """
    try:
        global assistant_instance
        assistant_instance = None
        clear_assistant_instance()
        
        return {
            "message": "Assistant reset successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Assistant reset failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assistant reset failed: {str(e)}")

@app.get("/status", response_model=Dict[str, Any])
async def get_status(assistant: Any = Depends(get_assistant_instance)):
    """
    Get detailed status information about the assistant and its components.
    """
    try:
        status_info = {
            "api_status": "running",
            "assistant_initialized": assistant is not None,
            "available_agents": [],
            "available_tools": [],
            "llm_provider": "unknown",
            "timestamp": datetime.now().isoformat()
        }
        
        if assistant:
            # Get agent information
            if hasattr(assistant, 'agents'):
                status_info["available_agents"] = [
                    {
                        "id": agent_id,
                        "name": getattr(agent, 'name', 'Unknown'),
                        "description": getattr(agent, 'description', 'No description')
                    }
                    for agent_id, agent in assistant.agents.items()
                ]
            
            # Get tool information
            if hasattr(assistant, 'tools'):
                status_info["available_tools"] = list(assistant.tools.keys())
            
            # Get LLM provider information
            if hasattr(assistant, 'llm_provider'):
                provider = assistant.llm_provider
                status_info["llm_provider"] = {
                    "type": provider.__class__.__name__,
                    "available": getattr(provider, 'is_available', lambda: True)()
                }
        
        return status_info
        
    except Exception as e:
        logger.error(f"Status check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Status check failed: {str(e)}")

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Endpoint not found",
            "message": f"The requested endpoint {request.url.path} was not found",
            "timestamp": datetime.now().isoformat()
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        }
    )

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    logger.info("🚀 Starting Agentic AI Assistant API...")
    logger.info("📡 API Documentation available at /docs")
    logger.info("🔍 Health check available at /health")
    
    # Pre-initialize the assistant to catch any initialization errors early
    try:
        assistant = get_assistant_instance()
        logger.info("✅ Assistant initialized successfully")
    except Exception as e:
        logger.error(f"❌ Assistant initialization failed: {str(e)}")
        # Don't exit - let health checks handle this

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up on application shutdown."""
    logger.info("🛑 Shutting down Agentic AI Assistant API...")
    
    # Clear the assistant instance
    global assistant_instance
    if assistant_instance:
        try:
            assistant_instance.clear_context()
            assistant_instance = None
            logger.info("✅ Assistant context cleared")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {str(e)}")

if __name__ == "__main__":
    # For development/testing
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🌐 Starting server on {host}:{port}")
    uvicorn.run(
        "api_server:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )