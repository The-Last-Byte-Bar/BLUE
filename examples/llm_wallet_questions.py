"""
Example script for asking questions about wallets using LLM integration.

This script demonstrates how to use the LLM wallet insights module
to ask natural language questions about blockchain wallets.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm.wallet_insights import answer_wallet_question, get_wallet_insights

# Load environment variables
load_dotenv()

# Example Ergo address to analyze
EXAMPLE_ADDRESS = "9hY16vzHmmfyVBwKeFGHvb2bMFsG94A1u7MxLR3MkKYKDzwCEVg"

# Example questions to ask about the wallet
EXAMPLE_QUESTIONS = [
    "What is the total ERG balance of this wallet?",
    "Is this wallet actively used or dormant?",
    "What tokens does this wallet hold?",
    "Has this wallet had more incoming or outgoing transactions recently?"
]

async def main():
    """Run the LLM wallet questions example."""
    print("BLUE LLM Wallet Questions Example\n")
    print(f"Analyzing wallet address: {EXAMPLE_ADDRESS}\n")
    
    # First, get general insights about the wallet
    print("Getting general wallet insights...\n")
    insights = await get_wallet_insights(EXAMPLE_ADDRESS)
    
    if 'error' in insights:
        print(f"Error: {insights['error']}")
        return
    
    print("General Wallet Insights:")
    print("------------------------")
    print(insights.get('insights', 'No insights available'))
    print("\n")
    
    # Then, ask specific questions about the wallet
    print("Asking specific questions about the wallet...\n")
    
    for i, question in enumerate(EXAMPLE_QUESTIONS, 1):
        print(f"Question {i}: {question}")
        print("Answer:")
        
        # Get answer to the question
        response = await answer_wallet_question(EXAMPLE_ADDRESS, question)
        
        if 'error' in response:
            print(f"Error: {response['error']}")
        else:
            print(response.get('insights', 'No answer available'))
        
        print("\n")
        
        # Pause between questions for readability
        if i < len(EXAMPLE_QUESTIONS):
            print("Press Enter for the next question...")
            input()
            print("\n")
    
    print("This example demonstrates how LLMs can be used to provide")
    print("natural language insights about blockchain wallets using")
    print("the BLUE wallet analyzer module.")

if __name__ == "__main__":
    asyncio.run(main()) 