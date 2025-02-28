"""
Blockchain explorer API client implementation.

This module provides a client for connecting to blockchain explorer APIs
which often provide higher-level aggregated data about blockchain entities.
"""

import aiohttp
import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from .client import BlockchainClient
from .models import Block, Transaction, Address


class ExplorerClient(BlockchainClient):
    """Client for interaction with a blockchain explorer API."""

    def __init__(self, base_url: str = None, api_key: Optional[str] = None):
        """
        Initialize the explorer client.

        Args:
            base_url: Base URL for the blockchain explorer API
            api_key: Optional API key for authentication
        """
        # Load environment variables
        load_dotenv()
        
        # Use provided base_url or get from environment variables
        base_url = base_url or os.getenv('EXPLORER_API_URL', 'https://api.ergoplatform.com')
        api_key = api_key or os.getenv('EXPLORER_API_KEY')
        
        super().__init__(base_url, api_key)
        self.session = None

    async def __aenter__(self):
        """Set up the HTTP session when used as an async context manager."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session when exiting the async context manager."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_session(self):
        """Get or create an HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the blockchain explorer API.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response data as a dictionary
        """
        session = await self._get_session()
        headers = {}
        
        if self.api_key:
            headers['api_key'] = self.api_key
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with session.get(url, params=params, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Explorer API error ({response.status}): {error_text}")
            
            return await response.json()

    async def get_block(self, block_id: str) -> Block:
        """
        Get a block by its ID or height.

        Args:
            block_id: Block ID (hash) or height

        Returns:
            Block object
        """
        # Try to parse as integer (height) or use as hash
        try:
            block_param = int(block_id)
            data = await self._make_request("api/v1/blocks", {"height": block_param})
        except ValueError:
            data = await self._make_request(f"api/v1/blocks/{block_id}")
        
        return Block.from_json(data)

    async def get_transaction(self, tx_id: str) -> Transaction:
        """
        Get a transaction by its ID.

        Args:
            tx_id: Transaction ID (hash)

        Returns:
            Transaction object
        """
        data = await self._make_request(f"api/v1/transactions/{tx_id}")
        return Transaction.from_json(data)

    async def get_address(self, address: str) -> Address:
        """
        Get address details.

        Args:
            address: Blockchain address

        Returns:
            Address object
        """
        # Use the v0 API endpoint which we confirmed is working
        data = await self._make_request(f"api/v0/addresses/{address}")
        # Prepare the data for the Address model
        address_data = {
            'address': address,
            'transactionsCount': data.get('transactions', {}).get('confirmed', 0)
        }
        return Address.from_json(address_data)

    async def get_balance(self, address: str) -> Dict[str, float]:
        """
        Get the balance of an address.

        Args:
            address: Blockchain address

        Returns:
            Dictionary mapping asset IDs to amounts
        """
        # Use the working endpoint for balance information
        data = await self._make_request(f"api/v1/addresses/{address}/balance/confirmed")
        tokens = {}
        
        # Extract tokens
        for token in data.get('tokens', []):
            tokens[token.get('tokenId')] = token.get('amount')
            
        # Add nanoErgs as a special asset
        tokens['nanoErgs'] = data.get('nanoErgs', 0)
        
        return tokens

    async def get_address_total_balance(self, address: str) -> Dict[str, Any]:
        """
        Get the total balance for an address, including confirmed and unconfirmed.

        Args:
            address: Blockchain address

        Returns:
            Dictionary with balance information including nanoErgs and tokens
        """
        data = await self._make_request(f"api/v1/addresses/{address}/balance/total")
        return data

    async def submit_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Submit a transaction to the blockchain via the explorer.

        Args:
            transaction_data: Transaction data in the format required by the blockchain

        Returns:
            Transaction ID if successful
        """
        session = await self._get_session()
        headers = {'Content-Type': 'application/json'}
        
        if self.api_key:
            headers['api_key'] = self.api_key
        
        url = f"{self.base_url.rstrip('/')}/api/v1/mempool/transactions/submit"
        
        async with session.post(url, json=transaction_data, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Transaction submission error ({response.status}): {error_text}")
            
            result = await response.json()
            return result.get('id')

    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current status of the blockchain network.

        Returns:
            Dictionary with network status information
        """
        return await self._make_request("api/v1/info")
    
    async def get_rich_list(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get the richest addresses on the blockchain.

        Args:
            limit: Maximum number of addresses to return
            offset: Offset for pagination

        Returns:
            List of address data
        """
        data = await self._make_request("api/v1/addresses/rich", {"limit": limit, "offset": offset})
        return data.get('items', [])
    
    async def get_transactions_for_address(self, address: str, limit: int = 50, offset: int = 0, concise: bool = False) -> List[Dict[str, Any]]:
        """
        Get transactions for a specific address.

        Args:
            address: Blockchain address
            limit: Maximum number of transactions to return
            offset: Offset for pagination
            concise: Whether to return concise transaction data (True) or full data (False)

        Returns:
            List of transaction data
        """
        params = {"limit": limit, "offset": offset}
        if concise:
            params["concise"] = "true"
            
        data = await self._make_request(f"api/v1/addresses/{address}/transactions", params)
        return data.get('items', [])
    
    async def get_unspent_outputs(self, address: str) -> List[Dict[str, Any]]:
        """
        Get unspent outputs (UTXOs) for a specific address.

        Args:
            address: Blockchain address

        Returns:
            List of UTXO data
        """
        data = await self._make_request(f"api/v1/addresses/{address}/boxes/unspent")
        return data.get('items', []) 