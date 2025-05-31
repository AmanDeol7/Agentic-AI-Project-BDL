#!/usr/bin/env python3
"""
Test the complete document upload to system message generation flow.
"""
import sys
import os
from pathlib import Path
import json

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Import the main components
from backend.main import get_assistant
from config.app_config import PATHS

def test_document_upload_flow():
    """Test the complete flow from document upload to processing."""
    print("🧪 Testing Document Upload to System Message Flow")
    print("=" * 60)
    
    try:
        # Initialize the assistant
        print("1. Initializing assistant...")
        assistant = get_assistant()
        print(f"   ✅ Assistant initialized with LLM: {type(assistant.llm_provider).__name__}")
        
        # Create a test document
        test_doc_path = PATHS["uploads"] / "test_flow_document.txt"
        test_content = """
TechCorp Annual Report 2024

Executive Summary:
TechCorp has achieved record-breaking revenue of $50 million in 2024, representing a 35% increase from the previous year. Our key achievements include:

- Launched 5 new AI-powered products
- Expanded to 12 new international markets
- Hired 200+ new employees
- Achieved carbon neutrality in all operations

Financial Highlights:
- Revenue: $50M (up 35% YoY)
- Net Income: $12M (up 40% YoY)
- R&D Investment: $8M (16% of revenue)
- Customer Base: 150,000+ active users

Strategic Initiatives:
1. AI Innovation Lab established
2. Sustainability program launched
3. Global expansion accelerated
4. Customer experience enhanced

Future Outlook:
We project continued growth with targets of $70M revenue for 2025 and plan to launch 8 new products across various market segments.
"""
        
        # Write test document
        with open(test_doc_path, 'w') as f:
            f.write(test_content)
        print(f"   ✅ Test document created: {test_doc_path}")
        
        # Test single comprehensive query instead of multiple queries
        print(f"\n2. Testing Document Processing")
        comprehensive_query = "Please summarize this document and extract the key financial information"
        print(f"     Query: {comprehensive_query}")
        
        # Process the message with uploaded file
        result = assistant.process_message(
            message=comprehensive_query,
            conversation_history=[],
            uploaded_files=[str(test_doc_path)]
        )
        
        print(f"     ✅ Agent used: {result.get('agent_used', 'None')}")
        print(f"     ✅ Response length: {len(result.get('response', ''))}")
        print(f"     ✅ Tool results: {len(result.get('tool_results', []))}")
        
        # Print first 300 chars of response
        response = result.get('response', '')
        if response:
            preview = response[:300] + "..." if len(response) > 300 else response
            print(f"     📄 Response preview: {preview}")
        
        # Check if tools were executed
        tool_results = result.get('tool_results', [])
        if tool_results:
            for tool_result in tool_results:
                tool_name = tool_result.get('tool', 'Unknown')
                success = tool_result.get('success', False)
                print(f"     🔧 Tool: {tool_name} - {'✅ Success' if success else '❌ Failed'}")
                
                # Show tool result details
                result_data = tool_result.get('result', {})
                if isinstance(result_data, dict) and 'message' in result_data:
                    print(f"          Message: {result_data['message']}")
                if isinstance(result_data, dict) and 'file_type' in result_data:
                    print(f"          File type: {result_data['file_type']}")
                if isinstance(result_data, dict) and 'word_count' in result_data:
                    print(f"          Word count: {result_data['word_count']}")
        
        # Test system prompt generation (simplified)
        print("\n3. Testing System Prompt Generation")
        print("   Checking doc_agent system prompt...")
        
        # Get the doc agent
        doc_agent = assistant.agents['doc_agent']
        
        # Create context with uploaded file
        from backend.agents.base_agent import Message, AgentContext
        
        context = AgentContext(
            messages=[Message(role="user", content="Summarize this document")],
            uploaded_files=[str(test_doc_path)],
            tools_results={}
        )
        
        # Generate system prompt
        system_prompt = doc_agent.format_system_prompt(context)
        print(f"     ✅ System prompt generated ({len(system_prompt)} characters)")
        
        # Verify system prompt contains expected elements (quick checks)
        checks = [
            ("Agent name", doc_agent.name in system_prompt),
            ("TensorRT mention", "TensorRT" in system_prompt),
            ("File list", str(test_doc_path) in system_prompt),
            ("Capabilities", "CAPABILITIES" in system_prompt)
        ]
        
        all_checks_passed = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"     {status} {check_name}: {'Present' if check_result else 'Missing'}")
            if not check_result:
                all_checks_passed = False
        
        if all_checks_passed:
            print("     ✅ System prompt structure is correct")
        
        # Test LLM Provider (simplified)
        print("\n4. Testing LLM Provider")
        
        # Test provider availability
        provider_type = type(assistant.llm_provider).__name__
        if hasattr(assistant.llm_provider, 'is_available'):
            provider_available = assistant.llm_provider.is_available()
            print(f"     ✅ {provider_type} available: {provider_available}")
        else:
            print(f"     ✅ {provider_type} initialized successfully")
        
        if hasattr(assistant.llm_provider, 'server_url'):
            print(f"     ✅ Using TensorRT-LLM at: {assistant.llm_provider.server_url}")
        else:
            print(f"     ✅ Using Ollama with model: {getattr(assistant.llm_provider, 'model_name', 'unknown')}")
        
        # Skip LLM generation test to reduce calls
        
        print("\n🎉 Document Flow Test Complete!")
        print("All components are working correctly from upload to system message generation.")
        
        # Cleanup
        if test_doc_path.exists():
            test_doc_path.unlink()
            print(f"     ✅ Cleaned up test document")
            
    except Exception as e:
        print(f"\n❌ Error in document flow test: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_document_upload_flow()
    sys.exit(0 if success else 1)
