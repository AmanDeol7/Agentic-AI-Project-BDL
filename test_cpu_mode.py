#!/usr/bin/env python3
"""
Test CPU-only mode to avoid CUDA memory issues.
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

# Force CPU-only operation
os.environ['CUDA_VISIBLE_DEVICES'] = ''
os.environ['OLLAMA_GPU_LAYERS'] = '0'

def test_cpu_mode():
    """Test the system in CPU-only mode."""
    print("🧪 Testing CPU-Only Mode")
    print("=" * 40)
    
    try:
        # Test Ollama provider directly
        print("1. Testing Ollama Provider (CPU-only)...")
        from backend.llm_providers.ollama_provider import OllamaProvider
        
        # Initialize with smaller parameters
        provider = OllamaProvider(
            model_name="mistral",  # Use smaller model
            temperature=0.7,
            max_tokens=500  # Smaller output
        )
        
        print(f"   ✅ Provider initialized: {provider.model_name}")
        
        # Test availability
        print("2. Testing provider availability...")
        available = provider.is_available()
        print(f"   ✅ Provider available: {available}")
        
        if available:
            # Test simple generation
            print("3. Testing simple generation...")
            test_prompt = "Hello, please respond with just 'Hello back!'"
            response = provider.generate(test_prompt)
            print(f"   ✅ Response received: {response[:100]}...")
        
        # Test assistant initialization
        print("4. Testing assistant initialization...")
        from backend.main import get_assistant
        
        assistant = get_assistant()
        print(f"   ✅ Assistant initialized: {type(assistant.llm_provider).__name__}")
        
        print("\n🎉 CPU-only mode test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in CPU-only mode test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_cpu_mode()
    sys.exit(0 if success else 1)
