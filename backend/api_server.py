"""
FastAPI backend server for the Agentic AI Project.
Provides REST API endpoints for the agentic code assistant.
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

from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

# Import backend components
from backend.main import get_assistant, clear_assistant_instance
from config.app_config import BASE_DIR

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

class ChatResponse(BaseModel):
    response: str
    agent_used: str
    conversation_history: List[ChatMessage]
    tool_results: Optional[List[Dict[str, Any]]] = []
    timestamp: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    components: Dict[str, str]

class FileProcessRequest(BaseModel):
    query: str
    operation: str = "summarize"  # summarize, extract, analyze

# Global assistant instance management
assistant_instance = None

def get_assistant_instance():
    """Get or create the assistant instance."""
    global assistant_instance
    try:
        if assistant_instance is None:
            logger.info("Initializing assistant instance...")
            assistant_instance = get_assistant()
            logger.info("Assistant instance initialized successfully")
        return assistant_instance
    except Exception as e:
        logger.error(f"Failed to initialize assistant: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Assistant initialization failed: {str(e)}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint providing API information."""
    return {
        "message": "Agentic AI Assistant API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "health": "/health"
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
async def chat(request: ChatRequest, assistant: Any = Depends(get_assistant_instance)):
    """
    Main chat endpoint for conversing with the agentic assistant.
    Supports both code and document-related queries.
    """
    try:
        logger.info(f"Processing chat request: {request.message[:100]}...")
        
        # Convert Pydantic models to dictionaries
        conversation_history = []
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.conversation_history
            ]
        
        # Process the message through the assistant
        result = assistant.process_message(
            message=request.message,
            conversation_history=conversation_history,
            uploaded_files=[]
        )
        
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
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Chat processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")

@app.post("/upload", response_model=Dict[str, Any])
async def upload_file(
    file: UploadFile = File(...),
    assistant: Any = Depends(get_assistant_instance)
):
    """
    Upload a file for processing by the document agent.
    Supports PDF, text files, and Excel files.
    """
    try:
        # Check file type
        allowed_extensions = {'.pdf', '.txt', '.md', '.doc', '.docx', '.xlsx', '.xls'}
        file_ext = Path(file.filename).suffix.lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create uploads directory if it doesn't exist
        uploads_dir = BASE_DIR / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        # Save uploaded file
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"File uploaded successfully: {file.filename}")
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "file_path": str(file_path),
            "size": file_path.stat().st_size,
            "type": file_ext,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File upload failed: {str(e)}")

@app.post("/process-file", response_model=ChatResponse)
async def process_file(
    request: FileProcessRequest,
    file: UploadFile = File(...),
    assistant: Any = Depends(get_assistant_instance)
):
    """
    Upload and process a file with a specific query.
    Combines file upload and processing in one endpoint.
    """
    try:
        # First upload the file
        uploads_dir = BASE_DIR / "uploads"
        uploads_dir.mkdir(exist_ok=True)
        
        file_path = uploads_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Process the file with the query
        result = assistant.process_message(
            message=request.query,
            conversation_history=[],
            uploaded_files=[str(file_path)]
        )
        
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
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"File processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"File processing failed: {str(e)}")

@app.post("/execute-code", response_model=Dict[str, Any])
async def execute_code(
    code: str = Form(...),
    language: str = Form(default="python"),
    assistant: Any = Depends(get_assistant_instance)
):
    """
    Execute code directly through the code agent.
    Supports Python and C/C++ code execution.
    """
    try:
        # Create a message that requests code execution
        message = f"Execute this {language} code:\n```{language}\n{code}\n```"
        
        result = assistant.process_message(
            message=message,
            conversation_history=[],
            uploaded_files=[]
        )
        
        return {
            "result": result.get("response", "No output"),
            "agent_used": result.get("agent_used", "unknown"),
            "tool_results": result.get("tool_results", []),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Code execution failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Code execution failed: {str(e)}")

@app.post("/clear-context", response_model=Dict[str, str])
async def clear_context(assistant: Any = Depends(get_assistant_instance)):
    """
    Clear the assistant's context and memory.
    Useful for starting fresh conversations.
    """
    try:
        assistant.clear_context()
        return {
            "message": "Context cleared successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Context clearing failed: {str(e)}")
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