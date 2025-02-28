#!/usr/bin/env python3
"""
Debug script to investigate API endpoint issues with the Ergo Explorer.
"""

import asyncio
import aiohttp
import json
import sys
import os
import traceback

# The address we want to test
TEST_ADDRESS = "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc"
BASE_URL = "https://api.ergoplatform.com"

async def test_endpoint(url, description):
    """Test an API endpoint and print the result."""
    print(f"\nTesting {description}:")
    print(f"URL: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                status = response.status
                print(f"Status: {status}")
                
                if status == 200:
                    data = await response.json()
                    print(f"Success! Response data:\n{json.dumps(data, indent=2)}")
                    return True
                else:
                    text = await response.text()
                    print(f"Failed with status {status}: {text}")
                    return False
    except Exception as e:
        print(f"Error: {str(e)}")
        traceback.print_exc()
        return False

async def main():
    """Test different API endpoint formats for address information."""
    
    # List of endpoints to test with their descriptions
    endpoints = [
        (f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}", "Standard address endpoint"),
        (f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}/transactions/total", "Transactions total endpoint"),
        (f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}/balance", "Balance endpoint"),
        (f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}/balance/total", "Total balance endpoint"),
        (f"{BASE_URL}/api/v1/addresses/{TEST_ADDRESS}/transactions", "Transactions endpoint")
    ]
    
    success_count = 0
    for url, description in endpoints:
        success = await test_endpoint(url, description)
        if success:
            success_count += 1
    
    print(f"\nTested {len(endpoints)} endpoints, {success_count} succeeded.")
    
    # Also try the network status endpoint to confirm API is working
    await test_endpoint(f"{BASE_URL}/api/v1/info", "Network status endpoint")

if __name__ == "__main__":
    asyncio.run(main()) 