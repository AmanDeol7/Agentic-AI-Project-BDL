"""
Configuration settings for the agentic code assistant.
"""
from pathlib import Path

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent

# LLM Configuration
LLM_CONFIG = {
    "provider": "ollama",
    "model": "mistral",  # Default model through Ollama
    "temperature": 0.7,
    "max_tokens": 2000
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

# Application paths
PATHS = {
    "uploads": BASE_DIR / "data" / "uploads",
}

# Ensure necessary directories exist
for path in PATHS.values():
    path.mkdir(parents=True, exist_ok=True)