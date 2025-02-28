#!/usr/bin/env python3
"""
Simple test script to verify that the Ergo API endpoints are working correctly.
This script bypasses the ExplorerClient and uses aiohttp directly.
"""

import asyncio
import aiohttp
import json

# Test address from mainnet
TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
BASE_URL = "https://api.ergoplatform.com"

async def test_endpoints():
    """Test the Ergo API endpoints directly."""
    try:
        async with aiohttp.ClientSession() as session:
            print(f"Testing address: {TEST_ADDRESS}")
            
            # Test the v0 address endpoint
            v0_address_url = f"{BASE_URL}/api/v0/addresses/{TEST_ADDRESS}"
            print(f"\n1. Testing endpoint: {v0_address_url}")
            async with session.get(v0_address_url) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    tx_count = data.get('transactions', {}).get('confirmed', 0)
                    print(f"Transaction count: {tx_count}")
                else:
                    print(f"Error: {await response.text()}")
            
            # Test the v1 balance/confirmed endpoint
            balance_url = f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}/balance/confirmed"
            print(f"\n2. Testing endpoint: {balance_url}")
            async with session.get(balance_url) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    balance = data.get('nanoErgs', 0)
                    token_count = len(data.get('tokens', []))
                    print(f"Balance (nanoErgs): {balance}")
                    print(f"Number of tokens: {token_count}")
                else:
                    print(f"Error: {await response.text()}")
                
            print("\nAll tests completed!")
    
    except Exception as e:
        print(f"Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_endpoints()) 