"""
Abstract base class for blockchain clients.

This module defines the abstract interface for all blockchain clients,
whether they connect to a node directly or via an explorer API.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional

from .models import Block, Transaction, Address


class BlockchainClient(ABC):
    """Abstract base class for all blockchain clients."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the blockchain client.

        Args:
            base_url: Base URL for the blockchain node or API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key

    @abstractmethod
    async def get_block(self, block_id: str) -> Block:
        """
        Get a block by its ID or height.

        Args:
            block_id: Block ID (hash) or height

        Returns:
            Block object
        """
        pass

    @abstractmethod
    async def get_transaction(self, tx_id: str) -> Transaction:
        """
        Get a transaction by its ID.

        Args:
            tx_id: Transaction ID (hash)

        Returns:
            Transaction object
        """
        pass

    @abstractmethod
    async def get_address(self, address: str) -> Address:
        """
        Get address details.

        Args:
            address: Blockchain address

        Returns:
            Address object
        """
        pass

    @abstractmethod
    async def get_balance(self, address: str) -> Dict[str, float]:
        """
        Get the balance of an address.

        Args:
            address: Blockchain address

        Returns:
            Dictionary mapping asset IDs to amounts
        """
        pass

    @abstractmethod
    async def submit_transaction(self, transaction_data: Dict[str, Any]) -> str:
        """
        Submit a transaction to the blockchain.

        Args:
            transaction_data: Transaction data in the format required by the blockchain

        Returns:
            Transaction ID if successful
        """
        pass

    @abstractmethod
    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get the current status of the blockchain network.

        Returns:
            Dictionary with network status information
        """
        pass 