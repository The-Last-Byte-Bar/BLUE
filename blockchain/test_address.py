#!/usr/bin/env python3
"""
Simple test script for the get_address method in the Explorer client.
"""

import asyncio
import json
import sys
import os
import traceback

# Add the parent directory to the path so we can import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.explorer import ExplorerClient

TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"

async def test_get_address():
    """Test getting address information."""
    print(f"Testing get_address for {TEST_ADDRESS}...")
    try:
        async with ExplorerClient(base_url="https://api.ergoplatform.com") as client:
            address = await client.get_address(TEST_ADDRESS)
            print(f"Address: {address.address}")
            print(f"Transactions count: {address.transactions_count}")
            return "Success" if address else "Failed"
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return f"Error: {str(e)}"

if __name__ == "__main__":
    result = asyncio.run(test_get_address())
    print(f"\nTest result: {result}") 