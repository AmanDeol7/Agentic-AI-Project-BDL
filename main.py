#!/usr/bin/env python3
"""
Agentic AI Project - Main Entry Point
This is the main entry point for the Agentic AI application with auto-configuration.
"""

import os
import sys
import asyncio
from pathlib import Path
import warnings

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent
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

def auto_configure_environment():
    """Automatically configure the environment before starting the app."""
    try:
        print("Auto-configuring environment...")
        
        # Import and run auto-configuration
        from auto_setup import auto_configure, update_config
        
        service_type = auto_configure()
        if service_type:
            update_config(service_type)
            print("Environment configured successfully!")
            return True
        else:
            print("Failed to configure environment")
            return False
    except Exception as e:
        print(f"Auto-configuration failed: {e}")
        print("Proceeding with default configuration...")
        return True  # Continue with default config

def main():
    """Main function for the Agentic AI application."""
    try:
        print("🚀 Starting Agentic AI Application")
        print("=" * 50)
        
        # Auto-configure environment
        if not auto_configure_environment():
            print("❌ Environment setup failed. Please check the setup instructions.")
            sys.exit(1)
        
        # Import components after configuration
        from frontend.components.chat_interface import create_chat_interface
        from backend.main import get_assistant
        
        print("🎯 Initializing AI assistant...")
        
        # Get the assistant instance
        assistant = get_assistant()
        
        print("✅ AI assistant initialized successfully!")
        print("🌐 Starting web interface...")
        
        # Create message processor
        def process_message(message: str, conversation_history=None, uploaded_files=None):
            return assistant.process_message(
                message=message,
                conversation_history=conversation_history or [],
                uploaded_files=uploaded_files or []
            )
        
        # Configure Streamlit page
        import streamlit as st
        
        st.set_page_config(
            page_title="Agentic AI Assistant",
            page_icon="🚀",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Page header
        st.title("🚀 Agentic AI Assistant")
        st.markdown(
            """
            Welcome to the **Agentic AI Assistant** - your intelligent companion for code generation, 
            document analysis, and task automation.
            
            **Features:**
            - 💻 **Code Generation & Execution**: Write, analyze, and run code
            - 📄 **Document Processing**: Analyze PDFs, Excel files, and text documents  
            - 🤖 **Multi-Agent Intelligence**: Specialized agents for different tasks
            - 🔧 **Smart Routing**: Automatically selects the best agent for your request
            
            Upload files and start chatting to experience the power of AI agents!
            """
        )
        
        # Create the chat interface
        create_chat_interface(process_message)
        
        # Add system information in sidebar
        with st.sidebar:
            st.subheader("System Information")
            
            # Show configuration
            from config.app_config import LLM_CONFIG
            provider = LLM_CONFIG.get("provider", "unknown")
            model = LLM_CONFIG.get("model", "unknown")
            
            st.info(f"**Provider:** {provider}")
            st.info(f"**Model:** {model}")
            
            # Show available models if using Ollama
            if provider == "ollama":
                try:
                    from config.app_config import get_available_models
                    models = get_available_models()
                    if models:
                        st.success(f"**Available Models:** {len(models)}")
                        with st.expander("Model List"):
                            for model_name in models:
                                st.text(f"• {model_name}")
                except:
                    pass
            
            st.divider()
            st.markdown("**🚀 Quick Actions:**")
            if st.button("🔄 Refresh Environment"):
                st.rerun()
        
    except Exception as e:
        import streamlit as st
        st.error(f"❌ Application failed to start: {str(e)}")
        st.error("Please check the error messages and try restarting.")
        
        with st.expander("Troubleshooting"):
            st.markdown("""
            **Common solutions:**
            1. **Install dependencies:** `pip install -r requirements.txt`
            2. **Setup Ollama:** `./setup-dev.sh` (automated setup)
            3. **Manual Ollama:** `ollama serve` and `ollama pull llama3.2:1b`
            4. **Docker deployment:** `./deploy.sh main`
            5. **Check logs** for specific error details
            """)
        
        print(f"❌ Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
