#!/usr/bin/env python3
"""
Test script for fetching network status and finding valid addresses.
"""

import asyncio
import json
import sys
import os

# Add the parent directory to the path so we can import blockchain modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from blockchain.explorer import ExplorerClient

async def test_network_status():
    """Test getting network status."""
    print("Testing get_network_status...")
    async with ExplorerClient() as client:
        status = await client.get_network_status()
        print(json.dumps(status, indent=2))
        return "Success" if status else "Failed"

async def get_rich_addresses():
    """Get some rich addresses that should be valid."""
    print("Fetching rich list to find valid addresses...")
    async with ExplorerClient() as client:
        try:
            rich_list = await client.get_rich_list(limit=5)
            for i, addr_data in enumerate(rich_list, 1):
                addr = addr_data.get('address')
                balance = addr_data.get('balance', {}).get('confirmed', 0)
                print(f"Address {i}: {addr} - Balance: {balance}")
            return rich_list
        except Exception as e:
            print(f"Error fetching rich list: {str(e)}")
            return []

if __name__ == "__main__":
    print("Running network tests...\n")
    asyncio.run(test_network_status())
    print("\n---\n")
    asyncio.run(get_rich_addresses()) 