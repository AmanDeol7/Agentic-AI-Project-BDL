#!/usr/bin/env python3
"""
Test TensorRT provider connection to the vLLM server.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.append(str(project_root))

def test_tensorrt_connection():
    """Test TensorRT provider connection."""
    print("🧪 Testing TensorRT Provider Connection")
    print("=" * 50)
    
    try:
        # Test provider directly
        print("1. Testing TensorRT Provider...")
        from backend.llm_providers.tensorrt_provider import TensorRTProvider
        
        provider = TensorRTProvider(
            server_url="http://localhost:8000",
            model_name="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            temperature=0.7,
            max_tokens=100
        )
        
        print(f"   ✅ Provider initialized")
        print(f"   📡 Server URL: {provider.server_url}")
        print(f"   🤖 Model: {provider.model_name}")
        print(f"   📏 Max sequence length: {provider.max_seq_len}")
        
        # Test availability
        print("2. Testing provider availability...")
        available = provider.is_available()
        print(f"   ✅ Provider available: {available}")
        
        if available:
            # Test simple generation
            print("3. Testing simple generation...")
            test_prompt = "Hello! Please respond with just 'Hello back!' and nothing else."
            try:
                response = provider.generate(test_prompt)
                print(f"   ✅ Response received: '{response}'")
            except Exception as e:
                print(f"   ❌ Generation failed: {e}")
        
        # Test assistant initialization
        print("4. Testing assistant initialization...")
        from backend.main import get_assistant
        
        assistant = get_assistant()
        print(f"   ✅ Assistant initialized: {type(assistant.llm_provider).__name__}")
        
        if hasattr(assistant.llm_provider, 'server_url'):
            print(f"   📡 Using TensorRT server: {assistant.llm_provider.server_url}")
            print(f"   🤖 Model: {assistant.llm_provider.model_name}")
        
        print("\n🎉 TensorRT connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error in TensorRT connection test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tensorrt_connection()
    sys.exit(0 if success else 1)
