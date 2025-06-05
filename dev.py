#!/usr/bin/env python3
"""
Local Development Setup Script
Automatically detects and configures the best available LLM provider:
1. TensorRT-LLM (if available)
2. Ollama (fallback)

Usage:
    python dev.py              # Start with auto-detection
    python dev.py --ollama      # Force Ollama
    python dev.py --tensorrt    # Force TensorRT
    python dev.py --setup       # Install dependencies only
"""

import os
import sys
import subprocess
import requests
import time
import argparse
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))

def check_command(command):
    """Check if a command is available."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_service(url, timeout=2):
    """Check if a service is available at the given URL."""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def start_ollama():
    """Start Ollama service."""
    print("🔄 Starting Ollama...")
    try:
        # Start Ollama in background
        subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for it to start
        for i in range(10):
            if check_service("http://localhost:11434"):
                print("✅ Ollama started successfully")
                return True
            time.sleep(1)
            print(f"   Waiting for Ollama... ({i+1}/10)")
        
        print("❌ Failed to start Ollama")
        return False
    except Exception as e:
        print(f"❌ Error starting Ollama: {e}")
        return False

def ensure_ollama_model(model="mistral:7b"):
    """Ensure the specified model is available in Ollama."""
    print(f"🔄 Checking for model: {model}")
    try:
        # Check if model exists
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if model in result.stdout:
            print(f"✅ Model {model} already available")
            return True
        
        # Pull the model
        print(f"📦 Pulling model: {model} (this may take a few minutes...)")
        subprocess.run(["ollama", "pull", model], check=True)
        print(f"✅ Model {model} installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install model {model}: {e}")
        return False

def setup_config(provider, model):
    """Update the configuration for the detected provider."""
    config_file = PROJECT_ROOT / "config" / "app_config.py"
    
    # Read current config
    with open(config_file, 'r') as f:
        content = f.read()
    
    # Update LLM_CONFIG
    if provider == "tensorrt":
        new_config = '''LLM_CONFIG = {
    "provider": "tensorrt",
    "model": "mistral-7b-instruct-v0.1",
    "base_url": "http://localhost:8000",
    "temperature": 0.7,
    "max_tokens": 1000
}'''
    else:  # ollama
        new_config = f'''LLM_CONFIG = {{
    "provider": "ollama",
    "model": "{model}",
    "base_url": "http://localhost:11434",
    "temperature": 0.7,
    "max_tokens": 1000
}}'''
    
    # Replace the LLM_CONFIG section
    import re
    pattern = r'LLM_CONFIG = \{[^}]*\}'
    new_content = re.sub(pattern, new_config, content, flags=re.DOTALL)
    
    # Write back
    with open(config_file, 'w') as f:
        f.write(new_content)
    
    print(f"✅ Configuration updated for {provider}")

def detect_provider():
    """Detect the best available LLM provider."""
    print("🔍 Detecting available LLM providers...")
    
    # Check TensorRT-LLM
    if check_service("http://localhost:8000/v2/health"):
        print("✅ TensorRT-LLM server detected")
        return "tensorrt", "mistral-7b-instruct-v0.1"
    
    # Check Ollama
    if check_service("http://localhost:11434"):
        print("✅ Ollama server detected")
        return "ollama", "mistral:7b"
    
    # Try to start Ollama
    if check_command("ollama"):
        if start_ollama():
            return "ollama", "mistral:7b"
    
    print("❌ No LLM provider available")
    print("💡 Please install either:")
    print("   - TensorRT-LLM server (for GPU acceleration)")
    print("   - Ollama (https://ollama.ai/)")
    return None, None

def install_dependencies():
    """Install Python dependencies."""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_streamlit():
    """Start the Streamlit application."""
    print("🚀 Starting Streamlit application...")
    os.chdir(PROJECT_ROOT / "frontend")
    os.execv(sys.executable, [sys.executable, "-m", "streamlit", "run", "app.py", "--server.port=8501"])

def main():
    parser = argparse.ArgumentParser(description="Local Development Setup")
    parser.add_argument("--ollama", action="store_true", help="Force use Ollama")
    parser.add_argument("--tensorrt", action="store_true", help="Force use TensorRT")
    parser.add_argument("--setup", action="store_true", help="Install dependencies only")
    args = parser.parse_args()
    
    print("🚀 Agentic AI - Local Development Setup")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    if args.setup:
        print("✅ Setup complete!")
        return
    
    # Determine provider
    if args.tensorrt:
        if not check_service("http://localhost:8000/v2/health"):
            print("❌ TensorRT server not available at localhost:8000")
            sys.exit(1)
        provider, model = "tensorrt", "mistral-7b-instruct-v0.1"
    elif args.ollama:
        if not check_service("http://localhost:11434"):
            if not start_ollama():
                sys.exit(1)
        provider, model = "ollama", "mistral:7b"
    else:
        provider, model = detect_provider()
        if not provider:
            sys.exit(1)
    
    # Setup for Ollama
    if provider == "ollama":
        if not ensure_ollama_model(model):
            print("💡 Trying smaller model...")
            if not ensure_ollama_model("llama3.2:1b"):
                sys.exit(1)
            model = "llama3.2:1b"
    
    # Update configuration
    setup_config(provider, model)
    
    print("\n🎉 Setup complete!")
    print(f"   Provider: {provider}")
    print(f"   Model: {model}")
    print("\n🌐 Starting application at: http://localhost:8501")
    print("   Press Ctrl+C to stop")
    print("=" * 50)
    
    # Start Streamlit
    start_streamlit()

if __name__ == "__main__":
    main()
