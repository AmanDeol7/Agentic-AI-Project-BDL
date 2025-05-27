"""
Base agent implementation with common functionality.
"""
from typing import Dict, List, Any, Optional
import json
from pydantic import BaseModel, Field

class Message(BaseModel):
    """Message model for agent conversation."""
    role: str = Field(description="Role of the message sender (user, assistant)")
    content: str = Field(description="Content of the message")

class AgentContext(BaseModel):
    """Context for an agent interaction."""
    messages: List[Message] = Field(default_factory=list, description="Conversation history")
    tools_results: Dict[str, Any] = Field(default_factory=dict, description="Results from tool calls")
    uploaded_files: List[str] = Field(default_factory=list, description="List of uploaded file paths")

class BaseAgent:
    """
    Base class for all agents in the system.
    """
    
    def __init__(
        self,
        name: str,
        description: str,
        llm_provider: Any,
        tools: List[Any] = None,
    ):
        """
        Initialize the base agent.
        
        Args:
            name: Name of the agent
            description: Description of the agent's capabilities
            llm_provider: Provider for LLM functionality
            tools: List of tools available to the agent
        """
        self.name = name
        self.description = description
        self.llm_provider = llm_provider
        self.tools = tools or []
        
    def format_system_prompt(self, context: AgentContext) -> str:
        """
        Format the system prompt for the agent.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Formatted system prompt
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def format_conversation_history(self, context: AgentContext) -> str:
        """
        Format the conversation history for the agent.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Formatted conversation history
        """
        history = []
        for message in context.messages:
            history.append(f"{message.role}: {message.content}")
        return "\n".join(history)
    
    def generate_response(self, context: AgentContext) -> str:
        """
        Generate a response based on the current context.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Generated response
        """
        system_prompt = self.format_system_prompt(context)
        conversation_history = self.format_conversation_history(context)
        
        prompt = f"{system_prompt}\n\n{conversation_history}\n\nassistant:"
        return self.llm_provider.generate(prompt)
    
    def analyze_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current task and determine needed tools.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Analysis results
        """
        raise NotImplementedError("Subclasses must implement this method")
    
    def execute_tool(self, tool_name: str, tool_args: Dict[str, Any], context: AgentContext) -> Any:
        """
        Execute a tool with the given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            tool_args: Arguments for the tool
            context: Current context for the agent
            
        Returns:
            Tool execution results
        """
        for tool in self.tools:
            if tool.name == tool_name:
                return tool.run(tool_args, context)
        
        raise ValueError(f"Tool '{tool_name}' not found")