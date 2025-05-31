from typing import Dict, Any, List, Optional
import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import config
from config.app_config import LLM_CONFIG, AGENT_CONFIG, PATHS, TENSORRT_CONFIG

# Import LLM provider
from backend.llm_providers.ollama_provider import OllamaProvider
from backend.llm_providers.tensorrt_provider import TensorRTProvider

# Import agents
from backend.agents.code_agent import CodeAgent
from backend.agents.doc_agent import DocAgent

# Import tools
from backend.tools.code_tools.executor import CodeExecutor
from backend.tools.doc_tools.document_processor import DocumentProcessor

# Import router
from backend.utils.router import AgentRouter

# Import LangGraph controller
from backend.graphs.agent_controller import create_agent_graph, AgentState

class AgenticAssistant:
    """
    Main controller for the agentic code assistant with TensorRT-LLM support.
    """
    
    def __init__(self, use_tensorrt: bool = True):
        """Initialize the agentic assistant with agents and tools."""
        # Initialize LLM provider based on preference
        if use_tensorrt:
            self.llm_provider = TensorRTProvider(
                server_url="http://localhost:8000",  # Default TensorRT-LLM server
                model_name="llama2",
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"]
            )
            # Fallback to Ollama if TensorRT-LLM is not available
            if not self.llm_provider.is_available():
                print("TensorRT-LLM not available, falling back to Ollama")
                self.llm_provider = OllamaProvider(
                    model_name=LLM_CONFIG["model"],
                    temperature=LLM_CONFIG["temperature"],
                    max_tokens=LLM_CONFIG["max_tokens"]
                )
        else:
            self.llm_provider = OllamaProvider(
                model_name=LLM_CONFIG["model"],
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"]
            )
        
        # Initialize tools with LLM provider
        self.tools = {
            "code_executor": CodeExecutor(),
            "document_processor": DocumentProcessor(
                upload_dir=PATHS["uploads"],
                llm_provider=self.llm_provider
            )
        }
        
        # Initialize agents
        self.agents = {
            "code_agent": CodeAgent(
                name=AGENT_CONFIG["code_agent"]["name"],
                description=AGENT_CONFIG["code_agent"]["description"],
                llm_provider=self.llm_provider,
                tools=[self.tools["code_executor"]]
            ),
            "doc_agent": DocAgent(
                name=AGENT_CONFIG["doc_agent"]["name"],
                description=AGENT_CONFIG["doc_agent"]["description"],
                llm_provider=self.llm_provider,
                tools=[self.tools["document_processor"]]
            )
        }
        
        # Initialize router
        self.router = AgentRouter(self.agents)
        
        # Create agent workflow
        self.workflow = create_agent_graph(
            router=self.router,
            agents=self.agents,
            tools=self.tools
        ).compile()

    def clear_context(self):
        """
        Clear all context and internal state from the assistant.
        This resets the assistant to a fresh state as if newly initialized.
        """
        # Clear any internal state in agents
        for agent in self.agents.values():
            if hasattr(agent, 'clear_context'):
                agent.clear_context()
        
        # Clear any internal state in tools
        for tool in self.tools.values():
            if hasattr(tool, 'clear_context'):
                tool.clear_context()
        
        # Clear any cached results or states in the workflow
        if hasattr(self.workflow, 'clear_context'):
            self.workflow.clear_context()
        
        print("🧹 Backend assistant context cleared successfully")

    def process_query(
        self, 
        query: str, 
        agent_type: str = "doc_agent",
        files: List[str] = None
    ) -> str:
        """
        Process a simple query with optional files (for testing purposes).
        
        Args:
            query: The user query
            agent_type: Type of agent to use
            files: List of file paths to process
            
        Returns:
            The agent's response as a string
        """
        # Use the main process_message method
        result = self.process_message(
            message=query,
            conversation_history=[],
            uploaded_files=files or []
        )
        
        return result.get("response", "")

    def process_message(
        self, 
        message: str, 
        conversation_history: List[Dict[str, str]] = None,
        uploaded_files: List[str] = None
    ) -> Dict[str, Any]:
        """
        Process a user message through the agent workflow.
        
        Args:
            message: User message to process
            conversation_history: Previous conversation history
            uploaded_files: List of uploaded file paths
            
        Returns:
            Response from the selected agent
        """
        # Initialize state
        conversation_history = conversation_history or []
        uploaded_files = uploaded_files or []
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": message
        })
        
        # Create initial state
        initial_state: AgentState = {
            "messages": conversation_history,
            "current_agent": None,
            "tool_calls": [],
            "tool_results": [],
            "uploaded_files": uploaded_files,
            "final_response": None
        }
        
        # Execute workflow
        result = self.workflow.invoke(initial_state)
        
        # Add assistant response to history
        if result["final_response"]:
            conversation_history.append({
                "role": "assistant",
                "content": result["final_response"]
            })
        
        return {
            "response": result["final_response"],
            "agent_used": result["current_agent"],
            "conversation_history": conversation_history,
            "tool_results": result["tool_results"]
        }

# Lazy singleton instance
_assistant = None

def get_assistant() -> AgenticAssistant:
    """Get the singleton assistant instance."""
    global _assistant
    if _assistant is None:
        _assistant = AgenticAssistant()
    return _assistant

def clear_assistant_instance():
    """
    Clear the singleton assistant instance, forcing a fresh initialization on next get_assistant() call.
    This is useful for completely resetting the system state.
    """
    global _assistant
    if _assistant is not None:
        # Clear the assistant's context first
        _assistant.clear_context()
        # Remove the instance to force re-initialization
        _assistant = None
        print("🔄 Assistant instance cleared - will reinitialize on next request")