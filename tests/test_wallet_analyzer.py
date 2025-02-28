"""
Tests for the wallet analyzer.

This module tests the WalletAnalyzer functionality to ensure it correctly
analyzes wallet transactions and formats token amounts.
"""

import asyncio
import pytest
from decimal import Decimal
from unittest.mock import patch, AsyncMock, MagicMock

from data.wallet_analyzer import WalletAnalyzer
from blockchain.explorer import ExplorerClient


@pytest.fixture
def mock_client():
    """Create a mock blockchain client for testing."""
    client = AsyncMock(spec=ExplorerClient)
    
    # Mock get_balance method
    client.get_balance.return_value = {
        'nanoErgs': 1000000000,  # 1 ERG
        'tokenId1': 1000000,     # Some token
        'tokenId2': 500          # Another token
    }
    
    # Mock get_address method
    address_mock = MagicMock()
    address_mock.transactions_count = 42
    client.get_address.return_value = address_mock
    
    # Mock get_transactions_for_address method
    client.get_transactions_for_address.return_value = [
        {
            'id': 'tx1',
            'inputs': [
                {
                    'address': 'testAddress',
                    'value': 500000000,  # 0.5 ERG
                    'assets': [
                        {'tokenId': 'tokenId1', 'amount': 100000}
                    ]
                }
            ],
            'outputs': [
                {
                    'address': 'testAddress',
                    'value': 2000000000,  # 2 ERG
                    'assets': [
                        {'tokenId': 'tokenId1', 'amount': 500000},
                        {'tokenId': 'tokenId2', 'amount': 500}
                    ]
                }
            ]
        }
    ]
    
    # Mock _make_request method
    client._make_request = AsyncMock()
    client._make_request.return_value = {
        'name': 'Test Token',
        'decimals': 6  # 6 decimal places for token
    }
    
    return client


@pytest.mark.asyncio
async def test_format_token_amount(mock_client):
    """Test that token amounts are formatted correctly."""
    analyzer = WalletAnalyzer(mock_client)
    
    # Test ERG formatting (9 decimal places)
    decimal_value, formatted = await analyzer.format_token_amount('nanoErgs', 1000000000)
    assert decimal_value == Decimal('1')
    assert formatted == '1 ERG'
    
    # Test token formatting with mock decimals (6)
    decimal_value, formatted = await analyzer.format_token_amount('tokenId1', 1000000)
    assert decimal_value == Decimal('1')
    assert formatted == '1 Test Token'
    
    # Test small amount
    decimal_value, formatted = await analyzer.format_token_amount('tokenId1', 1000)
    assert decimal_value == Decimal('0.001')
    assert formatted == '0.001 Test Token'
    
    # Test zero amount
    decimal_value, formatted = await analyzer.format_token_amount('tokenId1', 0)
    assert decimal_value == Decimal('0')
    assert formatted == '0 Test Token'


@pytest.mark.asyncio
async def test_analyze_address_transactions(mock_client):
    """Test transaction analysis for an address."""
    analyzer = WalletAnalyzer(mock_client)
    analysis = await analyzer.analyze_address_transactions('testAddress')
    
    # Check that incoming and outgoing are tracked
    assert 'incoming' in analysis
    assert 'outgoing' in analysis
    
    # Check ERG values
    assert 'nanoErgs' in analysis['incoming']
    assert 'nanoErgs' in analysis['outgoing']
    assert analysis['incoming']['nanoErgs']['raw_amount'] == 2000000000  # 2 ERG in
    assert analysis['outgoing']['nanoErgs']['raw_amount'] == 500000000   # 0.5 ERG out
    
    # Check token values
    assert 'tokenId1' in analysis['incoming']
    assert 'tokenId1' in analysis['outgoing']
    assert analysis['incoming']['tokenId1']['raw_amount'] == 500000
    assert analysis['outgoing']['tokenId1']['raw_amount'] == 100000
    
    # Check net calculation
    assert 'net' in analysis
    assert 'nanoErgs' in analysis['net']
    assert analysis['net']['nanoErgs'] == 1500000000  # 2 ERG in - 0.5 ERG out


@pytest.mark.asyncio
async def test_get_wallet_summary(mock_client):
    """Test getting a complete wallet summary."""
    analyzer = WalletAnalyzer(mock_client)
    summary = await analyzer.get_wallet_summary('testAddress')
    
    # Check summary structure
    assert 'address' in summary
    assert 'current_balance' in summary
    assert 'transaction_count' in summary
    assert 'analysis' in summary
    assert 'human_readable' in summary
    
    # Check balance values
    assert 'nanoErgs' in summary['current_balance']
    assert summary['current_balance']['nanoErgs']['raw_amount'] == 1000000000
    
    # Check transaction count
    assert summary['transaction_count'] == 42
    
    # Ensure human readable summary was generated
    assert len(summary['human_readable']) > 0


@pytest.mark.asyncio
async def test_generate_human_readable_summary(mock_client):
    """Test generating a human-readable summary."""
    analyzer = WalletAnalyzer(mock_client)
    
    # Create a test summary
    test_summary = {
        'address': 'testAddress',
        'current_balance': {
            'nanoErgs': {'raw_amount': 1000000000, 'formatted': '1 ERG'},
            'tokenId1': {'raw_amount': 1000000, 'formatted': '1 Test Token'}
        },
        'transaction_count': 42,
        'analysis': {
            'incoming': {
                'nanoErgs': {'raw_amount': 2000000000, 'formatted': '2 ERG'},
                'tokenId1': {'raw_amount': 500000, 'formatted': '0.5 Test Token'}
            },
            'outgoing': {
                'nanoErgs': {'raw_amount': 500000000, 'formatted': '0.5 ERG'},
                'tokenId1': {'raw_amount': 100000, 'formatted': '0.1 Test Token'}
            }
        }
    }
    
    human_summary = await analyzer.generate_human_readable_summary(test_summary)
    
    # Check that key information is included in the summary
    assert 'testAddress' in human_summary
    assert '42' in human_summary  # Transaction count
    assert '1 ERG' in human_summary
    assert 'Test Token' in human_summary
    assert 'Incoming' in human_summary
    assert 'Outgoing' in human_summary


if __name__ == "__main__":
    # Run tests directly when script is executed
    asyncio.run(test_format_token_amount(mock_client()))
    asyncio.run(test_analyze_address_transactions(mock_client()))
    asyncio.run(test_get_wallet_summary(mock_client()))
    asyncio.run(test_generate_human_readable_summary(mock_client()))
    print("All tests passed!") 