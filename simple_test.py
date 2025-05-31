#!/usr/bin/env python3
"""
Simple test for the TensorRT-LLM Document Agent
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.main import get_assistant
from config.app_config import PATHS
import time


def create_simple_test_document():
    """Create a simple test document."""
    uploads_dir = Path(PATHS["uploads"])
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    content = """
# Company Report 2024

Our company achieved significant growth in 2024:
- Revenue: $50.2 million (25% increase)
- Net Profit: $8.7 million  
- Employees: 250
- Customer Satisfaction: 94%

The sales team exceeded targets, technology improved reliability,
and marketing increased brand awareness by 200%.

Key challenges include competition and supply chain issues.
"""
    
    test_file = uploads_dir / "simple_report.txt"
    with open(test_file, 'w') as f:
        f.write(content)
    
    return str(test_file)


def run_simple_test():
    """Run a simple test of the document agent."""
    print("🚀 Simple TensorRT-LLM Document Agent Test")
    print("=" * 50)
    
    # Create test document
    print("📁 Creating test document...")
    test_file = create_simple_test_document()
    print(f"✅ Created: {Path(test_file).name}")
    
    # Initialize assistant
    print("\n🤖 Initializing assistant...")
    assistant = get_assistant()
    print("✅ Assistant initialized")
    
    # Test scenarios
    test_queries = [
        "Summarize this document",
        "What was the revenue in 2024?",
        "What are the main challenges mentioned?"
    ]
    
    print(f"\n🧪 Running {len(test_queries)} tests...")
    print("-" * 50)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\nTest {i}: {query}")
        
        try:
            start_time = time.time()
            response = assistant.process_query(
                query=f"I have uploaded a document. {query}",
                agent_type="doc_agent",
                files=[test_file]
            )
            end_time = time.time()
            
            print(f"⏱️  Time: {end_time - start_time:.2f}s")
            print(f"📝 Response: {response[:150]}..." if len(response) > 150 else f"📝 Response: {response}")
            print("✅ Success")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    print(f"\n🎯 Test completed!")
    print(f"📁 Test file: {test_file}")


if __name__ == "__main__":
    try:
        run_simple_test()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted")
    except Exception as e:
        print(f"\n💥 Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
