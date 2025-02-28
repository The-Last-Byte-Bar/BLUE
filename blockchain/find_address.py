#!/usr/bin/env python3
"""
Script to find valid addresses from recent transactions.
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the path so we can import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.explorer import ExplorerClient

async def find_valid_addresses():
    """Find valid addresses from recent transactions."""
    async with ExplorerClient() as client:
        # Get latest block
        network_info = await client.get_network_status()
        latest_block_id = network_info.get("lastBlockId")
        print(f"Latest block ID: {latest_block_id}")
        
        # Get block details
        block = await client.get_block(latest_block_id)
        print(f"Block height: {block.height}")
        print(f"Transactions count: {len(block.transactions)}")
        
        # Get transaction details for a few transactions
        addresses = set()
        for i, tx_id in enumerate(block.transactions[:3]):
            print(f"\nFetching transaction {i+1}: {tx_id}")
            try:
                tx = await client.get_transaction(tx_id)
                
                # Extract addresses from inputs and outputs
                for inp in tx.inputs:
                    if 'address' in inp:
                        addresses.add(inp['address'])
                
                for out in tx.outputs:
                    if 'address' in out:
                        addresses.add(out['address'])
                
                print(f"Found {len(addresses)} addresses so far")
            except Exception as e:
                print(f"Error getting transaction: {str(e)}")
        
        # Print found addresses
        print("\nFound addresses:")
        for i, addr in enumerate(list(addresses)[:5], 1):
            print(f"Address {i}: {addr}")
            
            # Test if we can get address details
            try:
                address_obj = await client.get_address(addr)
                print(f"  - Valid! Transactions count: {address_obj.transactions_count}")
            except Exception as e:
                print(f"  - Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(find_valid_addresses()) 