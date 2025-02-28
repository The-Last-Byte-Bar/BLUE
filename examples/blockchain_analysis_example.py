"""
Example script demonstrating the LLM interface for blockchain analysis.

This script shows how to use the BlockchainAnalyzer to analyze
blockchain data with language models, including wallet analysis,
transaction analysis, network analysis, and forensic analysis.
"""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
import argparse
from typing import Optional, List

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.client import LLMClientFactory
from llm.analysis import (
    BlockchainAnalyzer,
    analyze_wallet,
    analyze_transaction,
    analyze_network,
    forensic_analysis
)

# Load environment variables
load_dotenv()

# Example Ergo addresses to analyze
EXAMPLE_ADDRESSES = [
    "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",  # Valid address example
]

# Example transaction IDs to analyze
EXAMPLE_TRANSACTIONS = [
    "b29358e110ae76db3f8cbd7296a3323a6bf9b39098e4cd05ea9964e6c1b9a689",  # Example transaction
]

async def run_wallet_analysis(address: str, 
                             question: Optional[str] = None, 
                             llm_provider: str = "claude") -> None:
    """
    Run wallet analysis and display the results.
    
    Args:
        address: Wallet address to analyze
        question: Optional specific question about the wallet
        llm_provider: LLM provider to use
    """
    print(f"\n=== Analyzing wallet: {address} ===\n")
    
    # Create an analyzer with the specified LLM provider
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Analyze the wallet
    result = await analyzer.analyze_wallet(address, question)
    
    # Display the results
    print("Analysis:")
    print("----------")
    print(result.get('analysis', 'No analysis available'))
    print("\n")
    
    # Display metadata
    print("Metadata:")
    print("---------")
    metadata = {
        'address': result.get('address'),
        'context_id': result.get('context_id'),
        'error': result.get('error')
    }
    print(json.dumps(metadata, indent=2))
    print("\n")
    
    # Follow-up question example
    if question is None and llm_provider == "claude":
        print("Follow-up Question Example:")
        print("-------------------------")
        follow_up = "What types of tokens does this wallet hold and what might be their purpose?"
        print(f"Question: {follow_up}\n")
        
        # Use the same context for the follow-up
        follow_up_result = await analyzer.analyze_wallet(
            address, 
            follow_up,
            context_id=result.get('context_id')
        )
        
        print("Analysis:")
        print(follow_up_result.get('analysis', 'No analysis available'))
        print("\n")

async def run_transaction_analysis(tx_id: str,
                                  question: Optional[str] = None,
                                  llm_provider: str = "claude") -> None:
    """
    Run transaction analysis and display the results.
    
    Args:
        tx_id: Transaction ID to analyze
        question: Optional specific question about the transaction
        llm_provider: LLM provider to use
    """
    print(f"\n=== Analyzing transaction: {tx_id} ===\n")
    
    # Create an analyzer with the specified LLM provider
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Analyze the transaction
    result = await analyzer.analyze_transaction(tx_id, question)
    
    # Display the results
    print("Analysis:")
    print("----------")
    print(result.get('analysis', 'No analysis available'))
    print("\n")
    
    # Display metadata
    print("Metadata:")
    print("---------")
    metadata = {
        'transaction_id': result.get('transaction_id'),
        'context_id': result.get('context_id'),
        'error': result.get('error')
    }
    print(json.dumps(metadata, indent=2))
    print("\n")

async def run_network_analysis(metrics: Optional[List[str]] = None,
                              question: Optional[str] = None,
                              llm_provider: str = "claude") -> None:
    """
    Run network analysis and display the results.
    
    Args:
        metrics: Optional list of metrics to include
        question: Optional specific question about the network
        llm_provider: LLM provider to use
    """
    metrics = metrics or ["hashrate", "difficulty", "transaction volume", "active addresses"]
    
    print(f"\n=== Analyzing network metrics: {', '.join(metrics)} ===\n")
    
    # Create an analyzer with the specified LLM provider
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Analyze the network
    result = await analyzer.analyze_network(metrics, question)
    
    # Display the results
    print("Analysis:")
    print("----------")
    print(result.get('analysis', 'No analysis available'))
    print("\n")
    
    # Display metadata
    print("Metadata:")
    print("---------")
    metadata = {
        'metrics': result.get('metrics'),
        'context_id': result.get('context_id'),
        'error': result.get('error')
    }
    print(json.dumps(metadata, indent=2))
    print("\n")

async def run_forensic_analysis(address: str,
                               depth: int = 2,
                               question: Optional[str] = None,
                               llm_provider: str = "claude") -> None:
    """
    Run forensic analysis and display the results.
    
    Args:
        address: Main address to analyze
        depth: How many levels of interaction to analyze
        question: Optional specific question about the relationships
        llm_provider: LLM provider to use
    """
    print(f"\n=== Performing forensic analysis for wallet: {address} (depth: {depth}) ===\n")
    
    # Create an analyzer with the specified LLM provider
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Perform forensic analysis
    result = await analyzer.forensic_analysis(address, depth, question)
    
    # Display the results
    print("Analysis:")
    print("----------")
    print(result.get('analysis', 'No analysis available'))
    print("\n")
    
    # Display metadata
    print("Metadata:")
    print("---------")
    metadata = {
        'address': result.get('address'),
        'depth': result.get('depth'),
        'context_id': result.get('context_id'),
        'error': result.get('error')
    }
    print(json.dumps(metadata, indent=2))
    print("\n")

async def test_llm_providers():
    """Test different LLM providers."""
    # This is a simple test to show how to use different LLM providers
    providers = ["claude", "ollama"]
    
    for provider in providers:
        print(f"\n=== Testing LLM provider: {provider} ===\n")
        
        try:
            # Create a client for the provider
            client = LLMClientFactory.create(provider=provider)
            
            # Test a simple prompt
            response = await client.generate(
                prompt="What is a blockchain?",
                system_prompt="You are a helpful assistant who provides concise, accurate information about blockchain technology."
            )
            
            print("Response:")
            print("---------")
            print(response)
            print("\n")
            
        except Exception as e:
            print(f"Error testing provider {provider}: {str(e)}")

async def main():
    """Run the blockchain analysis examples."""
    parser = argparse.ArgumentParser(description="Run blockchain analysis examples")
    parser.add_argument("--provider", type=str, default="claude", choices=["claude", "ollama"],
                      help="LLM provider to use (claude or ollama)")
    parser.add_argument("--example", type=str, default="all", 
                      choices=["all", "wallet", "transaction", "network", "forensic", "providers"],
                      help="Example to run")
    parser.add_argument("--address", type=str, default=EXAMPLE_ADDRESSES[0],
                      help="Wallet address to analyze")
    parser.add_argument("--transaction", type=str, default=EXAMPLE_TRANSACTIONS[0],
                      help="Transaction ID to analyze")
    parser.add_argument("--depth", type=int, default=2,
                      help="Depth for forensic analysis")
    parser.add_argument("--question", type=str, default=None,
                      help="Specific question to ask")
    
    args = parser.parse_args()
    
    print("BLUE Blockchain Analysis Examples\n")
    
    # Check for required environment variables
    if args.provider == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set.")
        print("Set this in your .env file or in your environment to use Claude.")
        print("Falling back to Ollama...")
        args.provider = "ollama"
    
    # Run the selected example(s)
    if args.example in ["all", "wallet"]:
        await run_wallet_analysis(args.address, args.question, args.provider)
        
    if args.example in ["all", "transaction"]:
        await run_transaction_analysis(args.transaction, args.question, args.provider)
        
    if args.example in ["all", "network"]:
        await run_network_analysis(None, args.question, args.provider)
        
    if args.example in ["all", "forensic"]:
        await run_forensic_analysis(args.address, args.depth, args.question, args.provider)
        
    if args.example in ["all", "providers"]:
        await test_llm_providers()

if __name__ == "__main__":
    asyncio.run(main()) 