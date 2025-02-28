#!/usr/bin/env python3
"""
Blockchain Analysis Demo Script with Mock Data

This script demonstrates the blockchain analysis functionality using LLM integration
with mock data for offline testing and demonstration purposes.

To run this script:
    ./demo_blockchain_analyzer_mock.py interactive
    
Example addresses to try:
    9demo_miner123 - a mining wallet
    9demo_exchange123 - an exchange wallet
    9demo_defi123 - a DeFi protocol wallet
    9demo_user123 - a personal wallet
"""

import asyncio
import argparse
import logging
import json
import sys
from typing import Dict, Any, Optional, List
from datetime import datetime

from llm.client import LLMClientFactory, LLMClient
from data.wallet_demo_mock import get_wallet_analysis_for_llm_mock

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MockBlockchainAnalyzer:
    """
    Mock version of the BlockchainAnalyzer for demonstrations.
    
    This class simulates the functionality of the real BlockchainAnalyzer
    but uses mock data instead of fetching real blockchain data.
    """
    
    def __init__(self, llm_provider: str = "claude"):
        """
        Initialize the mock blockchain analyzer.
        
        Args:
            llm_provider: LLM provider to use
        """
        self.llm_client = LLMClientFactory.create(provider=llm_provider)
        self.contexts = {}
    
    async def analyze_wallet(self, 
                             address: str, 
                             question: Optional[str] = None,
                             context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a wallet address with mock data.
        
        Args:
            address: Blockchain address to analyze
            question: Optional specific question about the wallet
            context_id: Optional context ID for continuing a conversation
            
        Returns:
            Dictionary with wallet data and analysis
        """
        try:
            # Get mock wallet analysis data
            wallet_data = await get_wallet_analysis_for_llm_mock(address)
            
            # Extract the human-readable summary
            summary = wallet_data.get('human_readable', '')
            
            # Create or use existing context
            if not context_id:
                context_id = f"wallet-{address[:8]}"
                self.contexts[context_id] = []
            
            # For Claude, we need to append wallet information as a user message
            # instead of a system message
            self.contexts[context_id].append({
                "role": "user",
                "content": f"Here is the wallet information to analyze:\n\n{summary}"
            })
            
            # Create the prompt
            if question:
                prompt = question
            else:
                prompt = """
Please analyze this wallet data and provide insights about:
1. The wallet's balance and holdings
2. Recent transaction patterns
3. Any notable observations
4. Potential user profile based on activity
"""
                
            # Get context for the conversation
            context = self.contexts[context_id]
            
            # Prepare system prompt with instructions
            system_prompt = """You are a blockchain analysis assistant. Your role is to analyze blockchain data and provide insights in a clear, accurate, and helpful manner. Focus on facts and patterns in the data. 
            
When analyzing wallets, look for:
- Balance changes over time
- Transaction patterns (frequency, size, direction)
- Interactions with known entities
- Signs of specific behaviors (trading, mining, staking)
"""
            
            # Get response from LLM
            llm_response = await self.llm_client.generate(
                prompt=prompt,
                context=context,
                system_prompt=system_prompt
            )
            
            # Add response to context
            self.contexts[context_id].append({
                "role": "assistant",
                "content": llm_response
            })
            
            # Also add the user's question to the context
            self.contexts[context_id].append({
                "role": "user",
                "content": prompt
            })
            
            return {
                'address': address,
                'wallet_data': wallet_data,
                'question': question,
                'analysis': llm_response,
                'context_id': context_id
            }
            
        except Exception as e:
            logger.error(f"Error analyzing wallet {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e)
            }

async def mock_analyze_wallet(address: str, 
                              question: Optional[str] = None, 
                              llm_provider: str = "claude",
                              context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Mock function for wallet analysis.
    
    Args:
        address: Blockchain address to analyze
        question: Optional specific question about the wallet
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with wallet data and analysis
    """
    analyzer = MockBlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.analyze_wallet(address, question, context_id)

async def demo_wallet_analysis(address: str, question: Optional[str] = None, provider: str = "claude"):
    """Run a wallet analysis demonstration with mock data."""
    print(f"\n{'=' * 80}")
    print(f"ANALYZING WALLET (MOCK DATA): {address}")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Fetching mock wallet data and generating analysis...")
    
    try:
        result = await mock_analyze_wallet(address, question, llm_provider=provider)
        
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

async def interactive_session(initial_address: Optional[str] = None, provider: str = "claude"):
    """Run an interactive analysis session with mock data."""
    print(f"\n{'=' * 80}")
    print(f"INTERACTIVE BLOCKCHAIN ANALYSIS SESSION (MOCK DATA)")
    print(f"{'=' * 80}\n")
    
    print(f"Using LLM Provider: {provider}")
    print("Type 'exit' or 'quit' to end the session")
    print("\nSuggested demo addresses to try:")
    print("  9demo_miner123 - a mining wallet")
    print("  9demo_exchange123 - an exchange wallet")
    print("  9demo_defi123 - a DeFi protocol wallet")
    print("  9demo_user123 - a personal wallet")
    
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
            result = await mock_analyze_wallet(current_address, question, llm_provider=provider, context_id=context_id)
            
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
    parser = argparse.ArgumentParser(description="Blockchain Analysis Demo with Mock Data")
    
    subparsers = parser.add_subparsers(dest="command", help="Analysis type")
    
    # Wallet analysis parser
    wallet_parser = subparsers.add_parser("wallet", help="Analyze a wallet address")
    wallet_parser.add_argument("address", help="Blockchain wallet address to analyze")
    wallet_parser.add_argument("-q", "--question", help="Specific question about the wallet")
    
    # Interactive session parser
    interactive_parser = subparsers.add_parser("interactive", help="Start an interactive analysis session")
    interactive_parser.add_argument("-a", "--address", help="Initial wallet address (optional)")
    
    # Common arguments
    for subparser in [wallet_parser, interactive_parser]:
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
    elif args.command == "interactive":
        await interactive_session(args.address, args.provider)
    else:
        print(f"Command {args.command} not supported in mock demo. Only 'wallet' and 'interactive' are available.")

if __name__ == "__main__":
    asyncio.run(main()) 