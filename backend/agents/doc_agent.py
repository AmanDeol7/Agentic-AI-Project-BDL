from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentContext

class DocAgent(BaseAgent):
    """
    Agent specialized in document parsing and analysis using RAG.
    """
    
    def format_system_prompt(self, context: AgentContext) -> str:
        """
        Format the system prompt for the RAG-enabled document agent.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Formatted system prompt
        """
        tool_descriptions = ""
        if self.tools:
            tool_descriptions = "Available tools:\n" + "\n".join(
                [f"- {tool.name}: {tool.description}" for tool in self.tools]
            )
        
        files_context = ""
        if context.uploaded_files:
            files_context = "Uploaded files:\n" + "\n".join(
                [f"- {file}" for file in context.uploaded_files]
            )
        
        # Check if we have RAG results in context
        rag_context = ""
        if 'rag_processor' in context.tools_results:
            rag_result = context.tools_results['rag_processor']
            if isinstance(rag_result, dict) and 'rag_prompt' in rag_result:
                # Use the RAG prompt directly
                return rag_result['rag_prompt']
        
        system_prompt = f"""You are {self.name}, {self.description}.
You are a specialized Document Assistant with RAG (Retrieval-Augmented Generation) capabilities.

You have these capabilities:
1. Ingest documents into a vector database for accurate retrieval
2. Answer questions using relevant document context
3. Provide precise information based on document content
4. Maintain source attribution for all answers

When working with documents:
- First ingest new documents into the RAG system
- Use retrieved context to provide accurate answers
- Always cite sources when providing information
- Be clear about the confidence level of your answers
- Don't make up information not present in the documents

{tool_descriptions}
{files_context}
"""
        return system_prompt
    
    def analyze_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current task and determine needed tools.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Analysis results with RAG processing plan
        """
        # Get the latest user message
        if not context.messages:
            return {"action": "respond", "needs_tools": False}
        
        last_user_messages = [msg for msg in context.messages if msg.role == "user"]
        if not last_user_messages:
            return {"action": "respond", "needs_tools": False}
        
        last_user_message = last_user_messages[-1].content.lower()
        
        # Check if there are new files to ingest
        if context.uploaded_files:
            # Check if this is the first time we're seeing these files
            # or if user is asking to process/read them
            if any(keyword in last_user_message for keyword in 
                   ["read", "analyze", "summarize", "process", "ingest", "upload"]):
                return {
                    "action": "use_tool",
                    "tool": "rag_processor",
                    "args": {
                        "action": "ingest",
                        "file": context.uploaded_files[0]  # Use the first file
                    },
                    "needs_tools": True
                }
        
        # Check if this is a query about documents
        if any(keyword in last_user_message for keyword in 
               ["what", "how", "why", "when", "where", "explain", "tell me", "question"]):
            # This looks like a query, use RAG to retrieve context
            return {
                "action": "use_tool",
                "tool": "rag_processor",
                "args": {
                    "action": "query",
                    "query": last_user_messages[-1].content
                },
                "needs_tools": True
            }
        
        # Default action is to respond normally
        return {"action": "respond", "needs_tools": False}