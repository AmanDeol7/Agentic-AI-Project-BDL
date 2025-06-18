#!/usr/bin/env python3
"""
Auto-configuration module for the Agentic AI Project.
Automatically detects available services and configures the optimal setup.
"""

import os
import sys
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ollama_availability() -> bool:
    """Check if Ollama is running and available."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model["name"] for model in data.get("models", [])]
            logger.info(f"Ollama is running with models: {models}")
            return True
        else:
            logger.warning("Ollama API responded with error")
            return False
    except Exception as e:
        logger.warning(f"Ollama not available: {e}")
        return False

def check_tensorrt_availability() -> bool:
    """Check if TensorRT-LLM server is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            logger.info("TensorRT-LLM server is running")
            return True
        else:
            logger.warning("TensorRT-LLM server responded with error")
            return False
    except Exception as e:
        logger.warning(f"TensorRT-LLM not available: {e}")
        return False

def get_available_ollama_models() -> list:
    """Get list of available Ollama models."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        return []
    except Exception:
        return []

def auto_configure() -> Optional[str]:
    """
    Automatically configure the best available service.
    
    Returns:
        str: Service type ('ollama', 'tensorrt', or None)
    """
    logger.info("Auto-detecting available services...")
    
    # Check Ollama first (more reliable for local development)
    if check_ollama_availability():
        models = get_available_ollama_models()
        if models:
            logger.info(f"Using Ollama with models: {models}")
            return "ollama"
        else:
            logger.warning("Ollama running but no models available")
    
    # Check TensorRT-LLM as fallback
    if check_tensorrt_availability():
        logger.info("Using TensorRT-LLM server")
        return "tensorrt"
    
    # No services available
    logger.error("No LLM services available. Please start Ollama or TensorRT-LLM server.")
    return None

def update_config(service_type: str) -> bool:
    """
    Update application configuration based on detected service.
    
    Args:
        service_type: Type of service to configure ('ollama' or 'tensorrt')
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Import config
        from config.app_config import update_config_for_local
        
        if service_type == "ollama":
            # Configure for Ollama
            models = get_available_ollama_models()
            preferred_model = None
            
            # Choose best available model
            model_priority = ["mistral:7b", "llama3.2:1b", "codellama:7b"]
            for model in model_priority:
                if model in models:
                    preferred_model = model
                    break
            
            if not preferred_model and models:
                preferred_model = models[0]  # Use first available model
            
            if preferred_model:
                # Update global config
                update_config_for_local()
                logger.info(f"Configured for Ollama with model: {preferred_model}")
                return True
            else:
                logger.error("No suitable Ollama models found")
                return False
                
        elif service_type == "tensorrt":
            logger.info("Configured for TensorRT-LLM")
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Failed to update config: {e}")
        return False

def setup_environment_variables():
    """Set up environment variables for optimal performance."""
    # Disable tokenizer parallelism to avoid warnings
    os.environ.setdefault('TOKENIZERS_PARALLELISM', 'false')
    
    # Set Streamlit configuration
    os.environ.setdefault('STREAMLIT_SERVER_HEADLESS', 'true')
    os.environ.setdefault('STREAMLIT_SERVER_WATCH_DIRS', 'false')
    os.environ.setdefault('STREAMLIT_SERVER_ENABLE_STATIC_SERVING', 'true')
    
    logger.info("Environment variables configured")

def verify_setup() -> Dict[str, Any]:
    """
    Verify the current setup and return status information.
    
    Returns:
        Dict containing setup status
    """
    status = {
        "ollama_available": check_ollama_availability(),
        "tensorrt_available": check_tensorrt_availability(),
        "ollama_models": get_available_ollama_models(),
        "recommended_service": None,
        "issues": []
    }
    
    if status["ollama_available"] and status["ollama_models"]:
        status["recommended_service"] = "ollama"
    elif status["tensorrt_available"]:
        status["recommended_service"] = "tensorrt"
    else:
        status["issues"].append("No LLM services available")
    
    return status

def main():
    """Main function for standalone execution."""
    print("Agentic AI Auto-Configuration")
    print("=" * 40)
    
    # Setup environment
    setup_environment_variables()
    
    # Auto-configure
    service_type = auto_configure()
    
    if service_type:
        success = update_config(service_type)
        if success:
            print(f"Successfully configured for {service_type}")
        else:
            print(f"Failed to configure for {service_type}")
            sys.exit(1)
    else:
        print("Auto-configuration failed")
        print("\nTo fix this issue:")
        print("1. Start Ollama: ollama serve")
        print("2. Pull a model: ollama pull mistral:7b")
        print("3. Or start TensorRT-LLM server on port 8000")
        sys.exit(1)
    
    # Verify setup
    status = verify_setup()
    print(f"\nSetup Status:")
    print(f"   Ollama: {'Available' if status['ollama_available'] else 'Not Available'}")
    print(f"   TensorRT: {'Available' if status['tensorrt_available'] else 'Not Available'}")
    print(f"   Models: {status['ollama_models']}")
    print(f"   Service: {status['recommended_service']}")
    
    if status["issues"]:
        print(f"   Issues: {', '.join(status['issues'])}")

if __name__ == "__main__":
    main()
