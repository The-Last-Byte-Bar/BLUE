"""
Blockchain data analysis with LLM.

This module provides functionality for analyzing blockchain data
using language models. It supports different types of analysis,
including wallet analysis, transaction analysis, and network analysis.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import json
import asyncio
from datetime import datetime

from .client import LLMClient, LLMClientFactory
from data.wallet_analyzer import get_wallet_analysis_for_llm

logger = logging.getLogger(__name__)

class ContextBuilder:
    """
    Helper class for building context for LLM prompts.
    
    This class helps manage and format contextual information
    for LLM prompts to ensure they have the necessary background
    to answer questions accurately.
    """
    
    def __init__(self):
        """Initialize the context builder."""
        self.contexts = {}
    
    def create_context(self, context_id: str) -> str:
        """
        Create a new context with the given ID.
        
        Args:
            context_id: Unique identifier for the context
            
        Returns:
            The context ID
        """
        if context_id in self.contexts:
            logger.warning(f"Context {context_id} already exists, overwriting")
        
        self.contexts[context_id] = {
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "items": []
        }
        
        return context_id
    
    def add_to_context(self, context_id: str, content: str, role: str = "user") -> None:
        """
        Add content to a context.
        
        Args:
            context_id: ID of the context to add to
            content: Content to add
            role: Role of the content (user, assistant, system)
        """
        if context_id not in self.contexts:
            logger.warning(f"Context {context_id} does not exist, creating")
            self.create_context(context_id)
        
        self.contexts[context_id]["items"].append({
            "role": role,
            "content": content,
            "added_at": datetime.now().isoformat()
        })
        
        self.contexts[context_id]["updated_at"] = datetime.now().isoformat()
    
    def get_context(self, context_id: str) -> List[Dict[str, Any]]:
        """
        Get the context with the given ID.
        
        Args:
            context_id: ID of the context to get
            
        Returns:
            List of context items
        """
        if context_id not in self.contexts:
            logger.warning(f"Context {context_id} does not exist")
            return []
        
        return [
            {"role": item["role"], "content": item["content"]}
            for item in self.contexts[context_id]["items"]
        ]
    
    def clear_context(self, context_id: str) -> None:
        """
        Clear the context with the given ID.
        
        Args:
            context_id: ID of the context to clear
        """
        if context_id in self.contexts:
            self.contexts[context_id]["items"] = []
            self.contexts[context_id]["updated_at"] = datetime.now().isoformat()
        else:
            logger.warning(f"Context {context_id} does not exist")
    
    def delete_context(self, context_id: str) -> None:
        """
        Delete the context with the given ID.
        
        Args:
            context_id: ID of the context to delete
        """
        if context_id in self.contexts:
            del self.contexts[context_id]
        else:
            logger.warning(f"Context {context_id} does not exist")


class BlockchainAnalyzer:
    """
    Analyzes blockchain data using LLM.
    
    This class provides methods for analyzing various aspects of
    blockchain data, including wallets, transactions, and the network.
    """
    
    def __init__(self, llm_client: Optional[LLMClient] = None, llm_provider: str = "claude"):
        """
        Initialize the blockchain analyzer.
        
        Args:
            llm_client: Optional LLM client to use
            llm_provider: Provider to use if llm_client is not provided
        """
        self.llm_client = llm_client or LLMClientFactory.create(provider=llm_provider)
        self.context_builder = ContextBuilder()
    
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
            
            # Add wallet information to context
            self.context_builder.add_to_context(
                context_id,
                f"WALLET INFORMATION:\n{summary}",
                role="system"
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
    
    async def analyze_transaction(self, 
                                 transaction_id: str, 
                                 question: Optional[str] = None,
                                 context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze a transaction.
        
        Args:
            transaction_id: ID of the transaction to analyze
            question: Optional specific question about the transaction
            context_id: Optional context ID for continuing a conversation
            
        Returns:
            Dictionary with transaction data and analysis
        """
        # This is a placeholder for transaction analysis
        # In a real implementation, we would fetch transaction data
        # and format it for the LLM
        
        try:
            # Create or use existing context
            if not context_id:
                context_id = f"tx-{transaction_id[:8]}"
                self.context_builder.create_context(context_id)
            
            # Create the prompt
            if question:
                prompt = question
            else:
                prompt = f"""
I need to analyze the transaction with ID {transaction_id}. 
Please describe what this transaction does, who the participants are, and any notable aspects of it.
"""
                
            # Get context for the conversation
            context = self.context_builder.get_context(context_id)
            
            # Get response from LLM
            llm_response = await self.llm_client.generate(
                prompt=prompt,
                context=context,
                system_prompt="You are a blockchain transaction analyst. Provide detailed, accurate information about blockchain transactions, including their purpose, participants, and any interesting patterns or anomalies."
            )
            
            # Add response to context
            self.context_builder.add_to_context(
                context_id,
                llm_response,
                role="assistant"
            )
            
            return {
                'transaction_id': transaction_id,
                'question': question,
                'analysis': llm_response,
                'context_id': context_id,
                'error': "Transaction data fetching not yet implemented"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing transaction {transaction_id}: {str(e)}")
            return {
                'transaction_id': transaction_id,
                'error': str(e)
            }
    
    async def analyze_network(self, 
                             metrics: Optional[List[str]] = None, 
                             question: Optional[str] = None,
                             context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze network metrics.
        
        Args:
            metrics: Optional list of metrics to include
            question: Optional specific question about the network
            context_id: Optional context ID for continuing a conversation
            
        Returns:
            Dictionary with network data and analysis
        """
        # This is a placeholder for network analysis
        # In a real implementation, we would fetch network data
        # and format it for the LLM
        
        try:
            # Create or use existing context
            if not context_id:
                context_id = f"network-{datetime.now().strftime('%Y%m%d')}"
                self.context_builder.create_context(context_id)
            
            # Create the prompt
            if question:
                prompt = question
            else:
                metrics_str = ", ".join(metrics) if metrics else "all relevant metrics"
                prompt = f"""
Please provide an analysis of the current network status based on {metrics_str}.
Focus on throughput, security, and overall health of the network.
"""
                
            # Get context for the conversation
            context = self.context_builder.get_context(context_id)
            
            # Get response from LLM
            llm_response = await self.llm_client.generate(
                prompt=prompt,
                context=context,
                system_prompt="You are a blockchain network analyst. Provide clear, factual analysis of network conditions, focusing on performance, security, and relevant patterns or trends."
            )
            
            # Add response to context
            self.context_builder.add_to_context(
                context_id,
                llm_response,
                role="assistant"
            )
            
            return {
                'metrics': metrics,
                'question': question,
                'analysis': llm_response,
                'context_id': context_id,
                'error': "Network data fetching not yet implemented"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing network: {str(e)}")
            return {
                'metrics': metrics,
                'error': str(e)
            }
    
    async def forensic_analysis(self,
                               address: str,
                               depth: int = 2,
                               question: Optional[str] = None,
                               context_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Perform a forensic analysis of wallet interactions.
        
        This analysis looks at the relationships between a wallet and
        other addresses it has interacted with, to identify patterns 
        or anomalies.
        
        Args:
            address: Main address to analyze
            depth: How many levels of interaction to analyze
            question: Optional specific question about the relationships
            context_id: Optional context ID for continuing a conversation
            
        Returns:
            Dictionary with forensic analysis data
        """
        # This is a placeholder for forensic analysis
        # In a real implementation, we would trace transaction
        # history to identify patterns and relationships
        
        try:
            # Create or use existing context
            if not context_id:
                context_id = f"forensic-{address[:8]}"
                self.context_builder.create_context(context_id)
            
            # Create the prompt
            if question:
                prompt = question
            else:
                prompt = f"""
Please perform a forensic analysis of wallet {address} with depth {depth}.
Identify key relationships, unusual patterns, and any suspicious activity.
"""
                
            # Get context for the conversation
            context = self.context_builder.get_context(context_id)
            
            # Get response from LLM
            llm_response = await self.llm_client.generate(
                prompt=prompt,
                context=context,
                system_prompt="You are a blockchain forensic analyst. Your role is to identify relationships, patterns, and anomalies in blockchain transactions. Be thorough, detailed, and factual in your analysis."
            )
            
            # Add response to context
            self.context_builder.add_to_context(
                context_id,
                llm_response,
                role="assistant"
            )
            
            return {
                'address': address,
                'depth': depth,
                'question': question,
                'analysis': llm_response,
                'context_id': context_id,
                'error': "Forensic analysis not yet fully implemented"
            }
            
        except Exception as e:
            logger.error(f"Error performing forensic analysis for {address}: {str(e)}")
            return {
                'address': address,
                'error': str(e)
            }


# Convenience functions for direct use

async def analyze_wallet(address: str, 
                         question: Optional[str] = None, 
                         llm_provider: str = "claude",
                         context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a wallet address.
    
    Args:
        address: Blockchain address to analyze
        question: Optional specific question about the wallet
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with wallet data and analysis
    """
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.analyze_wallet(address, question, context_id)


async def analyze_transaction(transaction_id: str, 
                             question: Optional[str] = None, 
                             llm_provider: str = "claude",
                             context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze a transaction.
    
    Args:
        transaction_id: ID of the transaction to analyze
        question: Optional specific question about the transaction
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with transaction data and analysis
    """
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.analyze_transaction(transaction_id, question, context_id)


async def analyze_network(metrics: Optional[List[str]] = None, 
                         question: Optional[str] = None, 
                         llm_provider: str = "claude",
                         context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze network metrics.
    
    Args:
        metrics: Optional list of metrics to include
        question: Optional specific question about the network
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with network data and analysis
    """
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.analyze_network(metrics, question, context_id)


async def forensic_analysis(address: str,
                           depth: int = 2,
                           question: Optional[str] = None,
                           llm_provider: str = "claude",
                           context_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Perform a forensic analysis of wallet interactions.
    
    Args:
        address: Main address to analyze
        depth: How many levels of interaction to analyze
        question: Optional specific question about the relationships
        llm_provider: LLM provider to use
        context_id: Optional context ID for continuing a conversation
        
    Returns:
        Dictionary with forensic analysis data
    """
    analyzer = BlockchainAnalyzer(llm_provider=llm_provider)
    return await analyzer.forensic_analysis(address, depth, question, context_id) 