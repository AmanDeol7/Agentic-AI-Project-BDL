"""
TensorRT-LLM integration for high-performance inference.
"""
from typing import List, Dict, Any, Optional
import json
import requests
import logging

logger = logging.getLogger(__name__)

class TensorRTProvider:
    """
    Provider for TensorRT-LLM based inference.
    Simple HTTP API integration for TensorRT-LLM server.
    """
    
    def __init__(
        self, 
        server_url: str = "http://localhost:8000",
        model_name: str = "llama2",
        temperature: float = 0.7,
        max_tokens: int = 512,
        timeout: int = 30
    ):
        """
        Initialize the TensorRT-LLM provider.
        
        Args:
            server_url: URL of the TensorRT-LLM server
            model_name: Name of the model to use
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
        """
        self.server_url = server_url.rstrip('/')
        self.model_name = model_name
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_seq_len = None  # Will be fetched from server
        
        # Health check and get server info
        try:
            server_info = self._health_check()
            if server_info:
                self.max_seq_len = server_info.get("max_seq_len", 4096)
            logger.info(f"TensorRT-LLM provider initialized: {server_url}, max_seq_len: {self.max_seq_len}")
        except Exception as e:
            logger.warning(f"TensorRT-LLM server not available: {e}")
            self.max_seq_len = 4096  # Default fallback
    
    def _health_check(self) -> Dict[str, Any]:
        """Check if TensorRT-LLM server is running and get server info."""
        try:
            # First try the health endpoint
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                # Some servers return empty health responses, try to get models instead
                try:
                    models_response = requests.get(f"{self.server_url}/v1/models", timeout=5)
                    if models_response.status_code == 200:
                        models_data = models_response.json()
                        # Return server info based on available models
                        return {
                            "status": "healthy",
                            "max_seq_len": 4096,  # Default value
                            "models": models_data.get("data", [])
                        }
                except:
                    pass
                
                # Try to parse health response as JSON, fallback to default if empty
                try:
                    return response.json()
                except:
                    return {"status": "healthy", "max_seq_len": 4096}
            else:
                return {}
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return {}
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text using TensorRT-LLM.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        try:
            # Calculate token limits based on server configuration
            max_tokens = kwargs.get("max_tokens", self.max_tokens)
            
            # Estimate prompt length (rough approximation: 1 token ≈ 4 chars)
            estimated_prompt_tokens = len(prompt) // 4
            
            # Ensure we don't exceed max_seq_len
            if self.max_seq_len:
                available_tokens = self.max_seq_len - estimated_prompt_tokens - 50  # Buffer
                max_tokens = min(max_tokens, available_tokens)
                
                if max_tokens <= 0:
                    logger.warning(f"Prompt too long ({estimated_prompt_tokens} tokens), truncating...")
                    # Truncate prompt to fit
                    max_prompt_chars = (self.max_seq_len - self.max_tokens - 50) * 4
                    prompt = prompt[:max_prompt_chars] + "..."
                    max_tokens = self.max_tokens
            
            # Prepare request payload
            payload = {
                "prompt": prompt,
                "model": self.model_name,
                "temperature": kwargs.get("temperature", self.temperature),
                "max_tokens": max_tokens,
                "stop": kwargs.get("stop", None),
                "stream": False
            }
            
            # Make request to TensorRT-LLM server
            response = requests.post(
                f"{self.server_url}/v1/completions",
                json=payload,
                timeout=self.timeout,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("choices", [{}])[0].get("text", "").strip()
            else:
                logger.error(f"TensorRT-LLM API error: {response.status_code} - {response.text}")
                return self._fallback_generation(prompt)
                
        except Exception as e:
            logger.error(f"TensorRT-LLM generation error: {e}")
            return self._fallback_generation(prompt)
    
    def _fallback_generation(self, prompt: str) -> str:
        """
        Fallback when TensorRT-LLM is unavailable.
        Uses Ollama as fallback provider.
        """
        try:
            # Try to use Ollama as fallback
            from .ollama_provider import OllamaProvider
            ollama = OllamaProvider(model_name="mistral:7b")
            return ollama.generate(prompt)
        except Exception as e:
            logger.error(f"Ollama fallback failed: {e}")
            # Final fallback to simple response
            if "summarize" in prompt.lower():
                return "I apologize, but I cannot summarize the document as both TensorRT-LLM and Ollama services are currently unavailable. Please check the server connection."
            elif "extract" in prompt.lower():
                return "I apologize, but I cannot extract information as both TensorRT-LLM and Ollama services are currently unavailable. Please check the server connection."
            else:
                return "I apologize, but I cannot process your request as both TensorRT-LLM and Ollama services are currently unavailable. Please check the server connection and try again."
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[str]:
        """
        Generate text for multiple prompts.
        
        Args:
            prompts: List of input prompts
            **kwargs: Additional generation parameters
            
        Returns:
            List of generated texts
        """
        return [self.generate(prompt, **kwargs) for prompt in prompts]
    
    def is_available(self) -> bool:
        """Check if the provider is available."""
        health_info = self._health_check()
        return bool(health_info)
