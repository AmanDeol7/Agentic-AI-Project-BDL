"""
Streamlit chat interface component for the agentic code assistant.
"""
import streamlit as st
from typing import List, Dict, Any, Callable
import os
from pathlib import Path

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

def create_chat_interface(process_message_callback: Callable):
    """
    Create the chat interface component.
    
    Args:
        process_message_callback: Callback function to process user messages
    """
    # Initialize chat state
    initialize_chat_state()
    
    # Create sidebar for agent and tool information
    with st.sidebar:
        st.header("System Information")
        
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
        "Upload a file (PDF, Python script, text file, etc.)",
        type=["pdf", "py", "txt", "csv", "c", "cpp"],
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