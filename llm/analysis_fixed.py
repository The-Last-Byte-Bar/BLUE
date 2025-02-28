"""
Fixed implementation of blockchain data analysis with LLM.

This module provides a corrected implementation of the blockchain analysis
functions to ensure compatibility with Claude's API requirements.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import copy
from datetime import datetime

from llm.client import LLMClient, LLMClientFactory
from data.wallet_analyzer import get_wallet_analysis_for_llm
from llm.analysis import ContextBuilder, BlockchainAnalyzer, analyze_wallet as original_analyze_wallet

logger = logging.getLogger(__name__)

class FixedBlockchainAnalyzer(BlockchainAnalyzer):
    """
    Fixed version of BlockchainAnalyzer to ensure compatibility with Claude API.
    
    The main difference is that this implementation adds wallet information
    as a user message instead of a system message.
    """
    
    async def analyze_wallet(self, 
                             address: str, 
                             question: Optional[str] = None,
                             context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a wallet address.
        
        Args:
            address: Blockchain address to analyze
            question: Optional specific question about the wallet
            context_id: Optional context ID for continuing a conversation
            
        Returns:
            Dictionary with wallet data and analysis
        """
        try:
            # Get wallet analysis data formatted for LLM
            wallet_data = await get_wallet_analysis_for_llm(address)
            
            # Extract the human-readable summary
            summary = wallet_data.get('human_readable', '')
            
            # Create or use existing context
            if not context_id:
                context_id = f"wallet-{address[:8]}"
                self.context_builder.create_context(context_id)
            
            # Add wallet information to context as a user message instead of system
            self.context_builder.add_to_context(
                context_id,
                f"Here is the wallet information to analyze:\n\n{summary}",
                role="user"  # Changed from "system" to "user"
            )
            
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
            context = self.context_builder.get_context(context_id)
            
            # Get response from LLM
            llm_response = await self.llm_client.generate(
                prompt=prompt,
                context=context,
                system_prompt="You are a blockchain analysis assistant. Your role is to analyze blockchain data and provide insights in a clear, accurate, and helpful manner. Focus on facts and patterns in the data."
            )
            
            # Add response to context
            self.context_builder.add_to_context(
                context_id,
                llm_response,
                role="assistant"
            )
            
            # Also add the user's question to the context
            self.context_builder.add_to_context(
                context_id,
                prompt,
                role="user"
            )
            
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

# Convenience function for direct use
async def analyze_wallet(address: str, 
                        question: Optional[str] = None, 
                        llm_provider: str = "claude",
                        context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a wallet address with the fixed implementation.
    
    Args:
        address: Blockchain address to analyze
        question: Optional specific question about the wallet
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with wallet data and analysis
    """
    analyzer = FixedBlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.analyze_wallet(address, question, context_id) 