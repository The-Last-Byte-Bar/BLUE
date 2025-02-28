"""
LLM client module.

This module provides clients for accessing language models
for natural language processing and generation, with support
for both cloud-based (Claude) and local (Ollama) models.
"""

from typing import Dict, Any, Optional, List, Union
import logging
import os
import json
import aiohttp
import asyncio
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class LLMClient(ABC):
    """Abstract base client for accessing language models."""
    
    @abstractmethod
    async def generate(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """
        Generate a response from the language model.
        
        Args:
            prompt: Prompt to send to the language model
            context: Optional list of contextual information to include
            **kwargs: Additional parameters for the language model
            
        Returns:
            Response from the language model
        """
        pass
    
    @abstractmethod
    async def embeddings(self, text: str) -> Dict[str, Any]:
        """
        Get embeddings for a text from the language model.
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            Embeddings for the text
        """
        pass


class ClaudeClient(LLMClient):
    """Client for accessing Anthropic's Claude models."""
    
    def __init__(self, 
                 model_name: str = "claude-3-sonnet-20240229", 
                 api_key: Optional[str] = None,
                 max_tokens: int = 4096):
        """
        Initialize the Claude client.
        
        Args:
            model_name: Name of the Claude model to use
            api_key: API key for accessing Anthropic's API
            max_tokens: Maximum number of tokens to generate
        """
        self.model_name = model_name
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for Claude client")
        
        self.base_url = "https://api.anthropic.com/v1"
        self.max_tokens = max_tokens
        
    async def generate(self, 
                       prompt: str, 
                       context: Optional[List[Dict[str, Any]]] = None, 
                       system_prompt: Optional[str] = None,
                       **kwargs) -> str:
        """
        Generate a response from Claude.
        
        Args:
            prompt: Prompt to send to Claude
            context: Optional list of contextual information to include
            system_prompt: Optional system prompt to guide Claude's behavior
            **kwargs: Additional parameters for the API call
            
        Returns:
            Response from Claude
        """
        if not self.api_key:
            raise ValueError("API key is required for Claude client")
        
        # Format the messages for Claude
        messages = []
        
        # Add context as assistant or user messages if provided
        if context:
            for item in context:
                role = item.get("role", "user")
                content = item.get("content", "")
                messages.append({"role": role, "content": content})
        
        # Add the current prompt as a user message
        messages.append({"role": "user", "content": prompt})
        
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
            
        # Add any additional parameters
        payload.update(kwargs)
        
        async with aiohttp.ClientSession() as session:
            headers = {
                "Content-Type": "application/json",
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01"
            }
            
            try:
                async with session.post(
                    f"{self.base_url}/messages",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Claude API error: {response.status} - {error_text}")
                        return f"Error: {response.status} - Unable to generate response"
                    
                    result = await response.json()
                    return result["content"][0]["text"]
                    
            except Exception as e:
                logger.error(f"Error calling Claude API: {str(e)}")
                return f"Error: {str(e)}"
    
    async def embeddings(self, text: str) -> Dict[str, Any]:
        """
        Get embeddings from Claude.
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            Embeddings for the text
        """
        logger.warning("Embeddings not yet supported by Claude API")
        return {
            "embeddings": [],
            "dimensions": 0,
            "error": "Embeddings not yet supported by Claude API"
        }


class OllamaClient(LLMClient):
    """Client for accessing local Ollama models."""
    
    def __init__(self, 
                 model_name: str = "llama3", 
                 api_url: Optional[str] = None,
                 max_tokens: int = 4096):
        """
        Initialize the Ollama client.
        
        Args:
            model_name: Name of the Ollama model to use
            api_url: URL for accessing the Ollama API
            max_tokens: Maximum number of tokens to generate
        """
        self.model_name = model_name
        self.api_url = api_url or os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
        self.max_tokens = max_tokens
        
    async def generate(self, 
                       prompt: str, 
                       context: Optional[List[Dict[str, Any]]] = None,
                       system_prompt: Optional[str] = None,
                       **kwargs) -> str:
        """
        Generate a response from Ollama.
        
        Args:
            prompt: Prompt to send to Ollama
            context: Optional list of contextual information to include
            system_prompt: Optional system prompt to guide model's behavior
            **kwargs: Additional parameters for the API call
            
        Returns:
            Response from Ollama
        """
        # Format the full prompt including context
        full_prompt = ""
        
        # Add context if provided
        if context:
            for item in context:
                role = item.get("role", "user")
                content = item.get("content", "")
                if role == "user":
                    full_prompt += f"User: {content}\n\n"
                elif role == "assistant":
                    full_prompt += f"Assistant: {content}\n\n"
                else:
                    full_prompt += f"{content}\n\n"
        
        # Add the current prompt
        full_prompt += f"User: {prompt}\n\nAssistant:"
        
        # Prepare the request payload
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False
        }
        
        # Add system prompt if provided
        if system_prompt:
            payload["system"] = system_prompt
            
        # Add max tokens
        if self.max_tokens:
            payload["max_tokens"] = self.max_tokens
            
        # Add any additional parameters
        for key, value in kwargs.items():
            payload[key] = value
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/generate",
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return f"Error: {response.status} - Unable to generate response"
                    
                    result = await response.json()
                    return result.get("response", "No response generated")
                    
            except Exception as e:
                logger.error(f"Error calling Ollama API: {str(e)}")
                return f"Error: {str(e)}"
    
    async def embeddings(self, text: str) -> Dict[str, Any]:
        """
        Get embeddings from Ollama.
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            Embeddings for the text
        """
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    f"{self.api_url}/api/embeddings",
                    json={"model": self.model_name, "prompt": text}
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        logger.error(f"Ollama API error: {response.status} - {error_text}")
                        return {
                            "embeddings": [],
                            "dimensions": 0,
                            "error": f"Error: {response.status} - {error_text}"
                        }
                    
                    result = await response.json()
                    return {
                        "embeddings": result.get("embedding", []),
                        "dimensions": len(result.get("embedding", []))
                    }
                    
            except Exception as e:
                logger.error(f"Error calling Ollama API for embeddings: {str(e)}")
                return {
                    "embeddings": [],
                    "dimensions": 0,
                    "error": str(e)
                }


class LLMClientFactory:
    """Factory for creating LLM clients."""
    
    @staticmethod
    def create(provider: str = "claude", **kwargs) -> LLMClient:
        """
        Create an LLM client.
        
        Args:
            provider: Name of the LLM provider ('claude' or 'ollama')
            **kwargs: Additional parameters for the LLM client
            
        Returns:
            An instance of LLMClient
        """
        if provider.lower() == "claude":
            return ClaudeClient(**kwargs)
        elif provider.lower() == "ollama":
            return OllamaClient(**kwargs)
        else:
            raise ValueError(f"Unsupported LLM provider: {provider}") 