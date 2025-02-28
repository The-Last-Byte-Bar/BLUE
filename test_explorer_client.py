#!/usr/bin/env python3
"""
Simple test script for the Ergo Explorer client.
"""

import asyncio
import json

from blockchain.explorer import ExplorerClient

TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"


async def test_get_network_status():
    """Test getting network status."""
    print("Testing get_network_status...")
    async with ExplorerClient() as client:
        status = await client.get_network_status()
        print(json.dumps(status, indent=2))
        return "Success" if status else "Failed"


async def test_get_address():
    """Test getting address information."""
    print(f"Testing get_address for {TEST_ADDRESS}...")
    async with ExplorerClient() as client:
        address = await client.get_address(TEST_ADDRESS)
        print(f"Address: {address.address}")
        print(f"Transactions count: {address.transactions_count}")
        return "Success" if address else "Failed"


async def test_get_balance():
    """Test getting address balance."""
    print(f"Testing get_balance for {TEST_ADDRESS}...")
    async with ExplorerClient() as client:
        balance = await client.get_balance(TEST_ADDRESS)
        print(json.dumps(balance, indent=2))
        return "Success" if isinstance(balance, dict) else "Failed"


async def test_get_total_balance():
    """Test getting total address balance."""
    print(f"Testing get_address_total_balance for {TEST_ADDRESS}...")
    async with ExplorerClient() as client:
        total_balance = await client.get_address_total_balance(TEST_ADDRESS)
        print(json.dumps(total_balance, indent=2))
        return "Success" if isinstance(total_balance, dict) else "Failed"


async def test_get_transactions():
    """Test getting address transactions."""
    print(f"Testing get_transactions_for_address for {TEST_ADDRESS}...")
    async with ExplorerClient() as client:
        txs = await client.get_transactions_for_address(TEST_ADDRESS, limit=3)
        for i, tx in enumerate(txs, 1):
            print(f"Transaction {i}: {tx.get('id')}")
        return "Success" if isinstance(txs, list) else "Failed"


async def main():
    """Run all tests."""
    tests = [
        test_get_network_status,
        test_get_address,
        test_get_balance,
        test_get_total_balance,
        test_get_transactions
    ]
    
    results = {}
    for test in tests:
        try:
            result = await test()
            results[test.__name__] = result
        except Exception as e:
            results[test.__name__] = f"Error: {str(e)}"
        
        print("\n---\n")
    
    print("Test Results:")
    for test_name, result in results.items():
        print(f"{test_name}: {result}")


if __name__ == "__main__":
    asyncio.run(main()) 