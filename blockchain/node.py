"""
Direct blockchain node client implementation.

This module provides a client for connecting directly to a blockchain node
using its JSON-RPC or REST API.
"""

import json
import aiohttp
from typing import Dict, Any, List, Optional

from .client import BlockchainClient
from .models import Block, Transaction, Address


class NodeClient(BlockchainClient):
    """Client for direct interaction with a blockchain node."""

    def __init__(self, base_url: str, api_key: Optional[str] = None, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the node client.

        Args:
            base_url: Base URL for the blockchain node API
            api_key: Optional API key for authentication
            username: Optional username for authentication
            password: Optional password for authentication
        """
        super().__init__(base_url, api_key)
        self.username = username
        self.password = password
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

    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the blockchain node.

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Optional query parameters
            data: Optional request body data

        Returns:
            Response data as a dictionary
        """
        session = await self._get_session()
        headers = {}
        
        if self.api_key:
            headers['Authorization'] = f'Bearer {self.api_key}'
        
        auth = None
        if self.username and self.password:
            auth = aiohttp.BasicAuth(self.username, self.password)
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with session.request(
            method=method,
            url=url,
            params=params,
            json=data,
            headers=headers,
            auth=auth
        ) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"API error ({response.status}): {error_text}")
            
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
            endpoint = f"blocks/height/{block_param}"
        except ValueError:
            endpoint = f"blocks/{block_id}"
        
        data = await self._make_request("GET", endpoint)
        return Block.from_json(data)

    async def get_transaction(self, tx_id: str) -> Transaction:
        """
        Get a transaction by its ID.

        Args:
            tx_id: Transaction ID (hash)

        Returns:
            Transaction object
        """
        data = await self._make_request("GET", f"transactions/{tx_id}")
        return Transaction.from_json(data)

    async def get_address(self, address: str) -> Address:
        """
        Get address details.

        Args:
            address: Blockchain address

        Returns:
            Address object
        """
        data = await self._make_request("GET", f"addresses/{address}")
        return Address.from_json(data)

    async def get_balance(self, address: str) -> Dict[str, float]:
        """
        Get the balance of an address.

        Args:
            address: Blockchain address

        Returns:
            Dictionary mapping asset IDs to amounts
        """
        data = await self._make_request("GET", f"addresses/{address}/balance")
        return {asset['id']: asset['amount'] for asset in data.get('assets', [])}

    async def submit_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Submit a transaction to the blockchain.

        Args:
            transaction_data: Transaction data in the format required by the blockchain

        Returns:
            Transaction ID if successful
        """
        response = await self._make_request("POST", "transactions", data=transaction_data)
        return response.get('id')

    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current status of the blockchain network.

        Returns:
            Dictionary with network status information
        """
        return await self._make_request("GET", "info") 