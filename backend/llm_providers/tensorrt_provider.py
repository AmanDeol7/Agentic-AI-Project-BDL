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
        max_tokens: int = 2000,
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
            response = requests.get(f"{self.server_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
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
        Uses a simple rule-based response.
        """
        if "summarize" in prompt.lower():
            return "I apologize, but I cannot summarize the document as the TensorRT-LLM service is currently unavailable. Please check the server connection."
        elif "extract" in prompt.lower():
            return "I apologize, but I cannot extract information as the TensorRT-LLM service is currently unavailable. Please check the server connection."
        else:
            return "I apologize, but I cannot process your request as the TensorRT-LLM service is currently unavailable. Please check the server connection and try again."
    
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
