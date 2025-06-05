"""
Configuration settings for the agentic code assistant.
"""
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# LLM Configuration
LLM_CONFIG = {
    "provider": "ollama",  # Use Ollama for local development
    "model": "mistral:7b",  # Mistral 7B model for better performance
    "temperature": 0.7,
    "max_tokens": 1000  # Reduced to prevent memory issues
}

# TensorRT-LLM Configuration
TENSORRT_CONFIG = {
    "server_url": "http://localhost:8000",
    "model_name": "TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # TensorRT-LLM model
    "timeout": 30,
    "enable_fallback": True  # Fall back to Ollama if TensorRT-LLM unavailable
}

# Agent Configuration
AGENT_CONFIG = {
    "code_agent": {
        "name": "Code Assistant",
        "description": "Specialized in code generation and analysis",
        "model": LLM_CONFIG["model"],
    },
    "doc_agent": {
        "name": "Document Assistant",
        "description": "Specialized in document parsing and analysis",
        "model": LLM_CONFIG["model"],
    }
}

# Database Configuration
DATABASE_URL = f"sqlite:///{BASE_DIR}/data/app.db"

# Application paths
PATHS = {
    "uploads": BASE_DIR / "data" / "uploads",
    "data": BASE_DIR / "data",
}

# Ensure necessary directories exist
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)

def update_config_for_local():
    """
    Update configuration for local development with Ollama.
    This function modifies the global LLM_CONFIG to use Ollama instead of TensorRT.
    """
    global LLM_CONFIG
    
    # Check if Ollama is running
    import requests
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            # Ollama is running, configure for it
            LLM_CONFIG = {
                "provider": "ollama",
                "model": "mistral:7b",  # Default model
                "base_url": "http://localhost:11434",
                "temperature": 0.7,
                "max_tokens": 1500,
                "stream": False
            }
            print("✅ Configuration updated to use Ollama")
            return True
        else:
            print("⚠️  Ollama API not responding")
            return False
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        return False

def get_available_models():
    """
    Get list of available models from Ollama.
    Returns list of model names or empty list if Ollama not available.
    """
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return [model["name"] for model in data.get("models", [])]
        return []
    except Exception:
        return []

def auto_select_best_model():
    """
    Automatically select the best available model for the current system.
    Prioritizes models based on size and capability.
    """
    available_models = get_available_models()
    
    if not available_models:
        return None
    
    # Model preference order (best to fastest)
    model_priority = [
        "mistral:7b",
        "llama3.2:3b", 
        "llama3.2:1b",
        "phi3:mini",
        "gemma2:2b"
    ]
    
    # Find the best available model
    for preferred_model in model_priority:
        if preferred_model in available_models:
            return preferred_model
    
    # If none of the preferred models are available, return the first one
    return available_models[0] if available_models else None