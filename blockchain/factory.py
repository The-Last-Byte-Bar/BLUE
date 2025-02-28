"""
Factory module for creating blockchain clients.

This module provides a factory class for creating blockchain clients
based on configuration parameters.
"""

from typing import Dict, Any, Optional
from enum import Enum

from .client import BlockchainClient
from .node import NodeClient
from .explorer import ExplorerClient


class ClientType(Enum):
    """Enum of blockchain client types."""
    NODE = "node"
    EXPLORER = "explorer"


class ClientFactory:
    """Factory for creating blockchain clients."""

    @staticmethod
    def create_client(
        client_type: ClientType,
        base_url: str,
        api_key: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ) -> BlockchainClient:
        """
        Create a blockchain client based on the specified type.

        Args:
            client_type: Type of client to create
            base_url: Base URL for the blockchain API
            api_key: Optional API key for authentication
            username: Optional username for authentication
            password: Optional password for authentication

        Returns:
            A blockchain client instance
        """
        if client_type == ClientType.NODE:
            return NodeClient(base_url, api_key, username, password)
        elif client_type == ClientType.EXPLORER:
            return ExplorerClient(base_url, api_key)
        else:
            raise ValueError(f"Unsupported client type: {client_type}")

    @staticmethod
    def create_from_config(config: Dict[str, Any]) -> BlockchainClient:
        """
        Create a blockchain client from a configuration dictionary.

        Args:
            config: Configuration dictionary with keys:
                - type: Client type (node or explorer)
                - base_url: Base URL for the blockchain API
                - api_key: Optional API key for authentication
                - username: Optional username for authentication
                - password: Optional password for authentication

        Returns:
            A blockchain client instance
        """
        client_type_str = config.get('type', 'node').lower()
        try:
            client_type = ClientType(client_type_str)
        except ValueError:
            raise ValueError(f"Unsupported client type: {client_type_str}")
        
        base_url = config.get('base_url')
        if not base_url:
            raise ValueError("base_url is required in client configuration")
        
        return ClientFactory.create_client(
            client_type=client_type,
            base_url=base_url,
            api_key=config.get('api_key'),
            username=config.get('username'),
            password=config.get('password')
        ) 