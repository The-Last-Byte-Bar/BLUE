#!/usr/bin/env python3
"""
Test script to directly access the address endpoint with the specific address.
"""

import asyncio
import aiohttp
import json
import traceback

# The address that should exist
TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"

async def test_address_info():
    """Test getting address info directly from the API."""
    print(f"Testing address info for {TEST_ADDRESS}...")
    
    # Try multiple endpoints that might work
    endpoints = [
        f"https://api.ergoplatform.com/api/v0/addresses/{TEST_ADDRESS}",
        f"https://api.ergoplatform.com/api/v1/addresses/{TEST_ADDRESS}",
        f"https://api.ergoplatform.com/api/v1/boxes/byAddress/{TEST_ADDRESS}",
        f"https://api.ergoplatform.com/api/v1/addresses/{TEST_ADDRESS}/balance/confirmed"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in endpoints:
            print(f"\nTrying endpoint: {endpoint}")
            try:
                async with session.get(endpoint) as response:
                    status = response.status
                    print(f"Status: {status}")
                    
                    if status == 200:
                        data = await response.json()
                        print(f"Success! Response:\n{json.dumps(data, indent=2)[:500]}...")
                    else:
                        text = await response.text()
                        print(f"Failed: {text}")
            except Exception as e:
                print(f"Error: {str(e)}")
                traceback.print_exc()
    
    # Now let's try to get just the transactions for this address
    tx_endpoint = f"https://api.ergoplatform.com/api/v1/addresses/{TEST_ADDRESS}/transactions"
    print(f"\nTrying transactions endpoint: {tx_endpoint}")
    try:
        async with session.get(tx_endpoint) as response:
            status = response.status
            print(f"Status: {status}")
            
            if status == 200:
                data = await response.json()
                print(f"Success! Transactions count: {data.get('total', 0)}")
                if data.get('items'):
                    for i, tx in enumerate(data['items'][:3], 1):
                        print(f"Transaction {i} ID: {tx.get('id')}")
            else:
                text = await response.text()
                print(f"Failed: {text}")
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
    
if __name__ == "__main__":
    asyncio.run(test_address_info()) 