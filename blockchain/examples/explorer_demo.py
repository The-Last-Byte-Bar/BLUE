"""
Demo script for the Ergo blockchain explorer client.

This script demonstrates how to use the ExplorerClient to interact
with the Ergo blockchain explorer API.
"""

import asyncio
import os
import sys
import json
from pathlib import Path

# Add the parent directory to the path so we can import the blockchain package
sys.path.append(str(Path(__file__).parent.parent.parent))

from blockchain.explorer import ExplorerClient


async def print_json(data):
    """Print data as formatted JSON."""
    print(json.dumps(data, indent=2))


async def demo_address_info(client, address):
    """Demonstrate fetching address information."""
    print("\n=== Address Information ===")
    try:
        address_obj = await client.get_address(address)
        print(f"Address: {address_obj.address}")
        print(f"Transactions count: {address_obj.transactions_count}")
        print(f"First seen: {address_obj.first_seen}")
        print(f"Last seen: {address_obj.last_seen}")
    except Exception as e:
        print(f"Error fetching address info: {e}")


async def demo_address_balance(client, address):
    """Demonstrate fetching address balance."""
    print("\n=== Address Balance ===")
    try:
        balance = await client.get_balance(address)
        print("Tokens:")
        for token_id, amount in balance.items():
            print(f"  {token_id}: {amount}")
            
        # Get total balance including confirmed and unconfirmed
        total_balance = await client.get_address_total_balance(address)
        print("\nTotal Balance:")
        print(f"  Confirmed ERG: {total_balance['confirmed']['nanoErgs'] / 1_000_000_000} ERG")
        if 'unconfirmed' in total_balance:
            print(f"  Unconfirmed ERG: {total_balance['unconfirmed']['nanoErgs'] / 1_000_000_000} ERG")
    except Exception as e:
        print(f"Error fetching balance: {e}")


async def demo_address_transactions(client, address):
    """Demonstrate fetching address transactions."""
    print("\n=== Recent Transactions ===")
    try:
        transactions = await client.get_transactions_for_address(address, limit=5)
        for i, tx in enumerate(transactions, 1):
            print(f"\nTransaction {i}:")
            print(f"  ID: {tx.get('id')}")
            print(f"  Timestamp: {tx.get('timestamp')}")
            print(f"  Confirmations: {tx.get('numConfirmations', 'N/A')}")
    except Exception as e:
        print(f"Error fetching transactions: {e}")


async def demo_unspent_outputs(client, address):
    """Demonstrate fetching unspent outputs."""
    print("\n=== Unspent Outputs (UTXOs) ===")
    try:
        utxos = await client.get_unspent_outputs(address)
        for i, utxo in enumerate(utxos[:3], 1):  # Show only first 3 UTXOs
            print(f"\nUTXO {i}:")
            print(f"  Box ID: {utxo.get('boxId')}")
            print(f"  Value: {utxo.get('value', 0) / 1_000_000_000} ERG")
            
        if len(utxos) > 3:
            print(f"\n... and {len(utxos) - 3} more UTXOs")
        print(f"\nTotal UTXOs: {len(utxos)}")
    except Exception as e:
        print(f"Error fetching UTXOs: {e}")


async def demo_network_status(client):
    """Demonstrate fetching network status."""
    print("\n=== Network Status ===")
    try:
        status = await client.get_network_status()
        print(f"Current Height: {status.get('height')}")
        print(f"Last Block ID: {status.get('lastBlockId')}")
        print(f"Supply: {status.get('supply', 0) / 1_000_000_000} ERG")
    except Exception as e:
        print(f"Error fetching network status: {e}")


async def main():
    """Run the explorer client demo."""
    # Use the address provided in the command line or a default test address
    address = sys.argv[1] if len(sys.argv) > 1 else "9fuTg7RBTi1Rwoa7a6Mx2h61phevUHc87p2P2Xga5SNy3BnVYeD"
    
    print(f"Ergo Explorer API Demo - Address: {address}")
    
    # Create the explorer client (it will use the EXPLORER_API_URL from .env if available)
    async with ExplorerClient() as client:
        await demo_network_status(client)
        await demo_address_info(client, address)
        await demo_address_balance(client, address)
        await demo_address_transactions(client, address)
        await demo_unspent_outputs(client, address)


if __name__ == "__main__":
    asyncio.run(main()) 