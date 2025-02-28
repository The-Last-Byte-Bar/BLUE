#!/usr/bin/env python3
"""
Test script to verify the updated ExplorerClient implementation.
"""

import asyncio
import sys
import os

# Add the parent directory to sys.path to allow direct imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.explorer import ExplorerClient

# Test address from mainnet
TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"

async def test_explorer_client():
    """Test the ExplorerClient with our updated implementation."""
    try:
        async with ExplorerClient() as client:
            print(f"Testing address: {TEST_ADDRESS}")
            
            # Test get_address method
            print("\n1. Testing get_address method...")
            address = await client.get_address(TEST_ADDRESS)
            print(f"Address: {address.address}")
            print(f"Transaction count: {address.transactions_count}")
            
            # Test get_balance method
            print("\n2. Testing get_balance method...")
            balance = await client.get_balance(TEST_ADDRESS)
            print(f"Balance (nanoErgs): {balance.get('nanoErgs', 0)}")
            print(f"Number of tokens: {len(balance) - 1}")  # -1 for nanoErgs
            
            # Test get_transactions_for_address method
            print("\n3. Testing get_transactions_for_address method...")
            txs = await client.get_transactions_for_address(TEST_ADDRESS, limit=3)
            print(f"Retrieved {len(txs)} transactions")
            for i, tx in enumerate(txs[:3], 1):
                print(f"  Transaction {i} ID: {tx.get('id')}")
            
            # Test get_unspent_outputs method
            print("\n4. Testing get_unspent_outputs method...")
            utxos = await client.get_unspent_outputs(TEST_ADDRESS)
            print(f"Retrieved {len(utxos)} UTXOs")
            for i, utxo in enumerate(utxos[:3], 1):
                print(f"  UTXO {i} ID: {utxo.get('boxId')}")
                print(f"  UTXO {i} Value: {utxo.get('value')} nanoErgs")
                
            print("\nAll tests completed successfully!")
    
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_explorer_client()) 