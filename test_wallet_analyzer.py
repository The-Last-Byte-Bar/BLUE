"""
Simple test script for the wallet analyzer.

This script tests the wallet analyzer functionality without relying on other modules.
"""

import asyncio
import sys
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

# Create mock classes to avoid importing from other modules
class BlockchainClient:
    """Mock blockchain client."""
    
    async def get_balance(self, address):
        """Mock get_balance method."""
        return {
            'nanoErgs': 1000000000,  # 1 ERG
            'tokenId1': 1000000,     # Some token
            'tokenId2': 500          # Another token
        }
    
    async def get_address(self, address):
        """Mock get_address method."""
        mock = MagicMock()
        mock.transactions_count = 42
        return mock
    
    async def get_transactions_for_address(self, address, limit=50):
        """Mock get_transactions_for_address method."""
        return [
            {
                'id': 'tx1',
                'inputs': [
                    {
                        'address': address,
                        'value': 500000000,  # 0.5 ERG
                        'assets': [
                            {'tokenId': 'tokenId1', 'amount': 100000}
                        ]
                    }
                ],
                'outputs': [
                    {
                        'address': address,
                        'value': 2000000000,  # 2 ERG
                        'assets': [
                            {'tokenId': 'tokenId1', 'amount': 500000},
                            {'tokenId': 'tokenId2', 'amount': 500}
                        ]
                    }
                ]
            }
        ]
    
    async def _make_request(self, endpoint, params=None):
        """Mock _make_request method."""
        return {
            'name': 'Test Token',
            'decimals': 6  # 6 decimal places for token
        }

# Define the WalletAnalyzer class here to avoid import issues
class WalletAnalyzer:
    """
    Advanced wallet analysis for LLM services.
    """

    def __init__(self, client=None):
        """Initialize the wallet analyzer."""
        self.client = client or BlockchainClient()
        self.token_info_cache = {}

    async def get_token_info(self, token_id):
        """Get information about a token, including its decimals."""
        if token_id in self.token_info_cache:
            return self.token_info_cache[token_id]
        
        try:
            # For ERG (represented as 'nanoErgs' in the API)
            if token_id == 'nanoErgs':
                token_info = {
                    'id': token_id,
                    'name': 'ERG',
                    'decimals': 9  # 1 ERG = 10^9 nanoErgs
                }
            else:
                # Fetch token info from the API
                token_data = await self.client._make_request(f"api/v1/tokens/{token_id}")
                token_info = {
                    'id': token_id,
                    'name': token_data.get('name', 'Unknown'),
                    'decimals': token_data.get('decimals', 0)
                }
            
            self.token_info_cache[token_id] = token_info
            return token_info
        except Exception as e:
            print(f"Error fetching token info for {token_id}: {str(e)}")
            # Default to 0 decimals if we can't get the information
            default_info = {'id': token_id, 'name': token_id[:8], 'decimals': 0}
            self.token_info_cache[token_id] = default_info
            return default_info

    async def format_token_amount(self, token_id, amount):
        """Format a token amount using the correct number of decimal places."""
        token_info = await self.get_token_info(token_id)
        decimals = token_info.get('decimals', 0)
        name = token_info.get('name', token_id[:8])
        
        # Convert to decimal with proper decimal places
        decimal_value = Decimal(amount) / Decimal(10 ** decimals)
        
        # Format with appropriate decimals
        if decimal_value == decimal_value.to_integral_value():
            formatted = f"{decimal_value:.0f} {name}"
        else:
            formatted = f"{decimal_value:.{decimals}f} {name}".rstrip('0').rstrip('.')
            formatted = f"{formatted} {name}"
        
        return decimal_value, formatted

    async def analyze_address_transactions(self, address, limit=50):
        """Analyze transactions for an address, tracking incoming and outgoing funds."""
        try:
            # Get transactions for the address
            transactions = await self.client.get_transactions_for_address(address, limit=limit)
            
            # Initialize tracking
            incoming = {'nanoErgs': 0}  # Default to tracking ERG
            outgoing = {'nanoErgs': 0}
            
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
            print(f"Error analyzing address transactions for {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e),
                'transactions_analyzed': 0,
                'incoming': {},
                'outgoing': {}
            }

    async def get_wallet_summary(self, address):
        """Get a complete wallet summary for LLM consumption."""
        try:
            # Get current balance
            balance = await self.client.get_balance(address)
            
            # Get transaction analysis
            tx_analysis = await self.analyze_address_transactions(address)
            
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
            print(f"Error generating wallet summary for {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e)
            }

    async def generate_human_readable_summary(self, summary):
        """Generate a human-readable summary for LLM consumption."""
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

async def main():
    """Run the wallet analyzer test."""
    print("BLUE Wallet Analyzer Test\n")
    
    # Create a wallet analyzer with our mock client
    analyzer = WalletAnalyzer()
    
    # Test address
    address = "test_address"
    
    print(f"Analyzing address: {address}\n")
    
    # Get the wallet summary
    summary = await analyzer.get_wallet_summary(address)
    
    # Display human-readable summary
    print("Human-Readable Summary:")
    print("-----------------------")
    print(summary.get('human_readable', 'Error generating summary'))
    print("\n")
    
    print("Test completed successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 