"""
Wallet analyzer for blockchain data.

This module provides advanced wallet analysis capabilities for LLM services,
including tracking total incoming and outgoing funds, token balances,
and properly formatted values with correct decimal places.
"""

import asyncio
import logging
import re
from typing import Dict, Any, List, Optional, Tuple
from decimal import Decimal

from blockchain.client import BlockchainClient
from blockchain.explorer import ExplorerClient
from data.blockchain_data import BlockchainDataHandler

logger = logging.getLogger(__name__)

# Constants
NANO_ERG_DECIMALS = 9  # 1 ERG = 10^9 nanoErgs

class WalletAnalyzer:
    """
    Advanced wallet analysis for LLM services.
    
    This class provides methods to analyze wallet activities including:
    - Tracking total incoming and outgoing funds
    - Token balances with proper decimal formatting
    - Transaction history analysis
    - Human-readable summaries for LLM consumption
    """

    def __init__(self, client: BlockchainClient = None):
        """
        Initialize the wallet analyzer.

        Args:
            client: Blockchain client to use for data access (defaults to ExplorerClient)
        """
        self.client = client or ExplorerClient()
        self.token_info_cache: Dict[str, Dict[str, Any]] = {}

    def is_valid_address(self, address: str) -> bool:
        """
        Validate an Ergo address format.
        
        Args:
            address: The address to validate
            
        Returns:
            True if the address format appears valid, False otherwise
        """
        # Basic validation for Ergo addresses
        # Most Ergo addresses are 51-58 characters in length and start with 9
        if not address or not isinstance(address, str):
            return False
            
        # Check if address has the correct format (simple regex check)
        # This is a basic check - a more comprehensive validation would require the actual checksum algorithm
        if not re.match(r'^[1-9A-HJ-NP-Za-km-z]{51,60}$', address):
            return False
            
        return True

    async def get_token_info(self, token_id: str) -> Dict[str, Any]:
        """
        Get information about a token, including its decimals.

        Args:
            token_id: Token ID

        Returns:
            Token information including name, decimals, etc.
        """
        if token_id in self.token_info_cache:
            return self.token_info_cache[token_id]
        
        try:
            # For ERG (represented as 'nanoErgs' in the API)
            if token_id == 'nanoErgs':
                token_info = {
                    'id': token_id,
                    'name': 'ERG',
                    'decimals': NANO_ERG_DECIMALS
                }
            else:
                # Fetch token info from the API
                # Note: This is a placeholder - implement actual token info fetching based on your API
                token_data = await self._make_request(f"api/v1/tokens/{token_id}")
                token_info = {
                    'id': token_id,
                    'name': token_data.get('name', 'Unknown'),
                    'decimals': token_data.get('decimals', 0)
                }
            
            self.token_info_cache[token_id] = token_info
            return token_info
        except Exception as e:
            logger.error(f"Error fetching token info for {token_id}: {str(e)}")
            # Default to 0 decimals if we can't get the information
            default_info = {'id': token_id, 'name': token_id[:8], 'decimals': 0}
            self.token_info_cache[token_id] = default_info
            return default_info

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the blockchain API.
        
        Args:
            endpoint: API endpoint
            params: Optional query parameters
            
        Returns:
            Response data as a dictionary
        """
        if hasattr(self.client, '_make_request'):
            return await self.client._make_request(endpoint, params)
        raise NotImplementedError("Client doesn't support direct API requests")

    async def format_token_amount(self, token_id: str, amount: int) -> Tuple[Decimal, str]:
        """
        Format a token amount using the correct number of decimal places.
        
        Args:
            token_id: Token ID
            amount: Raw token amount
            
        Returns:
            Tuple of (Decimal value, formatted string with symbol)
        """
        try:
            token_info = await self.get_token_info(token_id)
            decimals = token_info.get('decimals', 0)
            name = token_info.get('name', token_id[:8])
            
            # Ensure decimals is an integer
            if decimals is None:
                logger.warning(f"Token {token_id} has None decimals, defaulting to 0")
                decimals = 0
            
            # Convert to decimal with proper decimal places
            decimal_value = Decimal(amount) / Decimal(10 ** decimals)
            
            # Format with appropriate decimals
            if decimal_value == decimal_value.to_integral_value():
                formatted = f"{decimal_value:.0f} {name}"
            else:
                formatted = f"{decimal_value:.{decimals}f} {name}".rstrip('0').rstrip('.')
                formatted = f"{formatted} {name}"
            
            return decimal_value, formatted
        except Exception as e:
            logger.error(f"Error formatting token amount for {token_id}: {str(e)}")
            # Return a safe default if we encounter any error
            return Decimal(amount), f"{amount} {token_id[:8]}"

    async def analyze_address_transactions(self, address: str, limit: int = 50) -> Dict[str, Any]:
        """
        Analyze transactions for an address, tracking incoming and outgoing funds.
        
        Args:
            address: Blockchain address
            limit: Maximum number of transactions to analyze
            
        Returns:
            Analysis results with incoming/outgoing funds and tokens
        """
        try:
            # Validate address first
            if not self.is_valid_address(address):
                return {
                    'address': address,
                    'error': "Invalid address format",
                    'transactions_analyzed': 0,
                    'incoming': {},
                    'outgoing': {}
                }
            
            # Get transactions for the address
            transactions = await self.client.get_transactions_for_address(address, limit=limit)
            
            # Initialize tracking
            incoming: Dict[str, int] = {'nanoErgs': 0}  # Default to tracking ERG
            outgoing: Dict[str, int] = {'nanoErgs': 0}
            
            # Process each transaction
            for tx_data in transactions:
                tx_id = tx_data.get('id')
                inputs = tx_data.get('inputs', [])
                outputs = tx_data.get('outputs', [])
                
                # Analyze inputs (outgoing)
                for input_data in inputs:
                    input_address = input_data.get('address')
                    if input_address == address:
                        # This is an outgoing transaction from our address
                        value = input_data.get('value', 0)
                        outgoing['nanoErgs'] += value
                        
                        # Track tokens
                        assets = input_data.get('assets', [])
                        for asset in assets:
                            token_id = asset.get('tokenId')
                            amount = asset.get('amount', 0)
                            if token_id not in outgoing:
                                outgoing[token_id] = 0
                            outgoing[token_id] += amount
                
                # Analyze outputs (incoming)
                for output_data in outputs:
                    output_address = output_data.get('address')
                    if output_address == address:
                        # This is an incoming transaction to our address
                        value = output_data.get('value', 0)
                        incoming['nanoErgs'] += value
                        
                        # Track tokens
                        assets = output_data.get('assets', [])
                        for asset in assets:
                            token_id = asset.get('tokenId')
                            amount = asset.get('amount', 0)
                            if token_id not in incoming:
                                incoming[token_id] = 0
                            incoming[token_id] += amount
            
            # Format the results with proper decimal places
            formatted_incoming = {}
            formatted_outgoing = {}
            
            # Process ERG and tokens
            for token_id, amount in incoming.items():
                _, formatted = await self.format_token_amount(token_id, amount)
                formatted_incoming[token_id] = {
                    'raw_amount': amount,
                    'formatted': formatted
                }
            
            for token_id, amount in outgoing.items():
                _, formatted = await self.format_token_amount(token_id, amount)
                formatted_outgoing[token_id] = {
                    'raw_amount': amount,
                    'formatted': formatted
                }
            
            return {
                'address': address,
                'transactions_analyzed': len(transactions),
                'incoming': formatted_incoming,
                'outgoing': formatted_outgoing,
                'net': {
                    'nanoErgs': incoming.get('nanoErgs', 0) - outgoing.get('nanoErgs', 0)
                }
            }
        
        except Exception as e:
            logger.error(f"Error analyzing address transactions for {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e),
                'transactions_analyzed': 0,
                'incoming': {},
                'outgoing': {}
            }

    async def get_wallet_summary(self, address: str) -> Dict[str, Any]:
        """
        Get a complete wallet summary for LLM consumption.
        
        Args:
            address: Blockchain address
            
        Returns:
            Complete wallet summary with balance, transaction history, and analysis
        """
        try:
            # Validate address first
            if not self.is_valid_address(address):
                error_msg = f"Invalid address format: {address}"
                logger.error(error_msg)
                return {
                    'address': address,
                    'error': error_msg,
                    'human_readable': f"Error: {error_msg}"
                }
            
            # Get current balance
            balance = await self.client.get_balance(address)
            
            # Get transaction analysis
            tx_analysis = await self.analyze_address_transactions(address)
            
            # Check if there was an error in transaction analysis
            if 'error' in tx_analysis and tx_analysis.get('transactions_analyzed', 0) == 0:
                error_msg = tx_analysis.get('error', 'Unknown error in transaction analysis')
                return {
                    'address': address,
                    'error': error_msg,
                    'human_readable': f"Error analyzing transactions: {error_msg}"
                }
            
            # Format current balance
            formatted_balance = {}
            for token_id, amount in balance.items():
                _, formatted = await self.format_token_amount(token_id, amount)
                formatted_balance[token_id] = {
                    'raw_amount': amount,
                    'formatted': formatted
                }
            
            # Get transaction count
            address_data = await self.client.get_address(address)
            tx_count = getattr(address_data, 'transactions_count', 0)
            
            # Create the summary
            summary = {
                'address': address,
                'current_balance': formatted_balance,
                'transaction_count': tx_count,
                'analysis': {
                    'incoming': tx_analysis['incoming'],
                    'outgoing': tx_analysis['outgoing'],
                }
            }
            
            # Generate a human-readable summary for LLM consumption
            human_summary = await self.generate_human_readable_summary(summary)
            summary['human_readable'] = human_summary
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating wallet summary for {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e),
                'human_readable': f"Error generating summary: {str(e)}"
            }

    async def generate_human_readable_summary(self, summary: Dict[str, Any]) -> str:
        """
        Generate a human-readable summary for LLM consumption.
        
        Args:
            summary: Wallet summary data
            
        Returns:
            Human-readable summary text
        """
        address = summary.get('address', 'Unknown')
        balance = summary.get('current_balance', {})
        tx_count = summary.get('transaction_count', 0)
        
        # Start with balance information
        lines = [
            f"Wallet Address: {address}",
            f"Total Transactions: {tx_count}",
            "\nCurrent Balance:"
        ]
        
        # Add each token balance
        for token_id, data in balance.items():
            formatted = data.get('formatted', f"{data.get('raw_amount', 0)} (Unknown token)")
            if token_id == 'nanoErgs':
                lines.append(f"  • {formatted} (native currency)")
            else:
                # Could add more details about the token if available
                lines.append(f"  • {formatted}")
        
        # Add transaction analysis
        if 'analysis' in summary:
            incoming = summary['analysis'].get('incoming', {})
            outgoing = summary['analysis'].get('outgoing', {})
            
            lines.append("\nTransaction Analysis (recent transactions):")
            
            if incoming:
                lines.append("\nIncoming:")
                for token_id, data in incoming.items():
                    formatted = data.get('formatted', f"{data.get('raw_amount', 0)} (Unknown token)")
                    if token_id == 'nanoErgs':
                        lines.append(f"  • {formatted} received")
                    else:
                        lines.append(f"  • {formatted} received")
            
            if outgoing:
                lines.append("\nOutgoing:")
                for token_id, data in outgoing.items():
                    formatted = data.get('formatted', f"{data.get('raw_amount', 0)} (Unknown token)")
                    if token_id == 'nanoErgs':
                        lines.append(f"  • {formatted} sent")
                    else:
                        lines.append(f"  • {formatted} sent")
        
        return "\n".join(lines)

async def get_wallet_analysis_for_llm(address: str) -> Dict[str, Any]:
    """
    Get wallet analysis formatted for LLM consumption.
    
    This is the main entry point for LLM services to get wallet information.
    
    Args:
        address: Blockchain address
        
    Returns:
        Analysis data formatted for LLM use
    """
    client = ExplorerClient()
    analyzer = WalletAnalyzer(client)
    
    # Validate address before proceeding
    if not analyzer.is_valid_address(address):
        return {
            'wallet_summary': {
                'address': address,
                'error': "Invalid address format"
            },
            'human_readable': f"Error: Invalid address format - {address}"
        }
    
    try:
        async with client:
            summary = await analyzer.get_wallet_summary(address)
        
        return {
            'wallet_summary': summary,
            'human_readable': summary.get('human_readable', '')
        }
    except Exception as e:
        error_msg = f"Error in wallet analysis: {str(e)}"
        logger.error(error_msg)
        return {
            'wallet_summary': {
                'address': address,
                'error': error_msg
            },
            'human_readable': f"Error: {error_msg}"
        } 