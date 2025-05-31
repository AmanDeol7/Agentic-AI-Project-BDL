#!/usr/bin/env python3
"""
Direct test of AgenticAssistant without LangGraph workflow
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# Import only what we need for basic testing
from config.app_config import LLM_CONFIG, AGENT_CONFIG, PATHS, TENSORRT_CONFIG
from backend.llm_providers.ollama_provider import OllamaProvider
from backend.llm_providers.tensorrt_provider import TensorRTProvider
from backend.agents.doc_agent import DocAgent
from backend.tools.doc_tools.document_processor import DocumentProcessor


def create_test_document():
    """Create a simple test document."""
    uploads_dir = Path(PATHS["uploads"])
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    content = """
# Sales Report Q4 2024

## Summary
Our Q4 results exceeded expectations with strong performance across all metrics.

## Key Results
- Revenue: $12.3 million (15% increase)
- New customers: 45
- Customer satisfaction: 92%
- Market expansion: 2 new regions

## Department Performance
Sales team delivered exceptional results, technology improved efficiency by 25%.

## Challenges
Supply chain delays and increased competition remain concerns for 2025.
"""
    
    test_file = uploads_dir / "q4_report.txt"
    with open(test_file, 'w') as f:
        f.write(content)
    
    return str(test_file)


def test_direct_agent():
    """Test the document agent directly without the workflow."""
    print("🧪 Testing Direct Document Agent (No LangGraph)")
    print("=" * 55)
    
    # Create test document
    print("📁 Creating test document...")
    test_file = create_test_document()
    print(f"✅ Created: {Path(test_file).name}")
    
    # Initialize LLM provider
    print("\n🤖 Initializing LLM provider...")
    try:
        llm_provider = TensorRTProvider(
            server_url="http://localhost:8000",
            model_name="llama2",
            temperature=LLM_CONFIG["temperature"],
            max_tokens=LLM_CONFIG["max_tokens"]
        )
        
        if not llm_provider.is_available():
            print("TensorRT-LLM not available, falling back to Ollama")
            llm_provider = OllamaProvider(
                model_name=LLM_CONFIG["model"],
                temperature=LLM_CONFIG["temperature"],
                max_tokens=LLM_CONFIG["max_tokens"]
            )
        print("✅ LLM provider initialized")
    except Exception as e:
        print(f"❌ LLM provider failed: {e}")
        return
    
    # Initialize document processor
    print("\n📄 Initializing document processor...")
    try:
        doc_processor = DocumentProcessor(
            upload_dir=PATHS["uploads"],
            llm_provider=llm_provider
        )
        print("✅ Document processor initialized")
    except Exception as e:
        print(f"❌ Document processor failed: {e}")
        return
    
    # Initialize document agent
    print("\n🎯 Initializing document agent...")
    try:
        doc_agent = DocAgent(
            name=AGENT_CONFIG["doc_agent"]["name"],
            description=AGENT_CONFIG["doc_agent"]["description"],
            llm_provider=llm_provider,
            tools=[doc_processor]
        )
        print("✅ Document agent initialized")
    except Exception as e:
        print(f"❌ Document agent failed: {e}")
        return
    
    # Test document processing
    print("\n🧪 Testing document processing...")
    try:
        # Test extraction
        result = doc_processor.extract_text(test_file)
        print(f"📄 Extracted {len(result)} characters")
        
        # Test processing with LLM
        process_result = doc_processor.process_document(
            file_path=test_file,
            action="summarize"
        )
        print(f"📊 Processing result: {len(process_result)} characters")
        print(f"📝 Summary preview: {process_result[:150]}...")
        
    except Exception as e:
        print(f"❌ Document processing failed: {e}")
        return
    
    # Test agent response (without workflow)
    print("\n💬 Testing agent response...")
    try:
        from backend.agents.base_agent import AgentContext, Message
        
        # Create context
        context = AgentContext(
            messages=[Message(role="user", content="Summarize the uploaded document")],
            uploaded_files=[test_file]
        )
        
        # Generate response
        response = doc_agent.generate_response(context)
        print(f"🤖 Agent response: {response[:200]}...")
        
    except Exception as e:
        print(f"❌ Agent response failed: {e}")
        return
    
    print("\n✅ All tests completed successfully!")
    print(f"📁 Test file: {test_file}")


if __name__ == "__main__":
    try:
        test_direct_agent()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n💥 Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
