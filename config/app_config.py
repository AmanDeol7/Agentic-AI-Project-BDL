"""
Configuration settings for the agentic code assistant.
"""
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# LLM Configuration
LLM_CONFIG = {
    "provider": "tensorrt",  # Use TensorRT since server is available
    "model": "mistral",  # Default model through Ollama (fallback)
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