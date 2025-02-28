"""
Integration tests for the LLM blockchain analysis module.

This module contains tests that verify the proper integration of multiple
components of the LLM blockchain analysis system, including clients,
context management, and analysis functionality.
"""

import pytest
import os
import json
from unittest.mock import patch, AsyncMock, MagicMock

from llm.client import LLMClientFactory, LLMClient
from llm.analysis import BlockchainAnalyzer, ContextBuilder, analyze_wallet


class MockWalletModule:
    """Mock for the wallet analysis module."""
    
    @staticmethod
    def get_wallet_analysis_for_llm(address):
        """Return mock wallet data for testing."""
        return {
            "address": address,
            "transaction_count": 42,
            "current_balance": {
                "ERG": 100.5,
                "TOKEN1": 50
            },
            "human_readable": f"Mock wallet data for {address}"
        }


@pytest.fixture
def mock_llm_client():
    """Create a mock LLM client that simulates responses."""
    mock_client = MagicMock(spec=LLMClient)
    
    async def mock_generate(prompt, context=None, system_prompt=None, **kwargs):
        if context:
            return f"Response with context: {len(context)} items in context. Analyzing: {prompt[:30]}..."
        else:
            return f"Response without context. Analyzing: {prompt[:30]}..."
    
    mock_client.generate = AsyncMock(side_effect=mock_generate)
    return mock_client


@pytest.fixture
def mock_env_variables(monkeypatch):
    """Set up mock environment variables for testing."""
    monkeypatch.setenv("ANTHROPIC_API_KEY", "mock-api-key-for-testing")
    monkeypatch.setenv("OLLAMA_API_URL", "http://mock-ollama:11434")


@pytest.mark.asyncio
async def test_end_to_end_wallet_analysis(mock_env_variables):
    """Test the end-to-end flow of wallet analysis."""
    # Mock the necessary components
    with patch("llm.client.LLMClientFactory.create") as mock_factory:
        with patch("llm.analysis.get_wallet_analysis_for_llm",
                  side_effect=MockWalletModule.get_wallet_analysis_for_llm):
            # Setup the mock client
            mock_client = MagicMock(spec=LLMClient)
            mock_client.generate = AsyncMock(return_value="This wallet appears to be a mining wallet with regular income.")
            mock_factory.return_value = mock_client
            
            # Call the convenience function
            result = await analyze_wallet(
                "9test1testWalletAddressForIntegrationTest",
                question="What kind of wallet is this?",
                llm_provider="claude"
            )
            
            # Verify that the factory was called correctly
            mock_factory.assert_called_once_with(provider="claude")
            
            # Verify that the client generate method was called
            mock_client.generate.assert_called_once()
            
            # Check the results
            assert result["address"] == "9test1testWalletAddressForIntegrationTest"
            assert result["analysis"] == "This wallet appears to be a mining wallet with regular income."
            assert "context_id" in result


@pytest.mark.asyncio
async def test_conversation_flow(mock_env_variables):
    """Test a conversation flow with context preservation."""
    # Mock the necessary components
    with patch("llm.client.LLMClientFactory.create") as mock_factory:
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  side_effect=MockWalletModule.get_wallet_analysis_for_llm):
            # Setup the mock client
            mock_client = MagicMock(spec=LLMClient)
            
            # Create responses for a conversation flow
            responses = [
                "Initial analysis: This appears to be a mining wallet.",
                "Follow-up response: The wallet has been active for about 3 months.",
                "Final response: The wallet interacts mostly with exchange wallets."
            ]
            mock_client.generate = AsyncMock(side_effect=responses)
            mock_factory.return_value = mock_client
            
            # Create analyzer directly to maintain context through multiple calls
            analyzer = BlockchainAnalyzer(llm_client=mock_client)
            
            # First question
            result1 = await analyzer.analyze_wallet(
                "9test1testWalletAddressForIntegrationTest",
                question="What kind of wallet is this?"
            )
            context_id = result1["context_id"]
            
            # Second question using the same context
            result2 = await analyzer.analyze_wallet(
                "9test1testWalletAddressForIntegrationTest",
                question="How long has it been active?",
                context_id=context_id
            )
            
            # Third question using the same context
            result3 = await analyzer.analyze_wallet(
                "9test1testWalletAddressForIntegrationTest",
                question="What other wallets does it interact with?",
                context_id=context_id
            )
            
            # Verify the responses match our expected sequence
            assert result1["analysis"] == responses[0]
            assert result2["analysis"] == responses[1]
            assert result3["analysis"] == responses[2]
            
            # Verify all used the same context
            assert result1["context_id"] == context_id
            assert result2["context_id"] == context_id
            assert result3["context_id"] == context_id
            
            # Verify the context is building up (checking call details)
            args, kwargs = mock_client.generate.call_args_list[2]
            # By the third call, context should have at least 2 previous interactions
            assert len(kwargs["context"]) >= 2


@pytest.mark.asyncio
async def test_error_handling(mock_env_variables):
    """Test error handling across the integration."""
    # Set up the test with controlled failures
    with patch("llm.client.LLMClientFactory.create") as mock_factory:
        # First test API errors
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate = AsyncMock(side_effect=Exception("API Error"))
        mock_factory.return_value = mock_client
        
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  return_value=MockWalletModule.get_wallet_analysis_for_llm("test_address")):
            # Call the analyze function
            result = await analyze_wallet("test_address", llm_provider="claude")
            
            # Check that errors are properly captured and returned
            assert "error" in result
            assert "API Error" in result["error"]
            
    # Now test data retrieval errors
    with patch("llm.client.LLMClientFactory.create") as mock_factory:
        mock_client = MagicMock(spec=LLMClient)
        mock_client.generate = AsyncMock(return_value="This should not be reached")
        mock_factory.return_value = mock_client
        
        with patch("llm.analysis.get_wallet_analysis_for_llm", 
                  side_effect=Exception("Data Retrieval Error")):
            # Call the analyze function
            result = await analyze_wallet("test_address", llm_provider="claude")
            
            # Verify error handling
            assert "error" in result
            assert "Data Retrieval Error" in result["error"]
            # The client should not have been called
            mock_client.generate.assert_not_called()


@pytest.mark.asyncio
async def test_environment_configuration(mock_env_variables):
    """Test that the system correctly uses environment variables."""
    # Temporarily set environment variables
    original_api_key = os.environ.get('ANTHROPIC_API_KEY')
    original_api_url = os.environ.get('ANTHROPIC_API_URL')
    
    try:
        os.environ['ANTHROPIC_API_KEY'] = 'test_api_key'
        os.environ['ANTHROPIC_API_URL'] = 'https://test.api.anthropic.com'
        
        # Test with mocked aiohttp session
        with patch("aiohttp.ClientSession.post") as mock_post:
            mock_response = AsyncMock()
            mock_response.status = 200
            
            async def mock_json():
                return {"content": [{"text": "Test response"}]}
            
            mock_response.json = mock_json
            
            # Mock the context manager behavior
            mock_cm = AsyncMock()
            mock_cm.__aenter__.return_value = mock_response
            mock_post.return_value = mock_cm
            
            with patch("llm.analysis.get_wallet_analysis_for_llm", 
                      side_effect=MockWalletModule.get_wallet_analysis_for_llm):
                # Use a real client but mock the API call
                from llm.client import ClaudeClient
                client = ClaudeClient()
                analyzer = BlockchainAnalyzer(llm_client=client)
                
                # Call a method to test the API call
                response = await client.generate("Test prompt")
                
                # Check if the API key was correctly used
                mock_post.assert_called_once()
                args, kwargs = mock_post.call_args
                assert kwargs["headers"]["x-api-key"] == "test_api_key"
                assert response == "Test response"
    finally:
        # Restore original environment variables
        if original_api_key is not None:
            os.environ['ANTHROPIC_API_KEY'] = original_api_key
        else:
            os.environ.pop('ANTHROPIC_API_KEY', None)
            
        if original_api_url is not None:
            os.environ['ANTHROPIC_API_URL'] = original_api_url
        else:
            os.environ.pop('ANTHROPIC_API_URL', None) 