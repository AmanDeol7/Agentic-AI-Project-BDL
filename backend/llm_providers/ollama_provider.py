"""
Ollama integration for LLM functionality.
"""
from typing import List, Dict, Any, Optional
from langchain_ollama.llms import OllamaLLM
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

class OllamaProvider:
    """
    Provider for Ollama-based LLM services.
    """
    
    def __init__(
        self, 
        model_name: str = "mistral", 
        temperature: float = 0.7,
        max_tokens: int = 2000,
        streaming: bool = True
    ):
        """
        Initialize the Ollama provider.
        
        Args:
            model_name: Name of the model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            streaming: Whether to stream responses
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.streaming = streaming
        
        # Set up callback manager for streaming
        callback_manager = CallbackManager([StreamingStdOutCallbackHandler()]) if streaming else None
        
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model=model_name,
            temperature=temperature, #increasing will make it more creative
            num_predict=max_tokens,
            callback_manager=callback_manager
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