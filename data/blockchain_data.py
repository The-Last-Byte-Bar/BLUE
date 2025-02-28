"""
Blockchain data handlers.

This module provides handlers for fetching and processing data from blockchain sources.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
from datetime import datetime, timedelta

from .processor import DataSource
from ..blockchain.client import BlockchainClient
from ..blockchain.models import Block, Transaction, Address

logger = logging.getLogger(__name__)


class BlockchainDataHandler(DataSource):
    """Handler for blockchain data."""

    def __init__(self, client: BlockchainClient):
        """
        Initialize the blockchain data handler.

        Args:
            client: Blockchain client to use for data access
        """
        self.client = client
        self.cache: Dict[str, Dict[str, Any]] = {
            'blocks': {},
            'transactions': {},
            'addresses': {}
        }
        self.cache_expiry: Dict[str, Dict[str, datetime]] = {
            'blocks': {},
            'transactions': {},
            'addresses': {}
        }
        self.cache_ttl = timedelta(minutes=5)

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the blockchain.

        Args:
            **kwargs: Parameters for the data fetch:
                - block_id: Optional block ID or height to fetch
                - tx_id: Optional transaction ID to fetch
                - address: Optional address to fetch
                - network_status: Whether to fetch network status

        Returns:
            Dictionary of fetched data
        """
        result = {}

        # Fetch block if requested
        block_id = kwargs.get('block_id')
        if block_id:
            if self._is_cached('blocks', block_id):
                result['block'] = self.cache['blocks'][block_id]
            else:
                try:
                    block = await self.client.get_block(block_id)
                    result['block'] = block
                    self._cache_item('blocks', block_id, block)
                except Exception as e:
                    logger.error(f"Error fetching block {block_id}: {str(e)}")

        # Fetch transaction if requested
        tx_id = kwargs.get('tx_id')
        if tx_id:
            if self._is_cached('transactions', tx_id):
                result['transaction'] = self.cache['transactions'][tx_id]
            else:
                try:
                    tx = await self.client.get_transaction(tx_id)
                    result['transaction'] = tx
                    self._cache_item('transactions', tx_id, tx)
                except Exception as e:
                    logger.error(f"Error fetching transaction {tx_id}: {str(e)}")

        # Fetch address if requested
        address = kwargs.get('address')
        if address:
            if self._is_cached('addresses', address):
                result['address'] = self.cache['addresses'][address]
            else:
                try:
                    addr = await self.client.get_address(address)
                    result['address'] = addr
                    self._cache_item('addresses', address, addr)
                except Exception as e:
                    logger.error(f"Error fetching address {address}: {str(e)}")

        # Fetch network status if requested
        if kwargs.get('network_status', False):
            try:
                result['network_status'] = await self.client.get_network_status()
            except Exception as e:
                logger.error(f"Error fetching network status: {str(e)}")

        return result

    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the fetched blockchain data.

        Args:
            data: Raw blockchain data to process

        Returns:
            Processed blockchain data
        """
        processed = {}

        # Process block data if present
        if 'block' in data:
            block = data['block']
            if isinstance(block, Block):
                processed['block'] = {
                    'id': block.id,
                    'height': block.height,
                    'timestamp': block.timestamp.isoformat(),
                    'transactions_count': len(block.transactions),
                    'size': block.size
                }
            else:
                processed['block'] = block

        # Process transaction data if present
        if 'transaction' in data:
            tx = data['transaction']
            if isinstance(tx, Transaction):
                processed['transaction'] = {
                    'id': tx.id,
                    'block_id': tx.block_id,
                    'timestamp': tx.timestamp.isoformat() if tx.timestamp else None,
                    'inputs_count': len(tx.inputs),
                    'outputs_count': len(tx.outputs),
                    'fee': tx.fee
                }
            else:
                processed['transaction'] = tx

        # Process address data if present
        if 'address' in data:
            addr = data['address']
            if isinstance(addr, Address):
                processed['address'] = {
                    'address': addr.address,
                    'balance': addr.balance,
                    'transactions_count': addr.transactions_count
                }
            else:
                processed['address'] = addr

        # Pass through network status
        if 'network_status' in data:
            processed['network_status'] = data['network_status']

        return processed

    def _is_cached(self, cache_type: str, item_id: str) -> bool:
        """
        Check if an item is in the cache and not expired.

        Args:
            cache_type: Type of cache (blocks, transactions, addresses)
            item_id: ID of the item to check

        Returns:
            True if the item is cached and not expired, False otherwise
        """
        if item_id in self.cache[cache_type]:
            expiry = self.cache_expiry[cache_type].get(item_id)
            if expiry and datetime.now() < expiry:
                return True
            # Remove expired item
            if item_id in self.cache[cache_type]:
                del self.cache[cache_type][item_id]
            if item_id in self.cache_expiry[cache_type]:
                del self.cache_expiry[cache_type][item_id]
        return False

    def _cache_item(self, cache_type: str, item_id: str, item: Any) -> None:
        """
        Cache an item.

        Args:
            cache_type: Type of cache (blocks, transactions, addresses)
            item_id: ID of the item to cache
            item: Item to cache
        """
        self.cache[cache_type][item_id] = item
        self.cache_expiry[cache_type][item_id] = datetime.now() + self.cache_ttl
        
        # Limit cache size (keep most recent 1000 items)
        if len(self.cache[cache_type]) > 1000:
            oldest_id = min(self.cache_expiry[cache_type].items(), key=lambda x: x[1])[0]
            del self.cache[cache_type][oldest_id]
            del self.cache_expiry[cache_type][oldest_id]


class BlockchainAnalyzer:
    """
    Utility for analyzing blockchain data.
    
    This class provides methods for analyzing blockchain data and extracting
    insights such as transaction patterns, address activities, etc.
    """

    def __init__(self, client: BlockchainClient):
        """
        Initialize the blockchain analyzer.

        Args:
            client: Blockchain client to use for data access
        """
        self.client = client

    async def analyze_transactions(self, tx_ids: List[str]) -> Dict[str, Any]:
        """
        Analyze a set of transactions.

        Args:
            tx_ids: List of transaction IDs to analyze

        Returns:
            Analysis results
        """
        transactions = []
        for tx_id in tx_ids:
            try:
                tx = await self.client.get_transaction(tx_id)
                transactions.append(tx)
            except Exception as e:
                logger.error(f"Error fetching transaction {tx_id}: {str(e)}")
        
        result = {
            'count': len(transactions),
            'total_fees': sum(tx.fee for tx in transactions if tx.fee is not None),
            'by_size': self._group_by_size(transactions),
            'by_time': self._group_by_time(transactions)
        }
        
        return result

    async def analyze_address(self, address: str, tx_limit: int = 100) -> Dict[str, Any]:
        """
        Analyze an address and its transactions.

        Args:
            address: Address to analyze
            tx_limit: Maximum number of transactions to analyze

        Returns:
            Analysis results
        """
        try:
            addr = await self.client.get_address(address)
            
            # For explorers that support direct transaction fetching
            if hasattr(self.client, 'get_transactions_for_address'):
                transactions = await self.client.get_transactions_for_address(address, limit=tx_limit)
            else:
                # Fallback - this would need to be implemented with additional API calls
                transactions = []
            
            result = {
                'address': address,
                'balance': addr.balance,
                'transactions_count': addr.transactions_count,
                'first_seen': addr.first_seen.isoformat() if addr.first_seen else None,
                'last_seen': addr.last_seen.isoformat() if addr.last_seen else None,
                'transactions_sample': transactions[:tx_limit]
            }
            
            return result
        except Exception as e:
            logger.error(f"Error analyzing address {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e)
            }

    def _group_by_size(self, transactions: List[Transaction]) -> Dict[str, int]:
        """
        Group transactions by size.

        Args:
            transactions: List of transactions to group

        Returns:
            Dictionary mapping size ranges to counts
        """
        size_groups = {
            'small (< 1KB)': 0,
            'medium (1KB - 5KB)': 0,
            'large (> 5KB)': 0
        }
        
        for tx in transactions:
            if tx.size is None:
                continue
            
            if tx.size < 1024:
                size_groups['small (< 1KB)'] += 1
            elif tx.size < 5120:
                size_groups['medium (1KB - 5KB)'] += 1
            else:
                size_groups['large (> 5KB)'] += 1
        
        return size_groups

    def _group_by_time(self, transactions: List[Transaction]) -> Dict[str, int]:
        """
        Group transactions by time.

        Args:
            transactions: List of transactions to group

        Returns:
            Dictionary mapping time ranges to counts
        """
        time_groups = {}
        
        for tx in transactions:
            if tx.timestamp is None:
                continue
            
            hour = tx.timestamp.replace(minute=0, second=0, microsecond=0)
            hour_str = hour.isoformat()
            
            if hour_str not in time_groups:
                time_groups[hour_str] = 0
            
            time_groups[hour_str] += 1
        
        return time_groups 