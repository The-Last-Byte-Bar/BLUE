"""
Blockchain module for interacting with cryptocurrency blockchains.

This module provides clients for direct node connections and explorer APIs,
along with data models for blockchain entities.
"""

from .client import BlockchainClient
from .node import NodeClient
from .explorer import ExplorerClient
from .factory import ClientFactory
from .models import Block, Transaction, Address

__all__ = [
    'BlockchainClient',
    'NodeClient',
    'ExplorerClient',
    'ClientFactory',
    'Block',
    'Transaction',
    'Address'
] 