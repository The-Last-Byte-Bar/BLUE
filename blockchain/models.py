"""
Data models for blockchain entities.

This module defines the data models for common blockchain entities like
blocks, transactions, and addresses.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


class Block:
    """Model representing a blockchain block."""

    def __init__(
        self,
        id: str,
        height: int,
        timestamp: datetime,
        transactions: List[str],
        miner: Optional[str] = None,
        size: Optional[int] = None,
        difficulty: Optional[float] = None,
        nonce: Optional[str] = None,
        version: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Block instance.

        Args:
            id: Block ID (hash)
            height: Block height
            timestamp: Block timestamp
            transactions: List of transaction IDs
            miner: Optional miner address
            size: Optional block size in bytes
            difficulty: Optional mining difficulty
            nonce: Optional nonce value
            version: Optional block version
            raw_data: Optional raw block data
        """
        self.id = id
        self.height = height
        self.timestamp = timestamp
        self.transactions = transactions
        self.miner = miner
        self.size = size
        self.difficulty = difficulty
        self.nonce = nonce
        self.version = version
        self.raw_data = raw_data or {}

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Block':
        """
        Create a Block instance from JSON data.

        Args:
            data: JSON data representing a block

        Returns:
            Block instance
        """
        # Handle different timestamp formats
        timestamp = data.get('timestamp')
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
        elif isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = datetime.now()  # Fallback
        else:
            timestamp = datetime.now()  # Fallback

        return cls(
            id=data.get('id') or data.get('hash') or '',
            height=data.get('height', 0),
            timestamp=timestamp,
            transactions=data.get('transactions', []),
            miner=data.get('miner'),
            size=data.get('size'),
            difficulty=data.get('difficulty'),
            nonce=data.get('nonce'),
            version=data.get('version'),
            raw_data=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Block instance to a dictionary.

        Returns:
            Dictionary representation of the block
        """
        return {
            'id': self.id,
            'height': self.height,
            'timestamp': self.timestamp.isoformat(),
            'transactions': self.transactions,
            'miner': self.miner,
            'size': self.size,
            'difficulty': self.difficulty,
            'nonce': self.nonce,
            'version': self.version
        }


class Transaction:
    """Model representing a blockchain transaction."""

    def __init__(
        self,
        id: str,
        block_id: Optional[str] = None,
        timestamp: Optional[datetime] = None,
        inputs: Optional[List[Dict[str, Any]]] = None,
        outputs: Optional[List[Dict[str, Any]]] = None,
        fee: Optional[float] = None,
        size: Optional[int] = None,
        status: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a Transaction instance.

        Args:
            id: Transaction ID (hash)
            block_id: Optional block ID containing this transaction
            timestamp: Optional transaction timestamp
            inputs: Optional list of transaction inputs
            outputs: Optional list of transaction outputs
            fee: Optional transaction fee
            size: Optional transaction size in bytes
            status: Optional transaction status
            raw_data: Optional raw transaction data
        """
        self.id = id
        self.block_id = block_id
        self.timestamp = timestamp
        self.inputs = inputs or []
        self.outputs = outputs or []
        self.fee = fee
        self.size = size
        self.status = status
        self.raw_data = raw_data or {}

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Transaction':
        """
        Create a Transaction instance from JSON data.

        Args:
            data: JSON data representing a transaction

        Returns:
            Transaction instance
        """
        # Handle different timestamp formats
        timestamp = data.get('timestamp')
        if isinstance(timestamp, (int, float)):
            timestamp = datetime.fromtimestamp(timestamp / 1000 if timestamp > 1e10 else timestamp)
        elif isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except ValueError:
                timestamp = None
        else:
            timestamp = None

        return cls(
            id=data.get('id') or data.get('hash') or '',
            block_id=data.get('blockId') or data.get('blockHash'),
            timestamp=timestamp,
            inputs=data.get('inputs', []),
            outputs=data.get('outputs', []),
            fee=data.get('fee'),
            size=data.get('size'),
            status=data.get('status'),
            raw_data=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Transaction instance to a dictionary.

        Returns:
            Dictionary representation of the transaction
        """
        return {
            'id': self.id,
            'block_id': self.block_id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'inputs': self.inputs,
            'outputs': self.outputs,
            'fee': self.fee,
            'size': self.size,
            'status': self.status
        }


class Address:
    """Model representing a blockchain address."""

    def __init__(
        self,
        address: str,
        balance: Optional[Dict[str, float]] = None,
        transactions_count: Optional[int] = None,
        first_seen: Optional[datetime] = None,
        last_seen: Optional[datetime] = None,
        raw_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an Address instance.

        Args:
            address: The blockchain address string
            balance: Optional dictionary mapping asset IDs to amounts
            transactions_count: Optional count of transactions
            first_seen: Optional timestamp of first appearance
            last_seen: Optional timestamp of last appearance
            raw_data: Optional raw address data
        """
        self.address = address
        self.balance = balance or {}
        self.transactions_count = transactions_count
        self.first_seen = first_seen
        self.last_seen = last_seen
        self.raw_data = raw_data or {}

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> 'Address':
        """
        Create an Address instance from JSON data.

        Args:
            data: JSON data representing an address

        Returns:
            Address instance
        """
        # Extract balance data
        balance = {}
        if 'balance' in data:
            if isinstance(data['balance'], dict):
                balance = data['balance']
            elif isinstance(data['balance'], (int, float)):
                balance = {'default': float(data['balance'])}
        elif 'assets' in data:
            for asset in data.get('assets', []):
                asset_id = asset.get('id', 'default')
                balance[asset_id] = asset.get('amount', 0)

        # Handle different timestamp formats
        first_seen = data.get('firstSeen')
        if isinstance(first_seen, (int, float)):
            first_seen = datetime.fromtimestamp(first_seen / 1000 if first_seen > 1e10 else first_seen)
        elif isinstance(first_seen, str):
            try:
                first_seen = datetime.fromisoformat(first_seen.replace('Z', '+00:00'))
            except ValueError:
                first_seen = None
        else:
            first_seen = None

        last_seen = data.get('lastSeen')
        if isinstance(last_seen, (int, float)):
            last_seen = datetime.fromtimestamp(last_seen / 1000 if last_seen > 1e10 else last_seen)
        elif isinstance(last_seen, str):
            try:
                last_seen = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
            except ValueError:
                last_seen = None
        else:
            last_seen = None

        return cls(
            address=data.get('address') or '',
            balance=balance,
            transactions_count=data.get('transactionsCount') or data.get('txsCount'),
            first_seen=first_seen,
            last_seen=last_seen,
            raw_data=data
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the Address instance to a dictionary.

        Returns:
            Dictionary representation of the address
        """
        return {
            'address': self.address,
            'balance': self.balance,
            'transactions_count': self.transactions_count,
            'first_seen': self.first_seen.isoformat() if self.first_seen else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        } 