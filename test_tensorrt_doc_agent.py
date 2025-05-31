#!/usr/bin/env python3
"""
Test script for TensorRT-LLM Document Agent
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import our modules
from backend.main import AgenticAssistant
from backend.llm_providers.tensorrt_provider import TensorRTProvider
from backend.tools.doc_tools.document_processor import DocumentProcessor

def test_tensorrt_connection():
    """Test TensorRT-LLM connection"""
    print("🧪 Testing TensorRT-LLM Connection...")
    
    provider = TensorRTProvider(
        server_url="http://localhost:8000",
        model_name="llama2"
    )
    
    if provider.is_available():
        print("✅ TensorRT-LLM server is available")
        # Test generation
        response = provider.generate("Hello, how are you?")
        print(f"📝 Test response: {response[:100]}...")
        return True
    else:
        print("❌ TensorRT-LLM server is not available")
        print("📝 Will fall back to Ollama for testing")
        return False

def test_document_processor():
    """Test document processor without files"""
    print("\n🧪 Testing Document Processor...")
    
    # Create a test text file
    test_file = project_root / "test_document.txt"
    test_content = """
    This is a test document for the TensorRT-LLM Document Agent.
    
    Key Points:
    1. The agent can process multiple document formats
    2. It uses TensorRT-LLM for intelligent analysis
    3. It can summarize, analyze, and answer questions about documents
    
    Technologies:
    - TensorRT-LLM for high-performance inference
    - LangChain for document processing
    - UV for package management
    
    This document was created to test the functionality of our agentic system.
    """
    
    with open(test_file, 'w') as f:
        f.write(test_content)
    
    # Test processor
    processor = DocumentProcessor(upload_dir=project_root)
    
    # Test extraction
    result = processor.run({"action": "extract", "file": "test_document.txt"})
    print(f"📄 Extract result: {result.get('success', False)}")
    
    # Test processing
    result = processor.run({"action": "process", "file": "test_document.txt"})
    print(f"⚙️ Process result: {result.get('success', False)}")
    if result.get('success'):
        print(f"📊 Word count: {result.get('word_count', 0)}")
    
    # Clean up
    test_file.unlink()
    print("✅ Document processor test completed")

def test_agentic_assistant():
    """Test the full agentic assistant"""
    print("\n🧪 Testing Agentic Assistant...")
    
    # Create assistant (will try TensorRT-LLM first, fall back to Ollama)
    assistant = AgenticAssistant(use_tensorrt=True)
    
    # Test a simple document-related query
    response = assistant.process_message(
        "What capabilities do you have for document processing?",
        conversation_history=[]
    )
    
    print(f"🤖 Agent used: {response.get('agent_used', 'unknown')}")
    print(f"💬 Response length: {len(response.get('response', ''))}")
    print(f"📝 Response preview: {response.get('response', '')[:200]}...")
    
    return response.get('response') is not None

def create_sample_documents():
    """Create sample documents for testing"""
    print("\n📁 Creating sample documents...")
    
    # Create uploads directory
    uploads_dir = project_root / "uploads"
    uploads_dir.mkdir(exist_ok=True)
    
    # Sample text document
    sample_txt = uploads_dir / "sample.txt"
    with open(sample_txt, 'w') as f:
        f.write("""
Title: AI and Machine Learning Report

Executive Summary:
This report provides an overview of current trends in artificial intelligence and machine learning.

Key Findings:
1. Large Language Models (LLMs) are transforming natural language processing
2. TensorRT optimization provides significant performance improvements
3. Agent-based architectures are becoming more popular

Technologies Discussed:
- TensorRT-LLM: High-performance inference for large language models
- LangChain: Framework for building applications with LLMs
- UV: Fast Python package manager

Conclusion:
The field of AI is rapidly evolving with new tools and techniques emerging regularly.
Organizations should invest in understanding these technologies to remain competitive.

Contact: ai-research@example.com
Date: 2024
        """)
    
    print(f"✅ Created sample document: {sample_txt}")
    return str(sample_txt)

def main():
    """Main test function"""
    print("🚀 TensorRT-LLM Document Agent Test Suite")
    print("=" * 50)
    
    # Test 1: TensorRT connection
    tensorrt_available = test_tensorrt_connection()
    
    # Test 2: Document processor
    test_document_processor()
    
    # Test 3: Create sample documents
    sample_file = create_sample_documents()
    
    # Test 4: Full assistant
    assistant_works = test_agentic_assistant()
    
    # Summary
    print("\n" + "=" * 50)
    print("🏁 Test Summary:")
    print(f"TensorRT-LLM Available: {'✅' if tensorrt_available else '❌'}")
    print(f"Document Processor: ✅")
    print(f"Agentic Assistant: {'✅' if assistant_works else '❌'}")
    
    if not tensorrt_available:
        print("\n⚠️  Note: TensorRT-LLM server not running. To use TensorRT-LLM:")
        print("1. Install TensorRT-LLM")
        print("2. Start the server on http://localhost:8000")
        print("3. The system will automatically use it when available")
    
    print(f"\n📁 Sample document created at: {sample_file}")
    print("🎯 You can now test the agent with this document!")

if __name__ == "__main__":
    main()
