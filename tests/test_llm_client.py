"""
Unit tests for LLM client classes.

This module contains tests for the various LLM client implementations.
"""

import pytest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock
import aiohttp

from llm.client import LLMClient, ClaudeClient, OllamaClient, LLMClientFactory


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-api-key")
    monkeypatch.setenv("OLLAMA_API_URL", "http://mock-ollama:11434")


@pytest.fixture
def mock_aiohttp_response():
    """Create a mock aiohttp response object."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    async def mock_json():
        return {
            "content": [{"text": "This is a mock LLM response"}]
        }
    
    mock_response.json = mock_json
    
    # Mock the context manager behavior
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_response
    
    return mock_cm


@pytest.fixture
def mock_ollama_response():
    """Create a mock Ollama response object."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    async def mock_json():
        return {
            "response": "This is a mock Ollama response"
        }
    
    mock_response.json = mock_json
    
    # Mock the context manager behavior
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_response
    
    return mock_cm


@pytest.fixture
def mock_embeddings_response():
    """Create a mock embeddings response object."""
    mock_response = AsyncMock()
    mock_response.status = 200
    
    async def mock_json():
        return {
            "embedding": [0.1, 0.2, 0.3, 0.4, 0.5]
        }
    
    mock_response.json = mock_json
    
    # Mock the context manager behavior
    mock_cm = AsyncMock()
    mock_cm.__aenter__.return_value = mock_response
    
    return mock_cm


class TestLLMClientFactory:
    """Tests for the LLMClientFactory class."""
    
    def test_create_claude_client(self, mock_env_vars):
        """Test creating a Claude client."""
        client = LLMClientFactory.create("claude")
        assert isinstance(client, ClaudeClient)
        assert client.model_name == "claude-3-sonnet-20240229"
        assert client.api_key == "mock-api-key"
    
    def test_create_ollama_client(self, mock_env_vars):
        """Test creating an Ollama client."""
        client = LLMClientFactory.create("ollama")
        assert isinstance(client, OllamaClient)
        assert client.model_name == "llama3"
        assert client.api_url == "http://mock-ollama:11434"
    
    def test_create_with_custom_params(self, mock_env_vars):
        """Test creating a client with custom parameters."""
        client = LLMClientFactory.create("claude", model_name="claude-custom", max_tokens=1000)
        assert isinstance(client, ClaudeClient)
        assert client.model_name == "claude-custom"
        assert client.max_tokens == 1000
    
    def test_create_unsupported_provider(self):
        """Test creating a client with an unsupported provider."""
        with pytest.raises(ValueError, match="Unsupported LLM provider: not-a-provider"):
            LLMClientFactory.create("not-a-provider")


class TestClaudeClient:
    """Tests for the ClaudeClient class."""
    
    def test_init(self, mock_env_vars):
        """Test initializing a Claude client."""
        client = ClaudeClient()
        assert client.model_name == "claude-3-sonnet-20240229"
        assert client.api_key == "mock-api-key"
        assert client.max_tokens == 4096
    
    def test_init_with_params(self):
        """Test initializing a Claude client with custom parameters."""
        client = ClaudeClient(
            model_name="claude-custom",
            api_key="custom-key",
            max_tokens=1000
        )
        assert client.model_name == "claude-custom"
        assert client.api_key == "custom-key"
        assert client.max_tokens == 1000
    
    def test_init_no_api_key(self, monkeypatch):
        """Test initializing a Claude client with no API key."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        with pytest.raises(ValueError, match="API key is required for Claude client"):
            ClaudeClient(api_key=None)
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_aiohttp_response, mock_env_vars):
        """Test generating a response from Claude."""
        with patch("aiohttp.ClientSession.post", return_value=mock_aiohttp_response) as mock_post:
            client = ClaudeClient()
            response = await client.generate("What is a blockchain?")
            
            # Check the response
            assert response == "This is a mock LLM response"
            
            # Check that the post method was called correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "https://api.anthropic.com/v1/messages"
            assert kwargs["headers"]["x-api-key"] == "mock-api-key"
            assert kwargs["json"]["model"] == "claude-3-sonnet-20240229"
            assert kwargs["json"]["messages"][0]["role"] == "user"
            assert kwargs["json"]["messages"][0]["content"] == "What is a blockchain?"
    
    @pytest.mark.asyncio
    async def test_generate_with_context(self, mock_aiohttp_response, mock_env_vars):
        """Test generating a response from Claude with context."""
        with patch("aiohttp.ClientSession.post", return_value=mock_aiohttp_response) as mock_post:
            client = ClaudeClient()
            context = [
                {"role": "system", "content": "You are a blockchain expert."},
                {"role": "user", "content": "Tell me about Ergo."},
                {"role": "assistant", "content": "Ergo is a blockchain platform."}
            ]
            response = await client.generate(
                "What consensus algorithm does it use?",
                context=context
            )
            
            # Check the response
            assert response == "This is a mock LLM response"
            
            # Check that the context was included in the request
            args, kwargs = mock_post.call_args
            assert len(kwargs["json"]["messages"]) == 4
            assert kwargs["json"]["messages"][0]["role"] == "system"
            assert kwargs["json"]["messages"][0]["content"] == "You are a blockchain expert."
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_aiohttp_response, mock_env_vars):
        """Test generating a response from Claude with a system prompt."""
        with patch("aiohttp.ClientSession.post", return_value=mock_aiohttp_response) as mock_post:
            client = ClaudeClient()
            response = await client.generate(
                "What is a blockchain?",
                system_prompt="You are a helpful blockchain expert."
            )
            
            # Check the response
            assert response == "This is a mock LLM response"
            
            # Check that the system prompt was included in the request
            args, kwargs = mock_post.call_args
            assert kwargs["json"]["system"] == "You are a helpful blockchain expert."
    
    @pytest.mark.asyncio
    async def test_generate_api_error(self, mock_env_vars):
        """Test handling API errors in the generate method."""
        # Create a proper mock for the error response
        mock_error_response = AsyncMock()
        mock_error_response.status = 400
        
        async def mock_text():
            return '{"error": "Invalid request"}'
        
        mock_error_response.text = mock_text
        
        # Create a context manager mock
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_error_response
        
        with patch("aiohttp.ClientSession.post", return_value=mock_cm):
            client = ClaudeClient()
            response = await client.generate("What is a blockchain?")
            
            # Check that the error was handled correctly
            assert "Error: 400" in response
    
    @pytest.mark.asyncio
    async def test_embeddings_not_supported(self, mock_env_vars):
        """Test that embeddings are not yet supported by Claude."""
        client = ClaudeClient()
        result = await client.embeddings("Test text")
        
        # Check that the correct error message was returned
        assert result["error"] == "Embeddings not yet supported by Claude API"
        assert result["embeddings"] == []
        assert result["dimensions"] == 0


class TestOllamaClient:
    """Tests for the OllamaClient class."""
    
    def test_init(self, mock_env_vars):
        """Test initializing an Ollama client."""
        client = OllamaClient()
        assert client.model_name == "llama3"
        assert client.api_url == "http://mock-ollama:11434"
        assert client.max_tokens == 4096
    
    def test_init_with_params(self):
        """Test initializing an Ollama client with custom parameters."""
        client = OllamaClient(
            model_name="mistral",
            api_url="http://custom-ollama:11434",
            max_tokens=1000
        )
        assert client.model_name == "mistral"
        assert client.api_url == "http://custom-ollama:11434"
        assert client.max_tokens == 1000
    
    @pytest.mark.asyncio
    async def test_generate(self, mock_ollama_response, mock_env_vars):
        """Test generating a response from Ollama."""
        with patch("aiohttp.ClientSession.post", return_value=mock_ollama_response) as mock_post:
            client = OllamaClient()
            response = await client.generate("What is a blockchain?")
            
            # Check the response
            assert response == "This is a mock Ollama response"
            
            # Check that the post method was called correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "http://mock-ollama:11434/api/generate"
            assert kwargs["json"]["model"] == "llama3"
            assert "What is a blockchain?" in kwargs["json"]["prompt"]
    
    @pytest.mark.asyncio
    async def test_generate_with_context(self, mock_ollama_response, mock_env_vars):
        """Test generating a response from Ollama with context."""
        with patch("aiohttp.ClientSession.post", return_value=mock_ollama_response) as mock_post:
            client = OllamaClient()
            context = [
                {"role": "user", "content": "Tell me about Ergo."},
                {"role": "assistant", "content": "Ergo is a blockchain platform."}
            ]
            response = await client.generate(
                "What consensus algorithm does it use?",
                context=context
            )
            
            # Check the response
            assert response == "This is a mock Ollama response"
            
            # Check that the context was included in the prompt
            args, kwargs = mock_post.call_args
            assert "Tell me about Ergo." in kwargs["json"]["prompt"]
            assert "Ergo is a blockchain platform." in kwargs["json"]["prompt"]
            assert "What consensus algorithm does it use?" in kwargs["json"]["prompt"]
    
    @pytest.mark.asyncio
    async def test_generate_with_system_prompt(self, mock_ollama_response, mock_env_vars):
        """Test generating a response from Ollama with a system prompt."""
        with patch("aiohttp.ClientSession.post", return_value=mock_ollama_response) as mock_post:
            client = OllamaClient()
            response = await client.generate(
                "What is a blockchain?",
                system_prompt="You are a helpful blockchain expert."
            )
            
            # Check the response
            assert response == "This is a mock Ollama response"
            
            # Check that the system prompt was included in the request
            args, kwargs = mock_post.call_args
            assert kwargs["json"]["system"] == "You are a helpful blockchain expert."
    
    @pytest.mark.asyncio
    async def test_generate_api_error(self, mock_env_vars):
        """Test handling API errors in the generate method."""
        # Create a proper mock for the error response
        mock_error_response = AsyncMock()
        mock_error_response.status = 400
        
        async def mock_text():
            return '{"error": "Invalid request"}'
        
        mock_error_response.text = mock_text
        
        # Create a context manager mock
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_error_response
        
        with patch("aiohttp.ClientSession.post", return_value=mock_cm):
            client = OllamaClient()
            response = await client.generate("What is a blockchain?")
            
            # Check that the error was handled correctly
            assert "Error: 400" in response
    
    @pytest.mark.asyncio
    async def test_embeddings(self, mock_embeddings_response, mock_env_vars):
        """Test getting embeddings from Ollama."""
        with patch("aiohttp.ClientSession.post", return_value=mock_embeddings_response) as mock_post:
            client = OllamaClient()
            result = await client.embeddings("Test text")
            
            # Check the response
            assert result["embeddings"] == [0.1, 0.2, 0.3, 0.4, 0.5]
            assert result["dimensions"] == 5
            
            # Check that the post method was called correctly
            mock_post.assert_called_once()
            args, kwargs = mock_post.call_args
            assert args[0] == "http://mock-ollama:11434/api/embeddings"
            assert kwargs["json"]["model"] == "llama3"
            assert kwargs["json"]["prompt"] == "Test text"
    
    @pytest.mark.asyncio
    async def test_embeddings_api_error(self, mock_env_vars):
        """Test handling API errors in the embeddings method."""
        # Create a proper mock for the error response
        mock_error_response = AsyncMock()
        mock_error_response.status = 400
        
        async def mock_text():
            return '{"error": "Invalid request"}'
        
        mock_error_response.text = mock_text
        
        # Create a context manager mock
        mock_cm = AsyncMock()
        mock_cm.__aenter__.return_value = mock_error_response
        
        with patch("aiohttp.ClientSession.post", return_value=mock_cm):
            client = OllamaClient()
            result = await client.embeddings("Test text")
            
            # Check that the error was handled correctly
            assert "Error: 400" in result["error"]
            assert result["embeddings"] == []
            assert result["dimensions"] == 0 