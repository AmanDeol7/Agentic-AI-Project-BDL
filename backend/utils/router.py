from typing import Dict, Any, List
from ..agents.base_agent import AgentContext, Message

class AgentRouter:
    """
    Router for directing tasks to appropriate agents.
    """
    
    def __init__(self, agents: Dict[str, Any]):
        """
        Initialize the router with available agents.
        
        Args:
            agents: Dictionary of available agents, keyed by agent_id
        """
        self.agents = agents
    
    def route(self, message: str, context: AgentContext) -> Dict[str, Any]:
        """
        Route a message to the appropriate agent.
        
        Args:
            message: User message to route
            context: Current context including conversation history
            
        Returns:
            Dictionary with selected agent and reason
        """
        # If explicitly mentioned in message, route accordingly
        message_lower = message.lower()
        
        # Check if message mentions code-related terms
        code_terms = ["code", "programming", "function", "algorithm", "python", "javascript", "java", "script", "execute", "run"]
        if any(term in message_lower for term in code_terms):
            return {
                "agent_id": "code_agent",
                "reason": "Message contains code-related terms"
            }
        
        # Check if message mentions document-related terms or questions
        doc_terms = ["document", "pdf", "text", "extract", "summarize", "read", "what", "how", "why", "when", "where", "explain", "tell me"]
        if any(term in message_lower for term in doc_terms):
            return {
                "agent_id": "doc_agent",
                "reason": "Message contains document-related terms or questions"
            }
        
        # Check if files are attached in context
        if context.get("uploaded_files"):
            # Heuristic routing based on file types
            pdf_files = [f for f in context.get("uploaded_files") if f.lower().endswith('.pdf')]
            text_files = [f for f in context.get("uploaded_files") if f.lower().endswith(('.txt', '.md', '.doc'))]
            
            if pdf_files or text_files:
                return {
                    "agent_id": "doc_agent",
                    "reason": "Document files detected in context"
                }
            
            code_files = [f for f in context.get("uploaded_files") if f.lower().endswith(
                ('.py', '.js', '.java', '.c', '.cpp', '.html', '.css'))]
            if code_files:
                return {
                    "agent_id": "code_agent", 
                    "reason": "Code files detected in context"
                }
        
        # Default to doc agent for questions, code agent for everything else
        question_indicators = ["what", "how", "why", "when", "where", "?"]
        if any(indicator in message_lower for indicator in question_indicators):
            return {
                "agent_id": "doc_agent",
                "reason": "Question detected - using RAG-enabled document agent"
            }
        
        # Default to code agent if no clear routing found
        return {
            "agent_id": "code_agent",
            "reason": "Default routing when no specific indicators found"
        }