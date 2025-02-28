"""
Unit tests for the blockchain explorer client.
"""

import os
import pytest
import aiohttp
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime

from ..explorer import ExplorerClient
from ..models import Block, Transaction, Address

# Test address to use in tests
TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"


@pytest.fixture
def mock_response():
    """Create a mock aiohttp response."""
    mock = MagicMock()
    mock.status = 200
    mock.json = AsyncMock()
    return mock


@pytest.fixture
def explorer_client():
    """Create an ExplorerClient instance for testing."""
    return ExplorerClient(base_url="https://api.ergoplatform.com")


@pytest.mark.asyncio
async def test_get_block(explorer_client, mock_response):
    """Test fetching a block by ID."""
    block_data = {
        "id": "123abc",
        "height": 100,
        "timestamp": 1625000000000,
        "transactions": ["tx1", "tx2"]
    }
    mock_response.json.return_value = block_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        block = await explorer_client.get_block("123abc")
        
    assert isinstance(block, Block)
    assert block.id == "123abc"
    assert block.height == 100
    assert isinstance(block.timestamp, datetime)
    assert block.transactions == ["tx1", "tx2"]


@pytest.mark.asyncio
async def test_get_transaction(explorer_client, mock_response):
    """Test fetching a transaction by ID."""
    tx_data = {
        "id": "tx123",
        "blockId": "block123",
        "timestamp": 1625000000000,
        "inputs": [{"id": "input1"}],
        "outputs": [{"id": "output1"}]
    }
    mock_response.json.return_value = tx_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        tx = await explorer_client.get_transaction("tx123")
        
    assert isinstance(tx, Transaction)
    assert tx.id == "tx123"
    assert tx.block_id == "block123"
    assert isinstance(tx.timestamp, datetime)
    assert len(tx.inputs) == 1
    assert len(tx.outputs) == 1


@pytest.mark.asyncio
async def test_get_address(explorer_client, mock_response):
    """Test fetching address details."""
    address_data = {
        "summary": {
            "id": TEST_ADDRESS
        },
        "transactions": {
            "confirmed": 10
        }
    }
    mock_response.json.return_value = address_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        address = await explorer_client.get_address(TEST_ADDRESS)
        
    assert isinstance(address, Address)
    assert address.address == TEST_ADDRESS
    assert address.transactions_count == 10


@pytest.mark.asyncio
async def test_get_balance(explorer_client, mock_response):
    """Test fetching address balance."""
    balance_data = {
        "nanoErgs": 1000000000,
        "tokens": [
            {"tokenId": "token1", "amount": 10},
            {"tokenId": "token2", "amount": 20}
        ]
    }
    mock_response.json.return_value = balance_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        balance = await explorer_client.get_balance(TEST_ADDRESS)
        
    assert isinstance(balance, dict)
    assert balance["token1"] == 10
    assert balance["token2"] == 20
    assert balance["nanoErgs"] == 1000000000


@pytest.mark.asyncio
async def test_get_address_total_balance(explorer_client, mock_response):
    """Test fetching total address balance."""
    total_balance_data = {
        "confirmed": {
            "nanoErgs": 1000000000,
            "tokens": [
                {"tokenId": "token1", "amount": 10}
            ]
        },
        "unconfirmed": {
            "nanoErgs": 200000000,
            "tokens": [
                {"tokenId": "token1", "amount": 5}
            ]
        }
    }
    mock_response.json.return_value = total_balance_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        total_balance = await explorer_client.get_address_total_balance(TEST_ADDRESS)
        
    assert isinstance(total_balance, dict)
    assert total_balance["confirmed"]["nanoErgs"] == 1000000000
    assert total_balance["unconfirmed"]["nanoErgs"] == 200000000
    assert total_balance["confirmed"]["tokens"][0]["amount"] == 10
    assert total_balance["unconfirmed"]["tokens"][0]["amount"] == 5


@pytest.mark.asyncio
async def test_get_transactions_for_address(explorer_client, mock_response):
    """Test fetching transactions for an address."""
    tx_list_data = {
        "items": [
            {
                "id": "tx1",
                "timestamp": 1625000000000
            },
            {
                "id": "tx2",
                "timestamp": 1626000000000
            }
        ],
        "total": 2
    }
    mock_response.json.return_value = tx_list_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        txs = await explorer_client.get_transactions_for_address(TEST_ADDRESS)
        
    assert isinstance(txs, list)
    assert len(txs) == 2
    assert txs[0]["id"] == "tx1"
    assert txs[1]["id"] == "tx2"


@pytest.mark.asyncio
async def test_get_unspent_outputs(explorer_client, mock_response):
    """Test fetching unspent outputs for an address."""
    utxo_data = {
        "items": [
            {
                "boxId": "box1",
                "value": 1000000000
            },
            {
                "boxId": "box2",
                "value": 2000000000
            }
        ],
        "total": 2
    }
    mock_response.json.return_value = utxo_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        utxos = await explorer_client.get_unspent_outputs(TEST_ADDRESS)
        
    assert isinstance(utxos, list)
    assert len(utxos) == 2
    assert utxos[0]["boxId"] == "box1"
    assert utxos[1]["boxId"] == "box2"


@pytest.mark.asyncio
async def test_submit_transaction(explorer_client, mock_response):
    """Test submitting a transaction."""
    tx_data = {"id": "tx123"}
    mock_response.json.return_value = tx_data
    
    with patch("aiohttp.ClientSession.post", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        tx_id = await explorer_client.submit_transaction({"id": "tx123", "inputs": [], "outputs": []})
        
    assert tx_id == "tx123"


@pytest.mark.asyncio
async def test_get_network_status(explorer_client, mock_response):
    """Test fetching network status."""
    status_data = {
        "currentHeight": 1000,
        "currentDifficulty": 12345
    }
    mock_response.json.return_value = status_data
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_response))):
        status = await explorer_client.get_network_status()
        
    assert isinstance(status, dict)
    assert status["currentHeight"] == 1000
    assert status["currentDifficulty"] == 12345


@pytest.mark.asyncio
async def test_api_error_handling(explorer_client):
    """Test API error handling."""
    error_response = MagicMock()
    error_response.status = 404
    error_response.text = AsyncMock(return_value="Not found")
    
    with patch("aiohttp.ClientSession.get", return_value=AsyncMock(__aenter__=AsyncMock(return_value=error_response))):
        with pytest.raises(Exception) as excinfo:
            await explorer_client.get_block("nonexistent")
            
    assert "Explorer API error (404)" in str(excinfo.value) 