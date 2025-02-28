"""
High-level wrapper functions for LLM interaction.

This module provides simple non-async wrapper functions around the
LLM clients to make them easier to use in synchronous code.
"""

import os
import asyncio
from typing import Dict, Any, List, Optional

from .client import LLMClientFactory, LLMClient


def get_llm_client(provider: str = "claude", **kwargs) -> "SyncLLMClient":
    """
    Get a synchronous client for the specified LLM provider.
    
    Args:
        provider: Name of the LLM provider ('claude' or 'ollama')
        **kwargs: Additional parameters for the LLM client
        
    Returns:
        A synchronous wrapper around the LLM client
    """
    # Get the async client
    async_client = LLMClientFactory.create(provider, **kwargs)
    
    # Wrap it in the synchronous wrapper
    return SyncLLMClient(async_client)


class SyncLLMClient:
    """
    Synchronous wrapper around the asynchronous LLM client.
    
    This class provides synchronous methods that internally use
    the asyncio event loop to call the async methods of the wrapped client.
    """
    
    def __init__(self, async_client: LLMClient):
        """
        Initialize the synchronous wrapper.
        
        Args:
            async_client: The asynchronous LLM client to wrap
        """
        self.async_client = async_client
    
    def generate(self, prompt: str, context: Optional[List[Dict[str, Any]]] = None, **kwargs) -> str:
        """
        Generate a response from the language model synchronously.
        
        Args:
            prompt: Prompt to send to the language model
            context: Optional list of contextual information to include
            **kwargs: Additional parameters for the language model
            
        Returns:
            Response from the language model
        """
        return asyncio.run(self.async_client.generate(prompt, context, **kwargs))
    
    def embeddings(self, text: str) -> Dict[str, Any]:
        """
        Get embeddings for a text from the language model synchronously.
        
        Args:
            text: Text to get embeddings for
            
        Returns:
            Embeddings for the text
        """
        return asyncio.run(self.async_client.embeddings(text))
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate a chat completion from the language model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            
        Returns:
            Response from the language model
        """
        # Extract the system message if present
        system_prompt = None
        chat_messages = []
        
        for message in messages:
            if message.get("role") == "system":
                system_prompt = message.get("content")
            else:
                chat_messages.append(message)
        
        # If there are no messages left, return an empty string
        if not chat_messages:
            return ""
        
        # Extract the last user message as the prompt
        last_user_message = None
        context_messages = []
        
        for message in chat_messages:
            if message.get("role") == "user":
                last_user_message = message.get("content")
                # Don't add the last user message to context
            else:
                context_messages.append(message)
        
        # If there's no user message, use an empty string
        if last_user_message is None:
            last_user_message = ""
        
        # Generate the response
        return self.generate(
            prompt=last_user_message,
            context=context_messages,
            system_prompt=system_prompt
        ) 