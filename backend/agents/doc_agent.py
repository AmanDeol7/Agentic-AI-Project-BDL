from typing import Dict, List, Any, Optional
import logging
from .base_agent import BaseAgent, AgentContext

logger = logging.getLogger(__name__)

class DocAgent(BaseAgent):
    """
    Agent specialized in document parsing and analysis using TensorRT-LLM.
    Provides intelligent document processing, analysis, and question-answering capabilities.
    """
    
    def format_system_prompt(self, context: AgentContext) -> str:
        """
        Format the system prompt for the document agent with TensorRT-LLM specific capabilities.
        
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
        
        system_prompt = f"""You are {self.name}, {self.description}.
You are a specialized Document Assistant powered by TensorRT-LLM.

CAPABILITIES:
1. Parse and extract information from documents (PDF, Word, Excel, CSV, text)
2. Provide intelligent document analysis and summarization
3. Answer complex questions about document content
4. Perform document comparison and cross-referencing
5. Extract key insights and patterns from documents
6. Generate structured summaries and reports
7. If there is no file available in your context, just say that no document is uploaded.
PROCESSING POWER:
- Powered by TensorRT-LLM for high-performance inference
- Optimized for large document processing
- Capable of handling complex analytical tasks
- Falls back to Ollama if needed for reliability

DOCUMENT FORMATS SUPPORTED:
- PDF documents
- Microsoft Word (.docx)
- Excel spreadsheets (.xlsx)
- CSV files
- Plain text files

{tool_descriptions}
{files_context}

INSTRUCTIONS:
- Always process documents thoroughly before answering questions
- Provide detailed, accurate information based on document content
- Use tools to extract and analyze document data when needed
- If multiple documents are uploaded, consider relationships between them
- Highlight key findings and important information clearly
"""
        return system_prompt

    def analyze_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current task and determine needed tools with enhanced TensorRT-LLM logic.
        
        Args:
            context: Current context for the agent
        
        Returns:
            Analysis results with specific tool and action recommendations
        """
        # Get the latest user message
        if not context.messages:
            return {"action": "respond", "needs_tools": False}
        
        last_user_messages = [msg for msg in context.messages if msg.role == "user"]
        if not last_user_messages:
            return {"action": "respond", "needs_tools": False}
        
        last_user_message = last_user_messages[-1].content.lower()
        
        # Enhanced document processing logic with TensorRT-LLM capabilities
        if context.uploaded_files:
            # Determine the type of document processing needed
            if any(keyword in last_user_message for keyword in 
                   ["summarize", "summary", "overview", "main points"]):
                return {
                    "action": "use_tool",
                    "tool": "document_processor",
                    "args": {
                        "action": "summarize",
                        "file": context.uploaded_files[0]
                    },
                    "needs_tools": True,
                    "reason": "User requested document summarization"
                }
            
            elif any(keyword in last_user_message for keyword in 
                     ["analyze", "analysis", "insights", "patterns", "key findings"]):
                return {
                    "action": "use_tool",
                    "tool": "document_processor",
                    "args": {
                        "action": "analyze",
                        "file": context.uploaded_files[0]
                    },
                    "needs_tools": True,
                    "reason": "User requested document analysis"
                }
            
            elif any(keyword in last_user_message for keyword in 
                     ["read", "extract", "content", "text", "information"]):
                return {
                    "action": "use_tool",
                    "tool": "document_processor",
                    "args": {
                        "action": "extract",
                        "file": context.uploaded_files[0]
                    },
                    "needs_tools": True,
                    "reason": "User requested content extraction"
                }
            
            elif any(keyword in last_user_message for keyword in 
                     ["question", "what", "how", "when", "where", "why", "find"]):
                return {
                    "action": "use_tool",
                    "tool": "document_processor",
                    "args": {
                        "action": "question_answer",
                        "file": context.uploaded_files[0],
                        "question": last_user_messages[-1].content
                    },
                    "needs_tools": True,
                    "reason": "User asked a question about the document"
                }
            
            # Default processing for uploaded files
            return {
                "action": "use_tool",
                "tool": "document_processor",
                "args": {
                    "action": "process",
                    "file": context.uploaded_files[0]
                },
                "needs_tools": True,
                "reason": "General document processing needed"
            }
        
        # If no files but user mentions document-related tasks
        elif any(keyword in last_user_message for keyword in 
                 ["document", "file", "upload", "pdf", "word", "excel"]):
            return {
                "action": "respond",
                "needs_tools": False,
                "suggestion": "Please upload a document to analyze"
            }
        
        # Default action is to respond normally
        return {"action": "respond", "needs_tools": False}