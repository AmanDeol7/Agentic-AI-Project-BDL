"""
Enhanced code agent implementation for better code generation and analysis.
"""
from typing import Dict, List, Any, Optional
from .base_agent import BaseAgent, AgentContext
import json
import re

class CodeAgent(BaseAgent):
    """
    Agent specialized in code generation and analysis with improved capabilities.
    """
    
    def format_system_prompt(self, context: AgentContext) -> str:
        """
        Format the system prompt for the code agent with enhanced instructions.
        
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
You specialize in writing clean, efficient, and well-documented code. When asked to generate code:
1. First understand the requirements carefully, Check which language is required.
2. Plan your approach before writing code
3. Write code that is readable, robust, and follows best practices
4. When writing code, ensure it's standards-compliant and properly handles memory management
5. Explain the key aspects of your implementation
6. Suggest tests or edge cases to consider

You have these capabilities:
1. Generate C, C++ or python code based on user requirements
2. Explain code functionality
3. Debug and improve existing code
4. Work with data from uploaded files
5. Execute code to verify functionality
6. You have the functionality to execute c , c++ or python code.

For C programming specifically:
1. Include necessary headers
2. Use proper memory allocation and deallocation
3. Check return values of functions
4. Prevent buffer overflows
5. Avoid undefined behavior
6. Use clear variable and function naming

{tool_descriptions}
{files_context}

"""
        return system_prompt
    
    def analyze_task(self, context: AgentContext) -> Dict[str, Any]:
        """
        Analyze the current task and determine needed tools with improved logic for generation + execution.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Analysis results with code action plan
        """
        print(f"DEBUG: CodeAgent.analyze_task called with {len(context.messages)} messages")
        
        # Get the latest user message
        if not context.messages:
            print("DEBUG: No messages in context")
            return {"action": "respond", "needs_tools": False}
        
        last_user_messages = [msg for msg in context.messages if msg.role == "user"]
        if not last_user_messages:
            print("DEBUG: No user messages found")
            return {"action": "respond", "needs_tools": False}
        
        last_user_message = last_user_messages[-1].content
        print(f"DEBUG: Last user message: '{last_user_message[:100]}...'")
        
        # Check for "generate and execute" pattern
        generate_and_execute_patterns = [
            r"generate.*and.*execute",
            r"create.*and.*run", 
            r"write.*and.*execute",
            r"code.*and.*run",
            r"generate.*execute.*it",
            r"create.*run.*it"
        ]
        
        is_generate_and_execute = any(
            re.search(pattern, last_user_message.lower()) 
            for pattern in generate_and_execute_patterns
        )
        
        print(f"DEBUG: Is generate and execute request: {is_generate_and_execute}")
        
        if is_generate_and_execute:
            # This is a request to generate code and then execute it
            # We need to generate the code first, then execute it
            # For now, we'll generate a simple response and then look for code to execute
            print("DEBUG: Generate and execute request detected")
            
            # Try to infer the language from the request
            language = "python"  # default
            if any(lang in last_user_message.lower() for lang in ["c code", "c program", " c ", "c++"]):
                language = "c"
            elif any(lang in last_user_message.lower() for lang in ["python", "py"]):
                language = "python"
            
            # For generate and execute requests, we'll need to handle this differently
            # We should generate code first, then execute it in a second pass
            # For now, let's generate the code and mark that execution will be needed
            return {
                "action": "generate_and_execute",
                "needs_tools": False,  # We'll generate first, then execute
                "language": language,
                "generate_first": True
            }
        
        # Check if the message contains execution keywords
        execution_keywords = ["run", "execute", "test", "output", "result", "compile", "run it", "execute it", "run the code", "execute the code"]
        needs_execution = any(keyword in last_user_message.lower() for keyword in execution_keywords)
        
        print(f"DEBUG: Needs execution: {needs_execution}")
        
        if needs_execution:
            print("DEBUG: Execution needed, looking for code...")
            
            # First, check if there's code in the current message
            code_blocks = self.extract_code(last_user_message)
            print(f"DEBUG: Found {len(code_blocks)} code blocks in current message")
            
            if code_blocks:
                # Use code from current message
                for i, block in enumerate(code_blocks):
                    print(f"DEBUG: Code block {i}: language='{block['language']}', length={len(block['code'])}")
                    language = block["language"].lower()
                    if language in ["c", "cpp", "python", "py"]:
                        normalized_lang = "c" if language in ["c", "cpp"] else "python"
                        print(f"DEBUG: Using code block {i} with language {normalized_lang}")
                        return {
                            "action": "use_tool",
                            "tool": "code_executor",
                            "args": {
                                "code": block["code"],
                                "language": normalized_lang
                            },
                            "needs_tools": True
                        }
            
            # If no code in current message, look through conversation history
            print("DEBUG: No executable code in current message, searching conversation history...")
            for i, msg in enumerate(reversed(context.messages)):
                print(f"DEBUG: Checking message {i} (role: {msg.role})")
                
                blocks = self.extract_code(msg.content)
                print(f"DEBUG: Found {len(blocks)} code blocks in message {i}")
                
                if blocks:
                    # Find the most recent executable code block
                    for j, block in enumerate(blocks):
                        print(f"DEBUG: Message {i}, Block {j}: language='{block['language']}', length={len(block['code'])}")
                        language = block["language"].lower()
                        if language in ["c", "cpp", "python", "py"]:
                            normalized_lang = "c" if language in ["c", "cpp"] else "python"
                            print(f"DEBUG: Found executable code! Using block with language {normalized_lang}")
                            print(f"DEBUG: Code preview: {block['code'][:100]}...")
                            return {
                                "action": "use_tool",
                                "tool": "code_executor",
                                "args": {
                                    "code": block["code"],
                                    "language": normalized_lang
                                },
                                "needs_tools": True
                            }
            
            print("DEBUG: Execution requested but no executable code found")
            return {
                "action": "respond", 
                "needs_tools": False,
                "error": "Execution requested but no executable code found in conversation history"
            }
        
        # Check if there's code in the current message that might need execution
        code_blocks = self.extract_code(last_user_message)
        if code_blocks:
            print(f"DEBUG: Found {len(code_blocks)} code blocks, checking for executable code...")
            # If code is provided, assume execution might be wanted
            for i, block in enumerate(code_blocks):
                language = block["language"].lower()
                print(f"DEBUG: Block {i}: language='{language}'")
                if language in ["c", "cpp", "python", "py"]:
                    normalized_lang = "c" if language in ["c", "cpp"] else "python"
                    print(f"DEBUG: Auto-executing code block with language {normalized_lang}")
                    return {
                        "action": "use_tool",
                        "tool": "code_executor",
                        "args": {
                            "code": block["code"],
                            "language": normalized_lang
                        },
                        "needs_tools": True
                    }
        
        print("DEBUG: No tools needed, returning respond action")
        # Default action is to respond with code generation
        return {"action": "respond", "needs_tools": False}
    
    def extract_code(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from text with improved pattern matching.
        
        Args:
            text: Text containing code blocks
            
        Returns:
            List of dictionaries with language and code
        """
        import re
        
        code_blocks = []
        
        # Pattern to match code blocks with optional language specification
        pattern = r"```(\w*)\n(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)
        
        for lang, code in matches:
            lang = lang.strip().lower() or "text"  # Default to text if no language specified
            
            # Normalize language identifiers
            if lang in ["py", "python3"]:
                lang = "python"
            elif lang in ["c++"]:
                lang = "cpp"
            
            # If no language specified, try to infer from code content
            if lang == "text" or lang == "":
                code_lower = code.strip().lower()
                # Check for C/C++ indicators
                if any(indicator in code_lower for indicator in ["#include", "int main", "printf", "malloc", "free"]):
                    if "cout" in code_lower or "std::" in code_lower or "namespace" in code_lower:
                        lang = "cpp"
                    else:
                        lang = "c"
                # Check for Python indicators
                elif any(indicator in code_lower for indicator in ["def ", "import ", "print(", "if __name__", "elif"]):
                    lang = "python"
            
            code_blocks.append({"language": lang, "code": code.strip()})
        
        # Also check for inline code that might be meant for execution
        # Look for patterns like "run this: int main() { ... }"
        inline_pattern = r"(?:run|execute|test)(?:\s+this)?:?\s*([^`\n]+(?:\n[^`\n]+)*)"
        inline_matches = re.findall(inline_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        for code in inline_matches:
            code = code.strip()
            if len(code) > 20:  # Only consider substantial code snippets
                # Try to infer language
                if any(indicator in code.lower() for indicator in ["#include", "int main", "printf"]):
                    code_blocks.append({"language": "c", "code": code})
                elif any(indicator in code.lower() for indicator in ["def ", "print(", "import "]):
                    code_blocks.append({"language": "python", "code": code})
        
        return code_blocks
    
    def generate_response(self, context: AgentContext) -> str:
        """
        Generate a response with enhanced tool result handling and code generation.
        
        Args:
            context: Current context for the agent
            
        Returns:
            Generated response with tool usage details
        """
        print(f"DEBUG: CodeAgent.generate_response called with {len(context.tools_results)} tool results")
        
        # Check if we have code execution results to present
        if context.tools_results and "code_executor" in context.tools_results:
            execution_result = context.tools_results["code_executor"]
            print(f"DEBUG: Found code execution result: {type(execution_result)}")
            
            if isinstance(execution_result, dict):
                success = execution_result.get("success", False)
                language = execution_result.get("language", "unknown")
                output = execution_result.get("output", "")
                error = execution_result.get("error", "")
                
                response = f"## Code Execution Results\n\n"
                
                if success:
                    response += f"**Successfully executed {language.upper()} code**\n\n"
                    if output:
                        response += f"**Output:**\n```\n{output.strip()}\n```\n\n"
                    else:
                        response += "**Output:** (No output produced)\n\n"
                    
                    if error and error.strip():
                        response += f"**Warnings/Messages:**\n```\n{error.strip()}\n```\n\n"
                    
                    response += "The code executed successfully and produced the expected result."
                else:
                    response += f"**Failed to execute {language.upper()} code**\n\n"
                    if error:
                        response += f"**Error:**\n```\n{error.strip()}\n```\n\n"
                        if "compilation error" in error.lower():
                            response += "The code failed to compile. Please check the error message above and fix any syntax or compilation issues."
                        else:
                            response += "There was an issue executing the code. Please check the error message above."
                
                return response
            else:
                print(f"DEBUG: Execution result is not a dict: {execution_result}")
                return f"Error: Unexpected execution result format: {str(execution_result)}"
        
        # Check if this is a generate and execute request that needs code generation
        last_user_message = ""
        if context.messages:
            last_user_messages = [msg for msg in context.messages if msg.role == "user"]
            if last_user_messages:
                last_user_message = last_user_messages[-1].content
        
        # Check for generate and execute patterns
        generate_and_execute_patterns = [
            r"generate.*and.*execute",
            r"create.*and.*run", 
            r"write.*and.*execute",
            r"code.*and.*run",
            r"generate.*execute.*it",
            r"create.*run.*it"
        ]
        
        is_generate_and_execute = any(
            re.search(pattern, last_user_message.lower()) 
            for pattern in generate_and_execute_patterns
        )
        
        if is_generate_and_execute and not context.tools_results:
            # This is a generate and execute request - we should generate code and include execution instruction
            print("DEBUG: Generating code for generate-and-execute request")
            
            # Generate the base response with code
            response = super().generate_response(context)
            
            # Add a note about executing the generated code
            response += "\n\n**Note:** The code above has been generated and is ready for execution. If you'd like to run it, please let me know!"
            
            return response
        
        # Get the base response if no tool results or tool execution failed
        response = super().generate_response(context)
        
        # Add information about tool usage if applicable
        if context.tools_results:
            tool_info = "\n\n**Tool Execution Information:**\n"
            for tool_name, result in context.tools_results.items():
                if isinstance(result, dict):
                    success = result.get("success", False)
                    language = result.get("language", "unknown")
                    
                    status = "Successfully" if success else "Failed to"
                    tool_info += f"- {status} executed {language} code using '{tool_name}' tool.\n"
                    
                    if not success and "error" in result:
                        tool_info += f"  Error: {result['error']}\n"
            
            response += tool_info
        
        return response