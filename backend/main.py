from typing import Dict, Any, List, Optional
import os
from pathlib import Path

# Import config
from config.app_config import LLM_CONFIG, AGENT_CONFIG, PATHS

# Import LLM provider
from backend.llm_providers.ollama_provider import OllamaProvider

# Import agents
from backend.agents.code_agent import CodeAgent
from backend.agents.doc_agent import DocAgent

# Import tools
from backend.tools.code_tools.executor import CodeExecutor
from backend.tools.doc_tools.rag_processor import RAGDocumentProcessor

# Import router
from backend.utils.router import AgentRouter

# Import LangGraph controller
from backend.graphs.agent_controller import create_agent_graph, AgentState

class AgenticAssistant:
    """
    Main controller for the agentic code assistant with RAG support.
    """
    
    def __init__(self):
        """Initialize the agentic assistant with agents and tools."""
        # Initialize LLM provider
        self.llm_provider = OllamaProvider(
            model_name=LLM_CONFIG["model"],
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"]
        )
        
        # Initialize tools
        self.tools = {
            "code_executor": CodeExecutor(),
            "rag_processor": RAGDocumentProcessor(upload_dir=PATHS["uploads"])
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
                tools=[self.tools["rag_processor"]]
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

# Create singleton instance
assistant = AgenticAssistant()

def get_assistant() -> AgenticAssistant:
    """Get the singleton assistant instance."""
    return assistant