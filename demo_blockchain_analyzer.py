#!/usr/bin/env python3
"""
Blockchain Analysis Demo Script

This script demonstrates the blockchain analysis functionality using LLM integration.
It allows users to analyze a wallet address, a transaction, or network metrics.
"""

import asyncio
import argparse
import logging
import json
import sys
from typing import Optional
from datetime import datetime

from llm.analysis import (
    analyze_wallet, 
    analyze_transaction, 
    analyze_network, 
    forensic_analysis
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_wallet_analysis(address: str, question: Optional[str] = None, provider: str = "claude"):
    """Run a wallet analysis demonstration."""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING WALLET: {address}")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Fetching wallet data and generating analysis...")
    
    try:
        result = await analyze_wallet(address, question, llm_provider=provider)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
            return
        
        print("\nWALLET DATA SUMMARY:")
        if "wallet_data" in result and "human_readable" in result["wallet_data"]:
            print(result["wallet_data"]["human_readable"])
        else:
            print("No human-readable summary available")
            
        print("\nLLM ANALYSIS:")
        print(result["analysis"])
        
        print(f"\nContext ID for further questions: {result['context_id']}")
        
    except Exception as e:
        logger.error(f"Error in wallet analysis demo: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")

async def demo_transaction_analysis(tx_id: str, question: Optional[str] = None, provider: str = "claude"):
    """Run a transaction analysis demonstration."""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING TRANSACTION: {tx_id}")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Analyzing transaction...")
    
    try:
        result = await analyze_transaction(tx_id, question, llm_provider=provider)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
            return
            
        print("\nLLM ANALYSIS:")
        print(result["analysis"])
        
        print(f"\nContext ID for further questions: {result['context_id']}")
        
    except Exception as e:
        logger.error(f"Error in transaction analysis demo: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")

async def demo_network_analysis(metrics: Optional[list] = None, question: Optional[str] = None, provider: str = "claude"):
    """Run a network analysis demonstration."""
    metrics = metrics or ["hashrate", "difficulty", "transactionVolume"]
    
    print(f"\n{'=' * 80}")
    print(f"ANALYZING NETWORK METRICS: {', '.join(metrics)}")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Analyzing network metrics...")
    
    try:
        result = await analyze_network(metrics, question, llm_provider=provider)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
            return
            
        print("\nLLM ANALYSIS:")
        print(result["analysis"])
        
        print(f"\nContext ID for further questions: {result['context_id']}")
        
    except Exception as e:
        logger.error(f"Error in network analysis demo: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")

async def demo_forensic_analysis(address: str, depth: int = 2, question: Optional[str] = None, provider: str = "claude"):
    """Run a forensic analysis demonstration."""
    print(f"\n{'=' * 80}")
    print(f"FORENSIC ANALYSIS OF WALLET: {address} (Depth: {depth})")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Running forensic analysis...")
    
    try:
        result = await forensic_analysis(address, depth, question, llm_provider=provider)
        
        if "error" in result:
            print(f"\nError: {result['error']}")
            return
            
        print("\nLLM ANALYSIS:")
        print(result["analysis"])
        
        print(f"\nContext ID for further questions: {result['context_id']}")
        
    except Exception as e:
        logger.error(f"Error in forensic analysis demo: {str(e)}")
        print(f"\nAn error occurred: {str(e)}")

async def interactive_session(initial_address: Optional[str] = None, provider: str = "claude"):
    """Run an interactive analysis session."""
    print(f"\n{'=' * 80}")
    print(f"INTERACTIVE BLOCKCHAIN ANALYSIS SESSION")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Type 'exit' or 'quit' to end the session")
    
    # State variables for the session
    context_id = None
    current_address = initial_address
    
    while True:
        print("\n" + "-" * 40)
        
        if not current_address:
            current_address = input("Enter a wallet address (or 'exit' to quit): ")
            if current_address.lower() in ["exit", "quit"]:
                break
            print()
        
        question = input("What would you like to know about this wallet? (or 'change' for a different address, 'exit' to quit): ")
        if question.lower() in ["exit", "quit"]:
            break
        elif question.lower() == "change":
            current_address = None
            context_id = None
            continue
        
        print("\nAnalyzing...")
        
        try:
            result = await analyze_wallet(current_address, question, llm_provider=provider, context_id=context_id)
            
            if "error" in result:
                print(f"\nError: {result['error']}")
                current_address = None
                context_id = None
                continue
            
            # If this is the first question, display the wallet summary
            if context_id is None and "wallet_data" in result and "human_readable" in result["wallet_data"]:
                print("\nWALLET DATA SUMMARY:")
                print(result["wallet_data"]["human_readable"])
            
            # Update the context ID for continuity
            context_id = result["context_id"]
                
            print("\nLLM ANALYSIS:")
            print(result["analysis"])
            
        except Exception as e:
            logger.error(f"Error in interactive session: {str(e)}")
            print(f"\nAn error occurred: {str(e)}")
            current_address = None
            context_id = None

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Blockchain Analysis Demo")
    
    subparsers = parser.add_subparsers(dest="command", help="Analysis type")
    
    # Wallet analysis parser
    wallet_parser = subparsers.add_parser("wallet", help="Analyze a wallet address")
    wallet_parser.add_argument("address", help="Blockchain wallet address to analyze")
    wallet_parser.add_argument("-q", "--question", help="Specific question about the wallet")
    
    # Transaction analysis parser
    tx_parser = subparsers.add_parser("transaction", help="Analyze a transaction")
    tx_parser.add_argument("txid", help="Transaction ID to analyze")
    tx_parser.add_argument("-q", "--question", help="Specific question about the transaction")
    
    # Network analysis parser
    network_parser = subparsers.add_parser("network", help="Analyze network metrics")
    network_parser.add_argument("-m", "--metrics", nargs="+", help="Specific metrics to analyze")
    network_parser.add_argument("-q", "--question", help="Specific question about the network")
    
    # Forensic analysis parser
    forensic_parser = subparsers.add_parser("forensic", help="Perform forensic analysis of wallet interactions")
    forensic_parser.add_argument("address", help="Blockchain wallet address to analyze")
    forensic_parser.add_argument("-d", "--depth", type=int, default=2, help="Depth of analysis (default: 2)")
    forensic_parser.add_argument("-q", "--question", help="Specific question about the wallet relationships")
    
    # Interactive session parser
    interactive_parser = subparsers.add_parser("interactive", help="Start an interactive analysis session")
    interactive_parser.add_argument("-a", "--address", help="Initial wallet address (optional)")
    
    # Common arguments
    for subparser in [wallet_parser, tx_parser, network_parser, forensic_parser, interactive_parser]:
        subparser.add_argument("-p", "--provider", default="claude", choices=["claude", "ollama"], 
                              help="LLM provider to use (default: claude)")
    
    return parser.parse_args()

async def main():
    """Main entry point for the demo script."""
    args = parse_arguments()
    
    if not args.command:
        print("Please specify a command. Use -h or --help for options.")
        return
    
    if args.command == "wallet":
        await demo_wallet_analysis(args.address, args.question, args.provider)
    elif args.command == "transaction":
        await demo_transaction_analysis(args.txid, args.question, args.provider)
    elif args.command == "network":
        await demo_network_analysis(args.metrics, args.question, args.provider)
    elif args.command == "forensic":
        await demo_forensic_analysis(args.address, args.depth, args.question, args.provider)
    elif args.command == "interactive":
        await interactive_session(args.address, args.provider)

if __name__ == "__main__":
    asyncio.run(main()) 