"""
Streamlit chat interface component for the agentic code assistant.
"""
import streamlit as st
from typing import List, Dict, Any, Callable
import os
from pathlib import Path

def clear_system_context(remove_files_from_disk=False, backend_client=None):
    """
    Clear all system context including messages, files, and tool results.
    
    Args:
        remove_files_from_disk: If True, also delete uploaded files from disk
        backend_client: BackendClient instance for session-based clearing
    """
    # Get list of files to potentially remove before clearing session state
    files_to_remove = st.session_state.uploaded_files.copy() if remove_files_from_disk else []
    
    # Clear frontend session state
    st.session_state.messages = []
    st.session_state.uploaded_files = []
    st.session_state.last_agent_used = None
    st.session_state.last_tool_executions = []
    
    # Clear backend assistant context
    try:
        if backend_client and hasattr(backend_client, 'clear_session_context'):
            # Use session-based clearing if available
            result = backend_client.clear_session_context()
            if "error" not in result:
                st.success("🧹 Session context cleared successfully")
            else:
                st.warning(f"Could not clear session context: {result['error']}")
        else:
            # Fallback to legacy method
            from backend.main import clear_assistant_instance
            clear_assistant_instance()
            st.success("🧹 Backend context cleared successfully")
    except Exception as e:
        st.warning(f"Could not clear backend context: {str(e)}")
    
    # Clear uploaded files from disk if requested
    if remove_files_from_disk and files_to_remove:
        removed_count = 0
        for file_path in files_to_remove:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    removed_count += 1
            except Exception as e:
                st.warning(f"Could not remove file {os.path.basename(file_path)}: {str(e)}")
        
        if removed_count > 0:
            st.info(f"🗂️ Removed {removed_count} files from disk")

def initialize_chat_state():
    """Initialize the chat state in the Streamlit session."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    
    # Add new state variables for tracking agent and tool usage
    if "last_agent_used" not in st.session_state:
        st.session_state.last_agent_used = None
        
    if "last_tool_executions" not in st.session_state:
        st.session_state.last_tool_executions = []

def display_chat_messages():
    """Display the chat messages in the Streamlit UI."""
    for message in st.session_state.messages:
        role = message["role"]
        content = message["content"]
        
        with st.chat_message(role):
            st.markdown(content)

def create_chat_interface(process_message_callback: Callable, backend_client=None):
    """
    Create the chat interface component.
    
    Args:
        process_message_callback: Callback function to process user messages
        backend_client: Backend client instance for session management
    """
    # Initialize chat state
    initialize_chat_state()
    
    # Create sidebar for agent and tool information
    with st.sidebar:
        st.header("System Information")
        
        # Show session information if backend_client is available
        if backend_client and hasattr(backend_client, 'session_id'):
            st.subheader("Session Info")
            if backend_client.session_id:
                st.success(f"Session: `{backend_client.session_id[:8]}...`")
                if backend_client.client_id:
                    st.info(f"Client: `{backend_client.client_id}`")
            else:
                st.warning("No active session")
        
        # Add clear context button at the top
        st.subheader("System Control")
        
        # Show current context stats
        message_count = len(st.session_state.messages)
        file_count = len(st.session_state.uploaded_files)
        tool_count = len(st.session_state.last_tool_executions)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.metric("Messages", message_count)
            st.metric("Files", file_count)
        with col2:
            st.metric("Tools Used", tool_count)
            st.metric("Agent", st.session_state.last_agent_used or "None")
        
        # Clear context button with confirmation
        if message_count > 0 or file_count > 0:
            # Add options for clearing
            st.markdown("**Clear Options:**")
            
            col1, col2 = st.columns(2)
            with col1:
                clear_basic = st.button("🗑️ Clear Chat", 
                                       type="secondary", 
                                       help="Clear messages and session state only",
                                       use_container_width=True)
            with col2:
                clear_complete = st.button("🧹 Clear All", 
                                         type="secondary", 
                                         help="Clear everything including backend context",
                                         use_container_width=True)
            
            # Handle basic clear
            if clear_basic:
                if "confirm_clear_basic" not in st.session_state:
                    st.session_state.confirm_clear_basic = False
                
                if not st.session_state.confirm_clear_basic:
                    st.session_state.confirm_clear_basic = True
                    st.warning("⚠️ This will clear chat history and uploaded files. Click again to confirm.")
                    st.rerun()
                else:
                    # Clear only frontend state
                    st.session_state.messages = []
                    st.session_state.uploaded_files = []
                    st.session_state.last_agent_used = None
                    st.session_state.last_tool_executions = []
                    st.session_state.confirm_clear_basic = False
                    st.success("✅ Chat history cleared!")
                    st.rerun()
            
            # Handle complete clear
            if clear_complete:
                if "confirm_clear_complete" not in st.session_state:
                    st.session_state.confirm_clear_complete = False
                
                if not st.session_state.confirm_clear_complete:
                    st.session_state.confirm_clear_complete = True
                    st.warning("⚠️ This will completely reset the system including backend context. Click again to confirm.")
                    st.rerun()
                else:
                    # Get the remove files option
                    remove_files = st.session_state.get('remove_files_option', False)
                    clear_system_context(remove_files_from_disk=remove_files, backend_client=backend_client)
                    st.session_state.confirm_clear_complete = False
                    
                    # Force reinitialization of assistant in the main app
                    if 'assistant' in st.session_state:
                        del st.session_state.assistant
                    
                    st.success("✅ Complete system reset successful!")
                    st.rerun()
            
            # Add option to clear files from disk
            if st.session_state.uploaded_files:
                st.session_state.remove_files_option = st.checkbox(
                    "🗂️ Also remove uploaded files from disk", 
                    help="Delete the actual files from the uploads directory"
                )
        else:
            st.info("💡 No context to clear")
        
        # Reset confirmation if user does something else
        if "confirm_clear_basic" in st.session_state and st.session_state.confirm_clear_basic:
            if st.button("❌ Cancel", type="primary", use_container_width=True):
                st.session_state.confirm_clear_basic = False
                st.rerun()
        
        if "confirm_clear_complete" in st.session_state and st.session_state.confirm_clear_complete:
            if st.button("❌ Cancel", type="primary", use_container_width=True):
                st.session_state.confirm_clear_complete = False
                st.rerun()
        
        st.divider()
        
        # Display current agent information
        st.subheader("Active Agent")
        if st.session_state.last_agent_used:
            agent_name = st.session_state.last_agent_used
            if agent_name == "code_agent":
                agent_emoji = "💻"
                agent_desc = "Code generation and analysis"
            elif agent_name == "doc_agent":
                agent_emoji = "📄"
                agent_desc = "Document parsing and analysis"
            else:
                agent_emoji = "🤖"
                agent_desc = "Unknown agent type"
                
            st.markdown(f"**{agent_emoji} {agent_name.replace('_', ' ').title()}**")
            st.markdown(f"_{agent_desc}_")
        else:
            st.markdown("_No agent used yet_")
        
        # Display tool execution information
        st.subheader("Tools Executed")
        if st.session_state.last_tool_executions:
            for i, tool_info in enumerate(st.session_state.last_tool_executions):
                tool_name = tool_info.get("tool", "Unknown tool")
                success = tool_info.get("success", False)
                
                if tool_name == "code_executor":
                    tool_emoji = "⚙️"
                elif tool_name == "pdf_loader":
                    tool_emoji = "📎"
                else:
                    tool_emoji = "🔧"
                
                status_emoji = "✅" if success else "❌"
                
                with st.expander(f"{tool_emoji} {tool_name} {status_emoji}"):
                    result = tool_info.get("result", {})
                    
                    # Display different information based on tool type
                    if tool_name == "code_executor":
                        if "output" in result:
                            st.code(result["output"], language="text")
                        if "error" in result and result["error"]:
                            st.error(result["error"])
                        if "compilation" in result:
                            st.info(f"Compilation: {result['compilation']}")
                        if "language" in result:
                            st.info(f"Language: {result['language'].upper()}")
                    elif tool_name == "pdf_loader":
                        if "num_pages" in result:
                            st.info(f"Extracted {result['num_pages']} pages")
                        if "error" in result:
                            st.error(result["error"])
                    else:
                        st.json(result)
        else:
            st.markdown("_No tools executed yet_")
    
    # Display chat messages
    display_chat_messages()
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Upload a file (PDF, Excel, Python script, text file, etc.)",
        type=["pdf", "py", "txt", "csv", "c", "cpp", "xlsx", "xls", "docx", "doc", "md"],
        key="file_uploader"
    )
    
    # Handle file upload
    if uploaded_file is not None:
        # Create a file path in the uploads directory
        # Get path from config (or use a default)
        try:
            from config.app_config import PATHS
            upload_dir = PATHS["uploads"]
        except (ImportError, KeyError):
            upload_dir = Path("./data/uploads")
            upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the file
        file_path = os.path.join(upload_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Add to session state if not already there
        if file_path not in st.session_state.uploaded_files:
            st.session_state.uploaded_files.append(file_path)
            st.success(f"File uploaded: {uploaded_file.name}")
    
    # Display currently uploaded files
    if st.session_state.uploaded_files:
        with st.expander("Uploaded Files"):
            for file_path in st.session_state.uploaded_files:
                file_name = os.path.basename(file_path)
                st.text(file_name)
                
                # Add a button to remove the file
                if st.button(f"Remove {file_name}", key=f"remove_{file_name}"):
                    st.session_state.uploaded_files.remove(file_path)
                    st.rerun()
    
    # Chat input
    if prompt := st.chat_input("What do you want to know?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from backend
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = process_message_callback(
                        message=prompt,
                        conversation_history=st.session_state.messages,
                        uploaded_files=st.session_state.uploaded_files
                    )
                    
                    # Display response
                    st.markdown(response["response"])
                    
                    # Update conversation history
                    st.session_state.messages = response["conversation_history"]
                    
                    # Update agent and tool information in session state
                    st.session_state.last_agent_used = response.get("agent_used")
                    st.session_state.last_tool_executions = response.get("tool_results", [])
                    
                    # Force a rerun to update the sidebar with tool results
                    st.rerun()
                except Exception as e:
                    st.error(f"Error processing message: {str(e)}")
                    st.error("Please try again or restart the application.")