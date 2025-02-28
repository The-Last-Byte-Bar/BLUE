#!/usr/bin/env python3
"""
Simple test script for the get_address method in the Explorer client.
"""

import asyncio
import json
from blockchain.explorer import ExplorerClient

TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"

async def test_get_address():
    """Test getting address information."""
    print(f"Testing get_address for {TEST_ADDRESS}...")
    try:
        async with ExplorerClient() as client:
            address = await client.get_address(TEST_ADDRESS)
            print(f"Address: {address.address}")
            print(f"Transactions count: {address.transactions_count}")
            return "Success" if address else "Failed"
    except Exception as e:
        print(f"Error: {str(e)}")
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = asyncio.run(test_get_address())
    print(f"\nTest result: {result}") 