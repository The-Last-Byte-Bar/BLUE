"""
Wallet Analysis with LLM Example.

This script demonstrates how to analyze Ergo blockchain wallets
using LLM integration, including basic analysis, custom questions,
and conversation context management.
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

from llm.analysis import BlockchainAnalyzer
from data.wallet_analyzer import WalletAnalyzer, get_wallet_analysis_for_llm
from blockchain.explorer import ExplorerClient

# Load environment variables
load_dotenv()

# Example Ergo addresses to analyze
EXAMPLE_ADDRESSES = [
    "9hxEvxV6BqPJmWDesy8P1kFoXeQ3wF9ZGxvjak6TAiezr5tu4Sc",  # Valid address example
    # Add more example addresses here as needed
]

async def analyze_wallet_verbose(address: str, 
                                llm_provider: str = "claude", 
                                question: Optional[str] = None,
                                show_raw_data: bool = False) -> None:
    """
    Analyze a wallet address with detailed output.
    
    Args:
        address: Blockchain address to analyze
        llm_provider: LLM provider to use
        question: Optional specific question about the wallet
        show_raw_data: Whether to show raw wallet data
    """
    print(f"\n== Analyzing address: {address} ==\n")
    
    # Get raw wallet data first
    client = ExplorerClient()
    async with client:
        analyzer = WalletAnalyzer(client)
        wallet_summary = await analyzer.get_wallet_summary(address)
    
    # Display the human-readable summary
    print("Human-Readable Wallet Summary:")
    print("------------------------------")
    print(wallet_summary.get('human_readable', 'Error generating summary'))
    print("\n")
    
    # Display raw data if requested
    if show_raw_data:
        print("Raw Wallet Data (simplified):")
        print("-----------------------------")
        # Print a limited version for readability
        simplified = {
            'address': wallet_summary.get('address'),
            'transaction_count': wallet_summary.get('transaction_count'),
            'balance_example': next(iter(wallet_summary.get('current_balance', {}).items()), None),
            '...': '(additional data available in the full summary)'
        }
        print(json.dumps(simplified, indent=2))
        print("\n")
    
    # Create blockchain analyzer with LLM
    blockchain_analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Analyze the wallet with LLM
    if question:
        print(f"Analyzing with specific question: '{question}'")
    else:
        print("Performing general wallet analysis")
    
    llm_result = await blockchain_analyzer.analyze_wallet(address, question)
    
    # Display the LLM analysis
    print("\nLLM Analysis Result:")
    print("-------------------")
    print(llm_result.get('analysis', 'No analysis available'))
    print("\n")
    
    # Save the context ID for follow-up questions
    context_id = llm_result.get('context_id')
    
    # Follow-up conversation example
    if not question:
        # Demonstrate follow-up questions using the same context
        follow_up_questions = [
            "What can you tell me about the transaction patterns of this wallet?",
            "Based on the activity, what type of user do you think owns this wallet?",
            "What tokens does this wallet hold and what might they be used for?"
        ]
        
        for i, follow_up in enumerate(follow_up_questions, 1):
            print(f"\nFollow-up Question {i}:")
            print(f"Q: {follow_up}")
            
            # Use the same context for continuity
            follow_up_result = await blockchain_analyzer.analyze_wallet(
                address, 
                follow_up,
                context_id=context_id
            )
            
            print(f"\nA: {follow_up_result.get('analysis', 'No analysis available')}")
            
            # Pause between questions for readability
            if i < len(follow_up_questions):
                input("\nPress Enter for the next follow-up question...")

async def interactive_wallet_analysis(address: str, llm_provider: str = "claude") -> None:
    """
    Start an interactive wallet analysis session.
    
    Args:
        address: Blockchain address to analyze
        llm_provider: LLM provider to use
    """
    print(f"\n== Interactive Analysis for Address: {address} ==\n")
    print("Starting interactive wallet analysis session.")
    print("Type 'exit' or 'quit' to end the session.")
    
    # Create blockchain analyzer with LLM
    blockchain_analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Do initial analysis to establish context
    print("\nPerforming initial wallet analysis...")
    result = await blockchain_analyzer.analyze_wallet(address)
    
    # Save the context ID for the conversation
    context_id = result.get('context_id')
    
    # Display initial analysis
    print("\nInitial Analysis:")
    print("----------------")
    print(result.get('analysis', 'No analysis available'))
    
    # Start interactive loop
    while True:
        print("\n-----------------------------------------")
        question = input("\nEnter your question (or 'exit' to quit): ")
        
        if question.lower() in ['exit', 'quit', 'q']:
            break
        
        # Process the question
        print("\nAnalyzing...")
        result = await blockchain_analyzer.analyze_wallet(
            address,
            question,
            context_id=context_id
        )
        
        # Display the result
        print("\nAnalysis:")
        print(result.get('analysis', 'No analysis available'))
    
    print("\nEnding interactive session.")

async def compare_wallets(addresses: List[str], llm_provider: str = "claude") -> None:
    """
    Compare multiple wallet addresses.
    
    Args:
        addresses: List of addresses to compare
        llm_provider: LLM provider to use
    """
    if len(addresses) < 2:
        print("Need at least two addresses to compare.")
        return
    
    print(f"\n== Comparing {len(addresses)} Wallets ==\n")
    
    # Create blockchain analyzer with LLM
    blockchain_analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    
    # Create a new context for this comparison
    context_id = f"wallet-comparison-{addresses[0][:4]}-{addresses[1][:4]}"
    blockchain_analyzer.context_builder.create_context(context_id)
    
    # Fetch wallet data for all addresses
    wallet_summaries = []
    client = ExplorerClient()
    
    async with client:
        analyzer = WalletAnalyzer(client)
        for address in addresses:
            wallet_summary = await analyzer.get_wallet_summary(address)
            wallet_summaries.append(wallet_summary)
    
    # Add wallet information to context
    for i, summary in enumerate(wallet_summaries):
        human_readable = summary.get('human_readable', f"Error getting data for wallet {i+1}")
        blockchain_analyzer.context_builder.add_to_context(
            context_id,
            f"WALLET {i+1} ({addresses[i][:8]}...) INFORMATION:\n{human_readable}",
            role="system"
        )
    
    # Create the comparison prompt
    comparison_prompt = f"""
I'd like you to compare the {len(addresses)} wallets I've provided information for.
Please analyze:
1. The relative size and value of each wallet
2. Transaction patterns and activity levels
3. Token holdings and diversity
4. Likely wallet purposes/user types
5. Key similarities and differences

Provide a structured comparison that highlights the most significant differences.
"""
    
    # Get the comparison analysis
    result = await blockchain_analyzer.llm_client.generate(
        prompt=comparison_prompt,
        context=blockchain_analyzer.context_builder.get_context(context_id),
        system_prompt="You are a blockchain analysis assistant specializing in comparative wallet analysis. Provide clear, structured comparisons highlighting key similarities and differences between wallets."
    )
    
    # Display the result
    print("Wallet Comparison Analysis:")
    print("---------------------------")
    print(result)
    print("\n")

async def main():
    """Run the wallet analysis examples."""
    parser = argparse.ArgumentParser(description="Wallet Analysis with LLM")
    parser.add_argument("--address", type=str, default=EXAMPLE_ADDRESSES[0],
                      help="Wallet address to analyze")
    parser.add_argument("--provider", type=str, default="claude", choices=["claude", "ollama"],
                      help="LLM provider to use (claude or ollama)")
    parser.add_argument("--mode", type=str, default="analyze", 
                      choices=["analyze", "interactive", "compare"],
                      help="Analysis mode to run")
    parser.add_argument("--question", type=str, default=None,
                      help="Specific question to ask (for analyze mode)")
    parser.add_argument("--compare", type=str, nargs='+', default=None,
                      help="Addresses to compare (for compare mode)")
    parser.add_argument("--raw", action="store_true", 
                      help="Show raw wallet data")
    
    args = parser.parse_args()
    
    print("BLUE Wallet Analysis with LLM\n")
    
    # Check for required environment variables
    if args.provider == "claude" and not os.environ.get("ANTHROPIC_API_KEY"):
        print("WARNING: ANTHROPIC_API_KEY environment variable not set.")
        print("Set this in your .env file or in your environment to use Claude.")
        print("Falling back to Ollama...")
        args.provider = "ollama"
    
    # Run the selected mode
    if args.mode == "analyze":
        await analyze_wallet_verbose(args.address, args.provider, args.question, args.raw)
    elif args.mode == "interactive":
        await interactive_wallet_analysis(args.address, args.provider)
    elif args.mode == "compare":
        # Use provided addresses for comparison, or default to comparing with the main address
        compare_addresses = args.compare if args.compare else [args.address, EXAMPLE_ADDRESSES[0]]
        # Remove duplicates while preserving order
        compare_addresses = list(dict.fromkeys(compare_addresses))
        await compare_wallets(compare_addresses, args.provider)

if __name__ == "__main__":
    asyncio.run(main()) 