"""
Ollama integration for LLM functionality.
"""
from typing import List, Dict, Any, Optional
from langchain_ollama.llms import OllamaLLM

class OllamaProvider:
    """
    Provider for Ollama-based LLM services.
    """
    
    def __init__(
        self, 
        model_name: str = "mistral:7b", 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        base_url: str = None
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            base_url: Base URL for Ollama server (defaults to environment variable or localhost)
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # Use environment variable for Ollama base URL if available
        import os
        if base_url is None:
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=model_name,
            temperature=temperature, #increasing will make it more creative
            num_predict=max_tokens,
            base_url=base_url
        )
    
    def generate(self, prompt: str) -> str:
        """
        Generate text based on a prompt.
        
        Args:
            prompt: The input prompt
            
        Returns:
            Generated text
        """
        return self.llm.invoke(prompt)
    
    def batch_generate(self, prompts: List[str]) -> List[str]:
        """
        Generate responses for multiple prompts.
        
        Args:
            prompts: List of input prompts
            
        Returns:
            List of generated responses
        """
        return self.llm.batch(prompts)
    
    def is_available(self) -> bool:
        """
        Check if the Ollama provider is available.
        
        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            # Try a simple model call to check availability
            test_response = self.llm.invoke("test")
            return True
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "provider": "ollama"
        }