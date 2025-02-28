"""
Unit tests for the BlockchainAnalyzer class.

This module contains tests for the BlockchainAnalyzer class used for analyzing
blockchain data with language models.
"""

import pytest
import json
import os
from unittest.mock import patch, AsyncMock, MagicMock

from llm.analysis import BlockchainAnalyzer, ContextBuilder
from llm.client import LLMClient, ClaudeClient


@pytest.fixture
def mock_llm_client():
    """Set up a mock LLM client for testing."""
    mock_client = MagicMock(spec=LLMClient)
    
    async def mock_generate(prompt, context=None, system_prompt=None, **kwargs):
        # Check both prompt param and kwargs["prompt"] since both are used in different contexts
        prompt_text = kwargs.get("prompt", "") if isinstance(kwargs.get("prompt"), str) else ""
        if not prompt_text and isinstance(prompt, str):
            prompt_text = prompt
            
        if "forensic" in prompt_text.lower():
            return "Mock forensic analysis response"
        elif "wallet" in prompt_text.lower():
            return "Mock wallet analysis response"
        elif "transaction" in prompt_text.lower():
            return "Mock transaction analysis response"
        elif "network" in prompt_text.lower():
            return "Mock network analysis response"
        else:
            return "Mock general response"
    
    mock_client.generate = AsyncMock(side_effect=mock_generate)
    mock_client.embeddings = AsyncMock(return_value={"embeddings": [0.1, 0.2, 0.3]})
    return mock_client


@pytest.fixture
def mock_wallet_data():
    """Create mock wallet data for testing."""
    return {
        "address": "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",
        "transaction_count": 42,
        "current_balance": {
            "ERG": 100.5,
            "TOKEN1": 50
        },
        "human_readable": "Mock human-readable wallet summary for testing"
    }


@pytest.fixture
def mock_env_variables(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-api-key-for-testing")
    monkeypatch.setenv("OLLAMA_API_URL", "http://mock-ollama:11434")


class TestBlockchainAnalyzer:
    """Tests for the BlockchainAnalyzer class."""
    
    def test_init(self, mock_env_variables):
        """Test initializing a BlockchainAnalyzer."""
        # Test with default parameters
        analyzer = BlockchainAnalyzer()
        assert isinstance(analyzer.llm_client, ClaudeClient)
        assert isinstance(analyzer.context_builder, ContextBuilder)
        
        # Test with custom LLM client
        mock_client = MagicMock(spec=LLMClient)
        analyzer = BlockchainAnalyzer(llm_client=mock_client)
        assert analyzer.llm_client is mock_client
    
    @pytest.mark.asyncio
    async def test_analyze_wallet(self, mock_llm_client, mock_wallet_data):
        """Test analyzing a wallet address."""
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  return_value=mock_wallet_data) as mock_get_wallet:
            analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
            
            # Test with default parameters
            result = await analyzer.analyze_wallet("9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc")
            
            # Check that the wallet data was fetched
            mock_get_wallet.assert_called_once_with("9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc")
            
            # Check that the LLM was called
            mock_llm_client.generate.assert_called_once()
            args, kwargs = mock_llm_client.generate.call_args
            assert "wallet" in kwargs["prompt"].lower()
            assert kwargs["system_prompt"] is not None
            
            # Check the result
            assert result["address"] == "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
            assert result["wallet_data"] == mock_wallet_data
            assert result["question"] is None
            assert result["analysis"] == "Mock wallet analysis response"
            assert "context_id" in result
    
    @pytest.mark.asyncio
    async def test_analyze_wallet_with_question(self, mock_llm_client, mock_wallet_data):
        """Test analyzing a wallet address with a specific question."""
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  return_value=mock_wallet_data):
            analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
            
            # Test with a specific question
            result = await analyzer.analyze_wallet(
                "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",
                question="What tokens does this wallet hold?"
            )
            
            # Check that the LLM was called with the question
            args, kwargs = mock_llm_client.generate.call_args
            assert kwargs["prompt"] == "What tokens does this wallet hold?"
            
            # Check the result
            assert result["question"] == "What tokens does this wallet hold?"
            assert result["analysis"] == "Mock wallet analysis response"
    
    @pytest.mark.asyncio
    async def test_analyze_wallet_with_context(self, mock_llm_client, mock_wallet_data):
        """Test analyzing a wallet address with an existing context."""
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  return_value=mock_wallet_data):
            analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
            
            # Create a context first
            context_id = "test-wallet-context"
            analyzer.context_builder.create_context(context_id)
            analyzer.context_builder.add_to_context(
                context_id,
                "Previous wallet discussion",
                role="assistant"
            )
            
            # Test with the existing context
            result = await analyzer.analyze_wallet(
                "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",
                context_id=context_id
            )
            
            # Check that the context was used
            args, kwargs = mock_llm_client.generate.call_args
            assert len(kwargs["context"]) == 2  # Previous item + new wallet info
            assert kwargs["context"][0]["role"] == "assistant"
            assert kwargs["context"][0]["content"] == "Previous wallet discussion"
            
            # Check the result uses the same context ID
            assert result["context_id"] == context_id
    
    @pytest.mark.asyncio
    async def test_analyze_wallet_error(self, mock_llm_client):
        """Test handling errors when analyzing a wallet."""
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  side_effect=Exception("Mock error")):
            analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
            
            # Test error handling
            result = await analyzer.analyze_wallet("9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc")
            
            # Check that the error was handled correctly
            assert "error" in result
            assert result["error"] == "Mock error"
            assert result["address"] == "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
    
    @pytest.mark.asyncio
    async def test_analyze_transaction(self, mock_llm_client):
        """Test analyzing a transaction."""
        analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
        
        # Test with default parameters
        tx_id = "b29358e110ae76db3f8cbd7296a3323a6bf9b39098e4cd05ea9964e6c1b9a689"
        result = await analyzer.analyze_transaction(tx_id)
        
        # Check that the LLM was called
        mock_llm_client.generate.assert_called_once()
        args, kwargs = mock_llm_client.generate.call_args
        assert tx_id in kwargs["prompt"]
        assert kwargs["system_prompt"] is not None
        
        # Check the result
        assert result["transaction_id"] == tx_id
        assert result["question"] is None
        assert result["analysis"] == "Mock transaction analysis response"
        assert "context_id" in result
        # There should be an error message since this is a placeholder
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_analyze_network(self, mock_llm_client):
        """Test analyzing network metrics."""
        analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
        
        # Test with specific metrics
        metrics = ["hashrate", "difficulty"]
        result = await analyzer.analyze_network(metrics)
        
        # Check that the LLM was called
        mock_llm_client.generate.assert_called_once()
        args, kwargs = mock_llm_client.generate.call_args
        assert "hashrate, difficulty" in kwargs["prompt"]
        assert kwargs["system_prompt"] is not None
        
        # Check the result
        assert result["metrics"] == metrics
        assert result["question"] is None
        assert result["analysis"] == "Mock network analysis response"
        assert "context_id" in result
        # There should be an error message since this is a placeholder
        assert "error" in result
    
    @pytest.mark.asyncio
    async def test_forensic_analysis(self, mock_llm_client):
        """Test performing forensic analysis."""
        analyzer = BlockchainAnalyzer(llm_client=mock_llm_client)
        
        # Test with default parameters
        address = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
        depth = 3
        result = await analyzer.forensic_analysis(address, depth)
        
        # Check that the LLM was called
        mock_llm_client.generate.assert_called_once()
        args, kwargs = mock_llm_client.generate.call_args
        assert address in kwargs["prompt"]
        assert str(depth) in kwargs["prompt"]
        assert kwargs["system_prompt"] is not None
        
        # Check the result
        assert result["address"] == address
        assert result["depth"] == depth
        assert result["question"] is None
        assert result["analysis"] == "Mock forensic analysis response"
        assert "context_id" in result
        # There should be an error message since this is a placeholder
        assert "error" in result


# Test the convenience functions

@pytest.mark.asyncio
async def test_analyze_wallet_function(mock_llm_client, mock_wallet_data, mock_env_variables):
    """Test the analyze_wallet convenience function."""
    with patch("llm.analysis.BlockchainAnalyzer", return_value=MagicMock()) as mock_analyzer_class:
        # Set up the mock analyzer instance
        mock_analyzer_instance = mock_analyzer_class.return_value
        
        # Create an async mock for the analyze_wallet method
        async_result = {
            "address": "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",
            "analysis": "Mock convenience function response"
        }
        mock_analyzer_instance.analyze_wallet = AsyncMock(return_value=async_result)
        
        # Use the convenience function
        with patch("llm.analysis.LLMClientFactory.create", return_value=mock_llm_client):
            from llm.analysis import analyze_wallet
            
            result = await analyze_wallet(
                "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc", 
                question="Test question",
                llm_provider="claude",
                context_id="test-context"
            )
            
            # Validate the result
            assert result["address"] == "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
            assert result["analysis"] == "Mock convenience function response" 