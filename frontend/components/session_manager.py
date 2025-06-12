"""
Session management UI component for multi-client support.
Provides interface for creating, managing, and switching between sessions.
"""
import streamlit as st
import time
from typing import Dict, Any, Optional
from datetime import datetime


class SessionManagerUI:
    """UI component for managing client sessions."""
    
    def __init__(self, backend_client, is_sidebar=False):
        self.backend_client = backend_client
        self.is_sidebar = is_sidebar
    
    def render_session_selector(self):
        """Render session selection and management UI."""
        st.subheader("🔗 Session Management")
        
        # Current session status
        if self.backend_client.session_id:
            if not self.is_sidebar:
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.success(f"**Active Session:** `{self.backend_client.session_id[:8]}...`")
                    if self.backend_client.client_id:
                        st.caption(f"Client ID: `{self.backend_client.client_id}`")
                
                with col2:
                    if st.button("🔄", help="Refresh session info"):
                        st.rerun()
            else:
                # Vertical layout for sidebar
                st.success(f"**Active Session:** `{self.backend_client.session_id[:8]}...`")
                if self.backend_client.client_id:
                    st.caption(f"Client ID: `{self.backend_client.client_id}`")
                if st.button("🔄", help="Refresh session info", use_container_width=True):
                    st.rerun()
        else:
            st.warning("⚠️ No active session")
        
        # Session actions
        if not self.is_sidebar:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("➕ New Session", use_container_width=True):
                    self._create_new_session()
            
            with col2:
                if st.button("📋 List Sessions", use_container_width=True):
                    self._show_all_sessions()
            
            with col3:
                if self.backend_client.session_id:
                    if st.button("🗑️ Delete Current", use_container_width=True):
                        self._delete_current_session()
        else:
            # Vertical layout for sidebar
            if st.button("➕ New Session", use_container_width=True):
                self._create_new_session()
            if st.button("📋 List Sessions", use_container_width=True):
                self._show_all_sessions()
            if self.backend_client.session_id:
                if st.button("🗑️ Delete Current", use_container_width=True):
                    self._delete_current_session()
    
    def render_session_details(self):
        """Render detailed session information."""
        if not self.backend_client.session_id:
            return
        
        with st.expander("📊 Session Details", expanded=False):
            session_info = self.backend_client.get_session_info()
            
            if "error" not in session_info:
                if not self.is_sidebar:
                    # Use columns only when not in sidebar
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.metric(
                            "Messages", 
                            session_info.get("conversation_length", 0)
                        )
                        st.metric(
                            "Files", 
                            session_info.get("uploaded_files_count", 0)
                        )
                    
                    with col2:
                        created_at = session_info.get("created_at", "")
                        if created_at:
                            try:
                                created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                st.metric(
                                    "Created", 
                                    created_time.strftime("%H:%M:%S")
                                )
                            except:
                                st.metric("Created", "Unknown")
                        
                        has_assistant = session_info.get("has_assistant", False)
                        st.metric(
                            "Assistant", 
                            "✅ Active" if has_assistant else "❌ Inactive"
                        )
                else:
                    # Vertical layout for sidebar
                    st.metric(
                        "Messages", 
                        session_info.get("conversation_length", 0)
                    )
                    st.metric(
                        "Files", 
                        session_info.get("uploaded_files_count", 0)
                    )
                    
                    created_at = session_info.get("created_at", "")
                    if created_at:
                        try:
                            created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                            st.metric(
                                "Created", 
                                created_time.strftime("%H:%M:%S")
                            )
                        except:
                            st.metric("Created", "Unknown")
                    
                    has_assistant = session_info.get("has_assistant", False)
                    st.metric(
                        "Assistant", 
                        "✅ Active" if has_assistant else "❌ Inactive"
                    )
                
                # Session actions
                st.divider()
                if not self.is_sidebar:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("🧹 Clear Context", use_container_width=True):
                            self._clear_session_context()
                    
                    with col2:
                        if st.button("📤 Export Session", use_container_width=True):
                            self._export_session_data()
                else:
                    # Vertical layout for sidebar
                    if st.button("🧹 Clear Context", use_container_width=True):
                        self._clear_session_context()
                    if st.button("📤 Export Session", use_container_width=True):
                        self._export_session_data()
            else:
                st.error(f"Error loading session details: {session_info['error']}")
    
    def render_session_switcher(self):
        """Render UI for switching between sessions."""
        sessions_data = self.backend_client.list_sessions()
        
        if "error" in sessions_data:
            st.error(f"Failed to load sessions: {sessions_data['error']}")
            return
        
        sessions = sessions_data.get("sessions", {})
        if not sessions:
            st.info("No sessions available")
            return
        
        with st.expander("🔄 Switch Session", expanded=False):
            # Create session options
            session_options = {}
            for session_id, info in sessions.items():
                client_id = info.get("client_id", "Unknown")
                message_count = info.get("conversation_length", 0)
                created_at = info.get("created_at", "")
                
                # Format display name
                display_name = f"{session_id[:8]}... ({client_id}) - {message_count} msgs"
                if created_at:
                    try:
                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        display_name += f" - {created_time.strftime('%H:%M')}"
                    except:
                        pass
                
                session_options[display_name] = session_id
            
            # Session selector
            selected_display = st.selectbox(
                "Select a session:",
                options=list(session_options.keys()),
                index=None,
                placeholder="Choose a session to switch to..."
            )
            
            if selected_display and st.button("🔄 Switch to Session"):
                selected_session_id = session_options[selected_display]
                self._switch_to_session(selected_session_id)
    
    def _create_new_session(self):
        """Create a new session."""
        client_id = f"streamlit_client_{int(time.time())}"
        result = self.backend_client.create_session(client_id)
        
        if "error" not in result:
            st.success(f"✅ New session created: {result.get('session_id', 'Unknown')}")
            # Clear frontend state for new session
            self._clear_frontend_state()
            st.rerun()
        else:
            st.error(f"❌ Failed to create session: {result['error']}")
    
    def _show_all_sessions(self):
        """Display all active sessions."""
        sessions_data = self.backend_client.list_sessions()
        
        if "error" in sessions_data:
            st.error(f"Failed to load sessions: {sessions_data['error']}")
            return
        
        sessions = sessions_data.get("sessions", {})
        stats = sessions_data.get("stats", {})
        
        with st.expander("📋 All Sessions", expanded=True):
            # Show stats
            if not self.is_sidebar:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Sessions", stats.get("total_sessions", 0))
                with col2:
                    st.metric("Active Sessions", stats.get("active_sessions", 0))
                with col3:
                    timeout_mins = stats.get("session_timeout_minutes", 0)
                    st.metric("Timeout (min)", f"{timeout_mins:.0f}")
            else:
                # Vertical layout for sidebar
                st.metric("Total Sessions", stats.get("total_sessions", 0))
                st.metric("Active Sessions", stats.get("active_sessions", 0))
                timeout_mins = stats.get("session_timeout_minutes", 0)
                st.metric("Timeout (min)", f"{timeout_mins:.0f}")
            
            st.divider()
            
            # Show individual sessions
            if sessions:
                for session_id, info in sessions.items():
                    with st.container():
                        if not self.is_sidebar:
                            col1, col2, col3 = st.columns([2, 2, 1])
                            
                            with col1:
                                is_current = session_id == self.backend_client.session_id
                                status = "🟢 Current" if is_current else "⚪ Available"
                                st.write(f"**{session_id[:12]}...** {status}")
                                st.caption(f"Client: {info.get('client_id', 'Unknown')}")
                            
                            with col2:
                                msgs = info.get("conversation_length", 0)
                                files = info.get("uploaded_files_count", 0)
                                st.write(f"📝 {msgs} messages, 📎 {files} files")
                                
                                created_at = info.get("created_at", "")
                                if created_at:
                                    try:
                                        created_time = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                                        st.caption(f"Created: {created_time.strftime('%H:%M:%S')}")
                                    except:
                                        st.caption("Created: Unknown")
                            
                            with col3:
                                if not is_current:
                                    if st.button("🔄", key=f"switch_{session_id}", help="Switch to this session"):
                                        self._switch_to_session(session_id)
                        else:
                            # Vertical layout for sidebar
                            is_current = session_id == self.backend_client.session_id
                            status = "🟢 Current" if is_current else "⚪ Available"
                            st.write(f"**{session_id[:8]}...** {status}")
                            st.caption(f"Client: {info.get('client_id', 'Unknown')}")
                            
                            msgs = info.get("conversation_length", 0)
                            files = info.get("uploaded_files_count", 0)
                            st.caption(f"📝 {msgs} msgs, 📎 {files} files")
                            
                            if not is_current:
                                if st.button(f"Switch", key=f"switch_{session_id}", use_container_width=True):
                                    self._switch_to_session(session_id)
                        
                        st.divider()
                        
            else:
                st.info("No active sessions found")
    
    def _delete_current_session(self):
        """Delete the current session with confirmation."""
        if "confirm_delete_session" not in st.session_state:
            st.session_state.confirm_delete_session = False
        
        if not st.session_state.confirm_delete_session:
            st.session_state.confirm_delete_session = True
            st.warning("⚠️ This will permanently delete the current session. Click 'Delete Current' again to confirm.")
            st.rerun()
        else:
            result = self.backend_client.delete_session()
            if "error" not in result:
                st.success("✅ Session deleted successfully")
                self._clear_frontend_state()
                st.session_state.confirm_delete_session = False
                st.rerun()
            else:
                st.error(f"❌ Failed to delete session: {result['error']}")
                st.session_state.confirm_delete_session = False
    
    def _clear_session_context(self):
        """Clear the current session context."""
        result = self.backend_client.clear_session_context()
        if "error" not in result:
            st.success("✅ Session context cleared")
            # Clear frontend state too
            self._clear_frontend_state()
            st.rerun()
        else:
            st.error(f"❌ Failed to clear context: {result['error']}")
    
    def _switch_to_session(self, session_id: str):
        """Switch to a different session."""
        # Store the new session ID
        old_session_id = self.backend_client.session_id
        self.backend_client.session_id = session_id
        
        # Get session info to verify it exists and get client_id
        session_info = self.backend_client.get_session_info()
        if "error" not in session_info:
            self.backend_client.client_id = session_info.get("client_id")
            st.success(f"✅ Switched to session: {session_id[:8]}...")
            self._clear_frontend_state()
            st.rerun()
        else:
            # Revert if session doesn't exist
            self.backend_client.session_id = old_session_id
            st.error(f"❌ Failed to switch to session: {session_info['error']}")
    
    def _export_session_data(self):
        """Export session data (placeholder for future implementation)."""
        session_info = self.backend_client.get_session_info()
        if "error" not in session_info:
            st.json(session_info)
            st.info("💡 Session export feature will be enhanced in future versions")
        else:
            st.error(f"❌ Failed to export session: {session_info['error']}")
    
    def _clear_frontend_state(self):
        """Clear frontend session state."""
        if 'messages' in st.session_state:
            st.session_state.messages = []
        if 'uploaded_files' in st.session_state:
            st.session_state.uploaded_files = []
        if 'last_agent_used' in st.session_state:
            st.session_state.last_agent_used = None
        if 'last_tool_executions' in st.session_state:
            st.session_state.last_tool_executions = []


def create_session_manager_ui(backend_client, is_sidebar=False) -> SessionManagerUI:
    """Create and return a session manager UI instance."""
    return SessionManagerUI(backend_client, is_sidebar)


def render_session_management_sidebar(backend_client):
    """Render session management in sidebar."""
    session_ui = create_session_manager_ui(backend_client, is_sidebar=True)
    
    with st.sidebar:
        session_ui.render_session_selector()
        session_ui.render_session_details()
        session_ui.render_session_switcher()


def render_session_management_main(backend_client):
    """Render session management in main area."""
    st.title("🔗 Session Management")
    
    session_ui = create_session_manager_ui(backend_client, is_sidebar=False)
    
    # Main session controls
    session_ui.render_session_selector()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        session_ui.render_session_details()
    
    with col2:
        session_ui.render_session_switcher()
    
    st.divider()
    
    # All sessions view
    session_ui._show_all_sessions()