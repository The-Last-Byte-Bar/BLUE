# Blockchain Module

The blockchain module provides a set of tools for interacting with the Ergo blockchain through various APIs, including Explorer APIs and Node APIs.

## Components

- **ExplorerClient**: Client for interacting with the Ergo Explorer API (https://api.ergoplatform.com)
- **NodeClient**: Client for interacting with the Ergo Node API
- **Models**: Data models for representing blockchain entities like blocks, transactions, and addresses

## Configuration

Configuration is done through environment variables, which can be loaded from a `.env` file:

```
# Explorer API configuration
EXPLORER_API_URL=https://api.ergoplatform.com
EXPLORER_API_KEY=your_api_key_if_needed

# Node API configuration
NODE_API_URL=http://localhost:9053
NODE_API_KEY=your_node_api_key
```

## Usage Examples

### Using the Explorer Client

```python
import asyncio
from blockchain.explorer import ExplorerClient

async def main():
    # Create an explorer client (will use EXPLORER_API_URL from .env if available)
    async with ExplorerClient() as client:
        # Get information about an address
        address = "9fuTg7RBTi1Rwoa7a6Mx2h61phevUHc87p2P2Xga5SNy3BnVYeD"
        address_info = await client.get_address(address)
        
        # Get address transactions
        txs = await client.get_transactions_for_address(address, limit=10)
        
        # Get address total balance
        balance = await client.get_address_total_balance(address)
        
        # Get unspent outputs (UTXOs)
        utxos = await client.get_unspent_outputs(address)
        
        # Get network status
        status = await client.get_network_status()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using the Node Client

```python
import asyncio
from blockchain.node import NodeClient

async def main():
    # Create a node client (will use NODE_API_URL from .env if available)
    async with NodeClient() as client:
        # Get node info
        info = await client.get_info()
        
        # Get blockchain height
        height = await client.get_height()
        
        # Submit a transaction
        tx_id = await client.submit_transaction(tx_data)

if __name__ == "__main__":
    asyncio.run(main())
```

## Running the Demo

```bash
# Run with default address
python -m blockchain.examples.explorer_demo

# Run with custom address
python -m blockchain.examples.explorer_demo 9fuTg7RBTi1Rwoa7a6Mx2h61phevUHc87p2P2Xga5SNy3BnVYeD
```

## Running Tests

```bash
# Run all tests
pytest blockchain/tests/

# Run specific test
pytest blockchain/tests/test_explorer.py
```

# BLUE Blockchain Layer

This directory contains the blockchain integration layer for the BLUE (Blockchain Language Understanding Engine) project.

## Components

The blockchain layer is composed of the following components:

### Core Models

- `models.py`: Data models for blockchain entities (Block, Transaction, Address)
- `factory.py`: Factory patterns for creating blockchain entities

### API Clients

- `client.py`: Base blockchain client interface
- `node.py`: Client for direct blockchain node interaction
- `explorer.py`: Client for blockchain explorer API interaction

### Examples and Tests

The `examples/` and `tests/` directories contain example usage and test cases for the blockchain layer.

## Wallet Analysis

The blockchain layer provides data for wallet analysis through the `WalletAnalyzer` class in `data/wallet_analyzer.py`. This component:

- Tracks total incoming and outgoing funds for wallets
- Processes token balances with correct decimal formatting
- Converts raw blockchain data into human-readable formats
- Provides data in formats suitable for LLM consumption

## LLM Integration

The wallet data can be integrated with language models through the `wallet_insights.py` module in the `llm/` directory, which:

- Formats wallet data into LLM-friendly prompts
- Enables natural language questions about wallets
- Provides insights and explanations about wallet activity
- Translates technical blockchain data into user-friendly information

## Example Usage

### Basic Blockchain Data Access

```python
from blockchain.explorer import ExplorerClient

async def get_address_data(address):
    client = ExplorerClient()
    async with client:
        # Get basic address information
        address_data = await client.get_address(address)
        
        # Get balance information
        balance = await client.get_balance(address)
        
        # Get transactions
        transactions = await client.get_transactions_for_address(address, limit=10)
    
    return {
        'address': address_data,
        'balance': balance,
        'transactions': transactions
    }
```

### Wallet Analysis

```python
from data.wallet_analyzer import WalletAnalyzer

async def analyze_wallet(address):
    analyzer = WalletAnalyzer()
    summary = await analyzer.get_wallet_summary(address)
    return summary
```

### LLM Integration

```python
from llm.wallet_insights import answer_wallet_question

async def ask_about_wallet(address, question):
    response = await answer_wallet_question(address, question)
    return response.get('insights')
```

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set environment variables:
   - `EXPLORER_API_URL`: URL of the blockchain explorer API (default: https://api.ergoplatform.com)
   - `EXPLORER_API_KEY`: Optional API key for the explorer
   - `NODE_URL`: URL of the blockchain node (if using direct node access)
   - `NODE_API_KEY`: Optional API key for the node

## Additional Resources

- Full documentation in the `docs/` directory
- Example scripts in the `examples/` directory
- Test suite in the `tests/` directory 