"""
Main Streamlit app for the agentic code assistant.
"""
import streamlit as st
import sys
import os
import asyncio
from pathlib import Path
import warnings

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

# Import backend after event loop configuration
from backend.main import get_assistant

def initialize_assistant():
    """Initialize the assistant with proper error handling."""
    try:
        with st.spinner("Initializing assistant..."):
            assistant = get_assistant()
            # Test the assistant with a simple query to ensure everything is loaded
            test_response = assistant.process_message("Hello")
            if not test_response or "error" in test_response:
                raise Exception("Assistant initialization test failed")
            return assistant
    except Exception as e:
        st.error(f"Failed to initialize assistant: {str(e)}")
        st.error("Please check your environment and try again.")
        return None

def main():
    """Main function for the Streamlit app."""
    try:
        # Configure the page
        st.set_page_config(
            page_title="Agentic Code Assistant",
            page_icon="🧠",
            layout="wide"
        )
        
        # Initialize session state if not exists
        if 'assistant' not in st.session_state:
            assistant = initialize_assistant()
            if assistant is None:
                st.stop()
            st.session_state.assistant = assistant
        
        # Page title
        st.title("🧠 Agentic Code Assistant")
        st.markdown(
            """
            This is a locally running AI assistant that can help you with:
            - 💻 Writing and analyzing code
            - 📄 Extracting information from documents
            
            Upload files and start chatting!
            """
        )
        
        # Create the chat interface using the session state assistant
        create_chat_interface(st.session_state.assistant.process_message)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please try restarting the application.")
        if 'assistant' in st.session_state:
            del st.session_state.assistant

if __name__ == "__main__":
    main()