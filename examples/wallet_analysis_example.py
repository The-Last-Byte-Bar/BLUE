"""
Example script demonstrating wallet analysis for LLM services.

This script shows how to use the WalletAnalyzer to get wallet information
and format it for consumption by language models.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.wallet_analyzer import WalletAnalyzer, get_wallet_analysis_for_llm
from blockchain.explorer import ExplorerClient

# Load environment variables
load_dotenv()

# Example Ergo addresses to analyze
EXAMPLE_ADDRESSES = [
    "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",  # Valid address example
    # The following addresses have known issues and are kept for reference
    # "9hY16vzHmmfyVBwKeFGHvb2bMFsG94A1u7MxLR3MkKYKDzwCEVg",  # Fails checksum validation
    # "9fMPy1XY3GW4T6t3LjYofqmzER6x9cV21n5UVJTWmma4Y9mAW6c"   # Had issues with token decimals
]

async def main():
    """Run the wallet analysis example."""
    print("BLUE Wallet Analysis Example\n")
    print("Analyzing Ergo addresses for LLM consumption...\n")
    
    # Create an explorer client
    client = ExplorerClient()
    
    # Use the client with context manager to ensure proper cleanup
    async with client:
        # Create a wallet analyzer
        analyzer = WalletAnalyzer(client)
        
        # Analyze each example address
        for address in EXAMPLE_ADDRESSES:
            print(f"== Analyzing address: {address} ==\n")
            
            # Get the wallet summary
            summary = await analyzer.get_wallet_summary(address)
            
            # Display human-readable summary
            print("Human-Readable Summary (for LLM):")
            print("---------------------------------")
            print(summary.get('human_readable', 'Error generating summary'))
            print("\n")
            
            # Display the JSON data (useful for developers)
            print("JSON Data (for API/development):")
            print("--------------------------------")
            # Print a limited version for readability
            simplified = {
                'address': summary.get('address'),
                'transaction_count': summary.get('transaction_count'),
                'balance_example': next(iter(summary.get('current_balance', {}).items()), None),
                '...': '(additional data available in the full summary)'
            }
            print(json.dumps(simplified, indent=2))
            print("\n")
            
            # Demonstrate how this would be used with an LLM
            print("LLM Integration Example:")
            print("-----------------------")
            print("The human-readable summary would be sent to the LLM with a prompt like:")
            print("'Here is information about a blockchain wallet. Please analyze it and provide insights.'")
            print("\n")
            
            # Pause between addresses for readability
            if address != EXAMPLE_ADDRESSES[-1]:
                print("Press Enter to analyze the next address...")
                input()
                print("\n")

if __name__ == "__main__":
    asyncio.run(main()) 