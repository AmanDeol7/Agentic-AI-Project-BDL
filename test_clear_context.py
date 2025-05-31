#!/usr/bin/env python3
"""
Test script to verify that the clear context functionality works properly.
"""

import os
import sys
from pathlib import Path
import tempfile

# Add project root to Python path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from backend.main import get_assistant, clear_assistant_instance
from config.app_config import PATHS

def test_clear_context():
    """Test the clear context functionality."""
    print("🧪 Testing Clear Context Functionality")
    print("=" * 50)
    
    try:
        # Create a test document
        test_doc_path = PATHS["uploads"] / "test_clear_context.txt"
        test_content = """
        Test Document for Context Clearing
        
        This document contains important information:
        - The secret code is 12345
        - The project name is ClearTest
        - The status is active
        
        This document should be forgotten after context clearing.
        """
        
        with open(test_doc_path, 'w') as f:
            f.write(test_content)
        print(f"✅ Created test document: {test_doc_path}")
        
        # Step 1: Process a document with the assistant
        print("\n1. Processing document with assistant...")
        assistant = get_assistant()
        
        response1 = assistant.process_message(
            message="What is the secret code mentioned in the document?",
            conversation_history=[],
            uploaded_files=[str(test_doc_path)]
        )
        
        print(f"   Agent used: {response1.get('agent_used', 'None')}")
        print(f"   Response length: {len(response1.get('response', ''))}")
        print(f"   Response preview: {response1.get('response', '')[:200]}...")
        
        # Step 2: Ask again without clearing context (should remember)
        print("\n2. Asking again without clearing context...")
        response2 = assistant.process_message(
            message="What was the secret code again?",
            conversation_history=response1.get('conversation_history', []),
            uploaded_files=[]  # No files passed this time
        )
        
        print(f"   Response preview: {response2.get('response', '')[:200]}...")
        
        # Step 3: Clear the context
        print("\n3. Clearing assistant context...")
        clear_assistant_instance()
        print("   ✅ Context cleared")
        
        # Step 4: Get a fresh assistant and ask the same question
        print("\n4. Getting fresh assistant and asking same question...")
        fresh_assistant = get_assistant()
        
        response3 = fresh_assistant.process_message(
            message="What was the secret code from the document?",
            conversation_history=[],
            uploaded_files=[]  # No files - should not remember
        )
        
        print(f"   Response preview: {response3.get('response', '')[:200]}...")
        
        # Step 5: Verify that context was actually cleared
        print("\n5. Verifying context clearing...")
        
        # The assistant should not know about the document anymore
        if "12345" not in response3.get('response', ''):
            print("   ✅ Context successfully cleared - secret code not remembered")
        else:
            print("   ❌ Context NOT cleared - secret code still remembered")
        
        # Step 6: Test with fresh document
        print("\n6. Testing with fresh document upload...")
        response4 = fresh_assistant.process_message(
            message="What is the secret code mentioned in the document?",
            conversation_history=[],
            uploaded_files=[str(test_doc_path)]
        )
        
        print(f"   Response preview: {response4.get('response', '')[:200]}...")
        
        if "12345" in response4.get('response', ''):
            print("   ✅ Fresh document processing works correctly")
        else:
            print("   ❌ Fresh document processing may have issues")
        
        # Cleanup
        if test_doc_path.exists():
            test_doc_path.unlink()
            print(f"\n🧹 Cleaned up test document")
        
        print("\n🎉 Clear Context Test Completed!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in clear context test: {e}")
        import traceback
        traceback.print_exc()
        
        # Cleanup on error
        if 'test_doc_path' in locals() and test_doc_path.exists():
            test_doc_path.unlink()
        
        return False

if __name__ == "__main__":
    success = test_clear_context()
    sys.exit(0 if success else 1)
