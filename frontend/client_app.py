"""
Client Streamlit app for the agentic code assistant.
This app connects to a remote backend server via HTTP API calls.
"""
import streamlit as st
import sys
import os
import asyncio
import time
from pathlib import Path
import warnings
import requests
import json
from typing import List, Dict, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Configure environment variables before any other imports
os.environ['STREAMLIT_SERVER_WATCH_DIRS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_ENABLE_STATIC_SERVING'] = 'true'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'  # Disable tokenizer parallelism

# Suppress specific warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')
warnings.filterwarnings('ignore', category=UserWarning, module='transformers')

# Configure event loop policy for Windows
if sys.platform == 'win32':
    try:
        # Try to get the current event loop
        loop = asyncio.get_event_loop()
    except RuntimeError:
        # If no event loop exists, create a new one
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    # Set the event loop policy
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Import components after event loop configuration
from frontend.components.chat_interface import create_chat_interface
from frontend.components.session_manager import render_session_management_sidebar

# Get backend URL from environment
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8000')

class BackendClient:
    """Client for communicating with the backend API."""
    
    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip('/')
        self.session_id = None
        self.client_id = None
        
    def _get_session_headers(self) -> Dict[str, str]:
        """Get session headers for API requests."""
        headers = {}
        if self.session_id:
            headers['x-session-id'] = self.session_id
        if self.client_id:
            headers['x-client-id'] = self.client_id
        return headers
    
    def create_session(self, client_id: Optional[str] = None) -> Dict[str, Any]:
        """Create a new session."""
        try:
            response = requests.post(
                f"{self.base_url}/sessions",
                json={"client_id": client_id} if client_id else {},
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            
            # Store session information
            self.session_id = result.get("session_id")
            self.client_id = client_id
            
            return result
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information."""
        if not self.session_id:
            return {"error": "No active session"}
        
        try:
            response = requests.get(
                f"{self.base_url}/sessions/{self.session_id}",
                headers=self._get_session_headers(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def list_sessions(self) -> Dict[str, Any]:
        """List all active sessions."""
        try:
            response = requests.get(f"{self.base_url}/sessions", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_session_context(self) -> Dict[str, Any]:
        """Clear the current session context."""
        if not self.session_id:
            return {"error": "No active session"}
        
        try:
            response = requests.post(
                f"{self.base_url}/sessions/{self.session_id}/clear",
                headers=self._get_session_headers(),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def delete_session(self) -> Dict[str, Any]:
        """Delete the current session."""
        if not self.session_id:
            return {"error": "No active session"}
        
        try:
            response = requests.delete(
                f"{self.base_url}/sessions/{self.session_id}",
                headers=self._get_session_headers(),
                timeout=30
            )
            response.raise_for_status()
            result = response.json()
            
            # Clear local session information
            self.session_id = None
            self.client_id = None
            
            return result
        except Exception as e:
            return {"error": str(e)}
        
    def health_check(self) -> Dict[str, Any]:
        """Check backend health."""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    def process_message(
        self, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None,
        uploaded_files: List[str] = None
    ) -> Dict[str, Any]:
        """Process a message through the backend API."""
        try:
            # Prepare the request payload
            payload = {
                "message": message,
                "conversation_history": conversation_history or [],
                "agent_type": None,
                "uploaded_files": uploaded_files or [],
                "session_id": self.session_id  # Include session ID in payload
            }
            
            # Make the API call with session headers
            response = requests.post(
                f"{self.base_url}/chat",
                json=payload,
                headers=self._get_session_headers(),
                timeout=300  # 5 minute timeout for complex queries
            )
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            # Convert the response to the expected format
            return {
                "response": result.get("response", "No response generated"),
                "agent_used": result.get("agent_used", "unknown"),
                "conversation_history": [
                    {"role": msg["role"], "content": msg["content"]}
                    for msg in result.get("conversation_history", [])
                ],
                "tool_results": result.get("tool_results", [])
            }
            
        except requests.exceptions.Timeout:
            return {
                "response": "Request timed out. The backend may be processing a complex query.",
                "agent_used": "error",
                "conversation_history": conversation_history or [],
                "tool_results": [],
                "error": "timeout"
            }
        except requests.exceptions.ConnectionError:
            return {
                "response": f"Could not connect to backend at {self.base_url}. Please ensure the backend is running.",
                "agent_used": "error", 
                "conversation_history": conversation_history or [],
                "tool_results": [],
                "error": "connection_error"
            }
        except Exception as e:
            return {
                "response": f"Error communicating with backend: {str(e)}",
                "agent_used": "error",
                "conversation_history": conversation_history or [],
                "tool_results": [],
                "error": str(e)
            }
    
    def upload_file(self, file_path: str, file_content: bytes, filename: str) -> Dict[str, Any]:
        """Upload a file to the backend."""
        try:
            files = {"file": (filename, file_content)}
            response = requests.post(
                f"{self.base_url}/upload",
                files=files,
                headers=self._get_session_headers(),
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def clear_context(self) -> Dict[str, Any]:
        """Clear the backend context (legacy method - use clear_session_context instead)."""
        if self.session_id:
            return self.clear_session_context()
        
        try:
            response = requests.post(f"{self.base_url}/clear-context", timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

def test_backend_connection():
    """Test connection to the backend and display status."""
    client = BackendClient(BACKEND_URL)
    health = client.health_check()
    
    if health.get("status") == "healthy":
        st.success(f"✅ Connected to backend at {BACKEND_URL}")
        
        # Create a session for this client
        client_id = f"streamlit_client_{int(time.time())}"
        session_result = client.create_session(client_id)
        
        if "error" not in session_result:
            st.success(f"✅ Session created: {session_result.get('session_id', 'Unknown')}")
            st.info(f"Client ID: {client_id}")
        else:
            st.warning(f"⚠️ Session creation failed: {session_result.get('error')}")
        
        return client
    else:
        st.error(f"❌ Failed to connect to backend at {BACKEND_URL}")
        st.error(f"Error: {health.get('error', 'Unknown error')}")
        st.info("Please ensure the backend server is running and accessible.")
        return None

def create_message_processor(client: BackendClient):
    """Create a message processor function that uses the backend client."""
    def process_message(message: str, conversation_history: List[Dict[str, str]] = None, uploaded_files: List[str] = None):
        # If there are uploaded files, upload them to backend first
        backend_file_paths = []
        if uploaded_files:
            with st.spinner("Uploading files to backend..."):
                for file_path in uploaded_files:
                    try:
                        # Read file content
                        with open(file_path, 'rb') as f:
                            file_content = f.read()
                        filename = os.path.basename(file_path)
                        
                        # Upload to backend
                        upload_result = client.upload_file(file_path, file_content, filename)
                        if "error" not in upload_result:
                            backend_file_paths.append(upload_result.get("file_path", file_path))
                            st.success(f"✅ Uploaded {filename} to backend")
                        else:
                            st.error(f"❌ Failed to upload {filename}: {upload_result['error']}")
                    except Exception as e:
                        st.error(f"❌ Error uploading {os.path.basename(file_path)}: {str(e)}")
            
            # Update message to include file information
            if backend_file_paths:
                file_list = "\n".join([f"- {os.path.basename(fp)}" for fp in backend_file_paths])
                message = f"{message}\n\nFiles to analyze:\n{file_list}"
        
        # Process message with backend file paths
        return client.process_message(message, conversation_history, backend_file_paths)
    return process_message

def main():
    """Main function for the client Streamlit app."""
    try:
        # Configure the page
        st.set_page_config(
            page_title="Agentic Code Assistant (Client)",
            page_icon="🧠",
            layout="wide"
        )
        
        # Page title with client indicator
        st.title("🧠 Agentic Code Assistant (Client Mode)")
        st.markdown(
            f"""
            This is a client connecting to a remote AI assistant backend at `{BACKEND_URL}`.
            
            **Features:**
            - 💻 Writing and analyzing code
            - 📄 Extracting information from documents
            - 🔗 Remote backend processing
            
            Upload files and start chatting!
            """
        )
        
        # Initialize backend client if not exists
        if 'backend_client' not in st.session_state:
            with st.spinner("Connecting to backend..."):
                client = test_backend_connection()
                if client is None:
                    st.stop()
                st.session_state.backend_client = client
        
        # Create the chat interface using the backend client
        message_processor = create_message_processor(st.session_state.backend_client)
        create_chat_interface(message_processor, st.session_state.backend_client)
        
        # Add backend status in sidebar
        with st.sidebar:
            st.subheader("Backend Status")
            if st.button("🔄 Refresh Connection"):
                # Test connection again
                health = st.session_state.backend_client.health_check()
                if health.get("status") == "healthy":
                    st.success("✅ Backend is healthy")
                else:
                    st.error("❌ Backend connection failed")
                    st.error(health.get("error", "Unknown error"))
            
            # Show backend URL
            st.info(f"Backend: {BACKEND_URL}")
            
            st.divider()
            
            # Enhanced session management UI
            render_session_management_sidebar(st.session_state.backend_client)
            
            st.divider()
            
            # Legacy clear backend context button (for backward compatibility)
            st.subheader("Legacy Actions")
            if st.button("🧹 Clear Backend Context (Legacy)"):
                with st.spinner("Clearing backend context..."):
                    result = st.session_state.backend_client.clear_context()
                    if "error" in result:
                        st.error(f"Failed to clear context: {result['error']}")
                    else:
                        st.success("✅ Backend context cleared")
                        # Also clear frontend state
                        if 'messages' in st.session_state:
                            st.session_state.messages = []
                        if 'uploaded_files' in st.session_state:
                            st.session_state.uploaded_files = []
                        st.rerun()
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try restarting the application.")
        if 'backend_client' in st.session_state:
            del st.session_state.backend_client

if __name__ == "__main__":
    main()