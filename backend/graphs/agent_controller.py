"""
Improved LangGraph workflow for orchestrating agents with enhanced "generate and execute" pattern support.
"""
from typing import Dict, Any, List, Tuple, Optional, TypedDict, Annotated
import json
import re
from langgraph.graph import StateGraph, END
from pydantic import BaseModel, Field

class AgentState(TypedDict):
    """State for the agent workflow with enhanced tracking."""
    messages: List[Dict[str, str]]
    current_agent: Optional[str]
    tool_calls: List[Dict[str, Any]]
    tool_results: List[Dict[str, Any]]
    uploaded_files: List[str]
    final_response: Optional[str]
    agent_info: Optional[Dict[str, Any]]
    # New fields for generate and execute pattern
    generated_code: Optional[str]
    code_language: Optional[str]
    execution_requested: bool
    workflow_stage: str  # "routing", "analyzing", "generating", "executing", "responding"

def create_agent_graph(
    router: Any,
    agents: Dict[str, Any],
    tools: Dict[str, Any]
) -> StateGraph:
    """
    Create an improved LangGraph workflow for agent orchestration with better generate-and-execute support.
    
    Args:
        router: Agent router for determining which agent to use
        agents: Dictionary of available agents
        tools: Dictionary of available tools
        
    Returns:
        StateGraph for agent workflow
    """
    # Define the workflow graph
    workflow = StateGraph(AgentState)
    
    def initialize_state(state: AgentState) -> Dict[str, Any]:
        """Initialize the state with default values."""
        return {
            "generated_code": None,
            "code_language": None,
            "execution_requested": False,
            "workflow_stage": "routing"
        }
    
    def route_request(state: AgentState) -> Dict[str, Any]:
        """Route the request to the appropriate agent with enhanced logging."""
        print("DEBUG: route_request called")
        
        # Get the latest message
        if not state["messages"]:
            return {
                "current_agent": "code_agent", 
                "agent_info": {"selection_reason": "Default - no messages"},
                "workflow_stage": "analyzing"
            }
        
        latest_message = next((msg for msg in reversed(state["messages"]) 
                              if msg["role"] == "user"), None)
        
        if not latest_message:
            return {
                "current_agent": "code_agent", 
                "agent_info": {"selection_reason": "Default - no user message"},
                "workflow_stage": "analyzing"
            }
        
        # Create context for routing
        context = {
            "messages": state["messages"],
            "uploaded_files": state["uploaded_files"]
        }
        
        # Route the message
        routing_result = router.route(latest_message["content"], context)
        
        # Add detailed agent information
        agent_info = {
            "name": agents[routing_result["agent_id"]].name,
            "description": agents[routing_result["agent_id"]].description,
            "selection_reason": routing_result.get("reason", "Not specified")
        }
        
        return {
            "current_agent": routing_result["agent_id"],
            "agent_info": agent_info,
            "workflow_stage": "analyzing"
        }
    
    def analyze_task(state: AgentState) -> Dict[str, Any]:
        """Analyze if this is a generate-and-execute request or needs tools."""
        print("DEBUG: analyze_task called")
        
        agent_id = state["current_agent"]
        agent = agents[agent_id]
        
        # Convert state messages to agent context messages
        from ..agents.base_agent import Message, AgentContext
        agent_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in state["messages"]
        ]
        
        context = AgentContext(
            messages=agent_messages,
            uploaded_files=state["uploaded_files"],
            tools_results={}
        )
        
        # Let the agent analyze the task
        analysis = agent.analyze_task(context)
        print(f"DEBUG: Agent analysis result: {analysis}")
        
        # Update agent info with analysis results
        agent_info = state.get("agent_info", {})
        agent_info["task_analysis"] = {
            "needs_tools": analysis.get("needs_tools", False),
            "action": analysis.get("action", "respond")
        }
        
        # Check for generate-and-execute pattern
        if analysis.get("action") == "generate_and_execute":
            print("DEBUG: Generate-and-execute pattern detected")
            return {
                "execution_requested": True,
                "code_language": analysis.get("language", "python"),
                "workflow_stage": "generating",
                "agent_info": agent_info,
                "tool_calls": []  # No immediate tool calls - generate first
            }
        
        # Check if tools are needed immediately
        elif analysis.get("needs_tools", False) or analysis.get("action") == "use_tool":
            tool_name = analysis.get("tool")
            tool_args = analysis.get("args", {})
            
            if not tool_name:
                print(f"DEBUG: Tool needed but no tool name specified")
                return {
                    "tool_calls": [],
                    "workflow_stage": "responding",
                    "agent_info": agent_info
                }
            
            agent_info["tool_requested"] = {
                "name": tool_name,
                "args_summary": {k: v[:50] + '...' if isinstance(v, str) and len(v) > 50 else v 
                                for k, v in tool_args.items()}
            }
            
            print(f"DEBUG: Tool execution requested - {tool_name}")
            
            return {
                "tool_calls": [{
                    "tool": tool_name,
                    "args": tool_args
                }],
                "workflow_stage": "executing",
                "agent_info": agent_info
            }
        
        # Default: just generate a response
        print("DEBUG: No tools needed, proceeding to response generation")
        return {
            "tool_calls": [],
            "workflow_stage": "responding",
            "agent_info": agent_info
        }
    
    def generate_code_response(state: AgentState) -> Dict[str, Any]:
        """Generate code response for generate-and-execute requests."""
        print("DEBUG: generate_code_response called")
        
        agent_id = state["current_agent"]
        agent = agents[agent_id]
        
        # Convert state messages to agent context messages
        from ..agents.base_agent import Message, AgentContext
        agent_messages = [
            Message(role=msg["role"], content=msg["content"]) 
            for msg in state["messages"]
        ]
        
        context = AgentContext(
            messages=agent_messages,
            uploaded_files=state["uploaded_files"],
            tools_results={}
        )
        
        # Generate the code response
        response = agent.generate_response(context)
        print(f"DEBUG: Generated response with {len(response)} characters")
        
        # Extract code from the response for potential execution
        code_blocks = agent.extract_code(response)
        print(f"DEBUG: Found {len(code_blocks)} code blocks in response")
        
        generated_code = None
        code_language = state.get("code_language", "python")
        
        # Find the first executable code block
        for block in code_blocks:
            block_lang = block["language"].lower()
            if block_lang in ["c", "cpp", "python", "py"]:
                generated_code = block["code"]
                code_language = "c" if block_lang in ["c", "cpp"] else "python"
                print(f"DEBUG: Found executable code in {code_language}")
                break
        
        # Prepare for execution if code was found and execution was requested
        updates = {
            "generated_code": generated_code,
            "code_language": code_language,
        }
        
        if generated_code and state.get("execution_requested", False):
            print("DEBUG: Setting up code execution")
            updates.update({
                "tool_calls": [{
                    "tool": "code_executor",
                    "args": {
                        "code": generated_code,
                        "language": code_language
                    }
                }],
                "workflow_stage": "executing",
                "final_response": response  # Store the generation response
            })
        else:
            print("DEBUG: No execution needed, finalizing response")
            updates.update({
                "final_response": response,
                "workflow_stage": "complete"
            })
        
        return updates
    
    def execute_tools(state: AgentState) -> Dict[str, Any]:
        """Execute tools with detailed results tracking."""
        print(f"DEBUG: execute_tools called with {len(state['tool_calls'])} tool calls")
        
        tool_results = []
        agent_info = state.get("agent_info", {})
        tool_execution_info = []
        
        for tool_call in state["tool_calls"]:
            tool_name = tool_call["tool"]
            tool_args = tool_call.get("args", {})
            
            print(f"DEBUG: Executing tool '{tool_name}' with args: {list(tool_args.keys())}")
            
            execution_info = {
                "tool": tool_name,
                "started": True
            }
            
            # Check if the tool exists
            if tool_name not in tools:
                print(f"DEBUG: Tool '{tool_name}' not found")
                execution_info["success"] = False
                execution_info["error"] = f"Tool '{tool_name}' not found"
                
                tool_results.append({
                    "tool": tool_name,
                    "success": False,
                    "result": f"Tool '{tool_name}' not found"
                })
                
                tool_execution_info.append(execution_info)
                continue
            
            # Execute the tool
            tool = tools[tool_name]
            try:
                print(f"DEBUG: About to execute tool {tool_name}")
                
                # Add uploaded files to tool arguments if not present
                if "file" not in tool_args and state["uploaded_files"]:
                    tool_args["file"] = state["uploaded_files"][0]
                
                # Execute the tool - for code_executor, we don't need context
                if tool_name == "code_executor":
                    print(f"DEBUG: Executing code_executor with language: {tool_args.get('language', 'unknown')}")
                    result = tool.run(tool_args)
                    print(f"DEBUG: Code execution result type: {type(result)}")
                else:
                    # Create context for other tools
                    from ..agents.base_agent import Message, AgentContext
                    agent_messages = [
                        Message(role=msg["role"], content=msg["content"]) 
                        for msg in state["messages"]
                    ]
                    context = AgentContext(
                        messages=agent_messages,
                        uploaded_files=state["uploaded_files"],
                        tools_results={}
                    )
                    result = tool.run(tool_args, context)
                
                # Record success/failure
                if isinstance(result, dict):
                    success = result.get("success", "error" not in result)
                else:
                    success = True
                
                execution_info["success"] = success
                
                if not success and isinstance(result, dict) and "error" in result:
                    execution_info["error"] = result["error"]
                
                # Add execution details for code execution
                if tool_name == "code_executor" and isinstance(result, dict):
                    execution_info["language"] = tool_args.get("language", "unknown")
                    if "output" in result:
                        output_summary = result["output"]
                        if len(output_summary) > 100:
                            output_summary = output_summary[:100] + "..."
                        execution_info["output_summary"] = output_summary
                
                tool_results.append({
                    "tool": tool_name,
                    "success": success,
                    "result": result
                })
                
                print(f"DEBUG: Tool execution completed successfully: {success}")
                
            except Exception as e:
                print(f"DEBUG: Exception during tool execution: {str(e)}")
                execution_info["success"] = False
                execution_info["error"] = str(e)
                
                tool_results.append({
                    "tool": tool_name,
                    "success": False,
                    "result": f"Error executing tool: {str(e)}"
                })
            
            tool_execution_info.append(execution_info)
        
        # Update agent info with tool execution results
        agent_info["tool_executions"] = tool_execution_info
        
        print(f"DEBUG: Tool execution phase completed with {len(tool_results)} results")
        
        return {
            "tool_results": tool_results,
            "agent_info": agent_info,
            "workflow_stage": "responding"
        }
    
    def generate_final_response(state: AgentState) -> Dict[str, Any]:
        """Generate the final response, potentially combining generation and execution results."""
        print("DEBUG: generate_final_response called")
        
        agent_id = state["current_agent"]
        agent = agents[agent_id]
        agent_info = state.get("agent_info", {})
        
        # Check if we already have a generation response (from generate-and-execute flow)
        existing_response = state.get("final_response", "")
        
        # If we have tool results (execution results), we need to combine them
        if state["tool_results"]:
            print(f"DEBUG: Combining generation and execution results")
            
            # Create context with tool results for the agent to format the combined response
            from ..agents.base_agent import Message, AgentContext
            agent_messages = [
                Message(role=msg["role"], content=msg["content"]) 
                for msg in state["messages"]
            ]
            
            # Create context with tool results
            tools_results = {}
            for result in state["tool_results"]:
                tools_results[result["tool"]] = result["result"]
                print(f"DEBUG: Added tool result for {result['tool']}: success={result.get('success', 'unknown')}")
            
            context = AgentContext(
                messages=agent_messages,
                uploaded_files=state["uploaded_files"],
                tools_results=tools_results
            )
            
            # Generate the execution results response
            execution_response = agent.generate_response(context)
            
            # Combine generation and execution responses if we have both
            if existing_response and existing_response.strip():
                combined_response = f"{existing_response}\n\n---\n\n{execution_response}"
            else:
                combined_response = execution_response
            
        elif existing_response:
            # We have a generation response but no execution
            print("DEBUG: Using existing generation response")
            combined_response = existing_response
        else:
            # Generate a fresh response
            print("DEBUG: Generating fresh response")
            from ..agents.base_agent import Message, AgentContext
            agent_messages = [
                Message(role=msg["role"], content=msg["content"]) 
                for msg in state["messages"]
            ]
            
            context = AgentContext(
                messages=agent_messages,
                uploaded_files=state["uploaded_files"],
                tools_results={}
            )
            
            combined_response = agent.generate_response(context)
        
        # Add metadata about the workflow
        metadata = f"\n\n---\n**Workflow Information:**\n- Agent: {agent.name} ({agent_id})\n"
        
        # Add routing reason if available
        if "selection_reason" in agent_info:
            metadata += f"- Selected because: {agent_info['selection_reason']}\n"
        
        # Add tool usage information if available
        if state["tool_results"]:
            metadata += "- Tools executed:\n"
            for result in state["tool_results"]:
                tool_name = result["tool"]
                success = result.get("success", False)
                status = "✅" if success else "❌"
                metadata += f"  {status} {tool_name}\n"
        
        # Add generation info if code was generated
        if state.get("generated_code"):
            metadata += f"- Generated {state.get('code_language', 'unknown')} code and executed it\n"
        
        enhanced_response = combined_response + metadata
        
        return {
            "final_response": enhanced_response,
            "workflow_stage": "complete"
        }
    
    # Conditional routing functions
    def should_generate_code(state: AgentState) -> str:
        """Determine if we should generate code first or proceed with tool execution."""
        workflow_stage = state.get("workflow_stage", "analyzing")
        execution_requested = state.get("execution_requested", False)
        
        print(f"DEBUG: should_generate_code - stage: {workflow_stage}, execution_requested: {execution_requested}")
        
        if workflow_stage == "generating":
            return "generate_code"
        elif workflow_stage == "executing" and state.get("tool_calls"):
            return "execute_tools"
        else:
            return "final_response"
    
    def should_execute_after_generation(state: AgentState) -> str:
        """Determine if we need to execute tools after code generation."""
        has_tool_calls = bool(state.get("tool_calls", []))
        workflow_stage = state.get("workflow_stage", "")
        
        print(f"DEBUG: should_execute_after_generation - has_tool_calls: {has_tool_calls}, stage: {workflow_stage}")
        
        if has_tool_calls and workflow_stage == "executing":
            return "execute_tools"
        else:
            return "final_response"
    
    def should_execute_tools(state: AgentState) -> str:
        """Determine whether to execute tools or generate response directly."""
        has_tool_calls = bool(state.get("tool_calls", []))
        workflow_stage = state.get("workflow_stage", "")
        
        print(f"DEBUG: should_execute_tools - has_tool_calls: {has_tool_calls}, stage: {workflow_stage}")
        
        if has_tool_calls and workflow_stage == "executing":
            return "execute_tools"
        else:
            return "final_response"
    
    # Define the nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("route", route_request)
    workflow.add_node("analyze", analyze_task)
    workflow.add_node("generate_code", generate_code_response)
    workflow.add_node("execute_tools", execute_tools)
    workflow.add_node("generate_response", generate_final_response)
    
    # Define the edges
    workflow.add_edge("initialize", "route")
    workflow.add_edge("route", "analyze")
    
    # Conditional routing after analysis
    workflow.add_conditional_edges(
        "analyze",
        should_generate_code,
        {
            "generate_code": "generate_code",
            "execute_tools": "execute_tools",
            "final_response": "generate_response"
        }
    )
    
    # Conditional routing after code generation
    workflow.add_conditional_edges(
        "generate_code",
        should_execute_after_generation,
        {
            "execute_tools": "execute_tools",
            "final_response": "generate_response"
        }
    )
    
    # Always go to final response after tool execution
    workflow.add_edge("execute_tools", "generate_response")
    workflow.add_edge("generate_response", END)
    
    # Set the entry point
    workflow.set_entry_point("initialize")
    
    return workflow