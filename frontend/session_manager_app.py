"""
Session management page for the Agentic AI Project.
Provides comprehensive session management interface for multi-client support.
"""
import streamlit as st
import sys
import os
import time
from pathlib import Path
import warnings

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

# Configure environment variables
os.environ['STREAMLIT_SERVER_WATCH_DIRS'] = 'false'
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['TOKENIZERS_PARALLELISM'] = 'false'

# Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning, module='torch')
warnings.filterwarnings('ignore', category=UserWarning, module='transformers')

# Import after configuration
from frontend.components.session_manager import render_session_management_main
from frontend.client_app import BackendClient

# Get backend URL from environment
BACKEND_URL = os.getenv('BACKEND_URL', 'http://localhost:8001')


def main():
    """Main function for the session management page."""
    # Configure the page
    st.set_page_config(
        page_title="Session Management - Agentic AI",
        page_icon="🔗",
        layout="wide"
    )
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🔗 Session Management")
        st.markdown("Manage client sessions for the Agentic AI Project")
    
    # Initialize backend client
    if 'session_manager_client' not in st.session_state:
        st.session_state.session_manager_client = BackendClient(BACKEND_URL)
    
    client = st.session_state.session_manager_client
    
    # Backend connection status
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Test Connection", use_container_width=True):
                health = client.health_check()
                if health.get("status") == "healthy":
                    st.success("✅ Backend is healthy")
                else:
                    st.error(f"❌ Backend error: {health.get('error', 'Unknown')}")
        
        with col2:
            st.info(f"Backend: `{BACKEND_URL}`")
        
        with col3:
            # Quick session creation
            if st.button("⚡ Quick Session", use_container_width=True):
                client_id = f"admin_session_{int(time.time())}"
                result = client.create_session(client_id)
                if "error" not in result:
                    st.success(f"✅ Session created: {result.get('session_id', 'Unknown')[:8]}...")
                    st.rerun()
                else:
                    st.error(f"❌ Error: {result['error']}")
    
    st.divider()
    
    # Main session management interface
    render_session_management_main(client)
    
    # Footer with information
    st.divider()
    with st.expander("ℹ️ About Session Management", expanded=False):
        st.markdown("""
        ### Session Management Features
        
        **Session Operations:**
        - ➕ **Create Sessions**: Generate new isolated sessions for clients
        - 🔄 **Switch Sessions**: Move between different active sessions
        - 🧹 **Clear Context**: Reset conversation history and uploaded files
        - 🗑️ **Delete Sessions**: Permanently remove sessions and cleanup resources
        
        **Session Information:**
        - 📊 **Detailed Stats**: View conversation length, file count, creation time
        - 📋 **List All Sessions**: See all active sessions across the system
        - ⏱️ **Activity Tracking**: Monitor last activity and session timeouts
        - 🔍 **Session Export**: Export session data for debugging (coming soon)
        
        **Multi-Client Support:**
        - 🏢 **Client Isolation**: Each session maintains separate context
        - 🤖 **Assistant Instances**: Dedicated AI assistant per session
        - 📁 **File Management**: Session-specific file uploads and processing
        - 💾 **Memory Management**: Automatic cleanup of expired sessions
        
        ### Usage Tips
        1. **Create a session** before starting conversations
        2. **Switch between sessions** to handle multiple clients
        3. **Clear context** to reset without deleting the session
        4. **Monitor session stats** to track usage and performance
        5. **Delete old sessions** to free up resources
        """)


if __name__ == "__main__":
    main()
