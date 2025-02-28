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
from llm.llm import get_llm_client

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

def analyze_network(
    network_stats: Dict[str, str],
    network_events: List[str],
    question: Optional[str] = None,
    llm_provider: str = "claude"
) -> str:
    """
    Analyze network statistics using an LLM with proper context formatting.
    
    Args:
        network_stats: Dictionary containing network statistics
        network_events: List of recent network events
        question: Optional specific question to ask about the network
        llm_provider: The LLM provider to use (claude or ollama)
        
    Returns:
        str: The analysis from the LLM
    """
    # Get LLM client
    llm_client = get_llm_client(llm_provider)
    
    # Prepare network data for display
    network_summary = "NETWORK STATISTICS:\n"
    for key, value in network_stats.items():
        formatted_key = key.replace('_', ' ').title()
        network_summary += f"{formatted_key}: {value}\n"
    
    network_summary += "\nRECENT NETWORK EVENTS:\n"
    for event in network_events:
        network_summary += f"• {event}\n"
    
    # Create system prompt
    system_prompt = """
You are an expert blockchain analyst specializing in the Ergo blockchain. 
You provide detailed analyses of blockchain network statistics and trends.
Your analyses should be data-driven, objective, and insightful, highlighting patterns and notable observations.
Focus on extracting meaningful insights from the provided network data, including:
- Growth trends and user adoption
- Network security and health indicators
- Transaction volume patterns
- Notable ecosystem developments
- Market performance indicators

Respond directly to any questions asked by the user, ensuring comprehensive and informative responses.
    """
    
    # Set up the conversation context
    context = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the network statistics I'd like you to analyze:\n\n{network_summary}"}
    ]
    
    # Add the question if provided
    if question:
        context.append({"role": "user", "content": question})
    else:
        context.append({"role": "user", "content": "Please analyze these network statistics and provide insights about the current state and trends of the Ergo blockchain."})
    
    # Get response from LLM
    response = llm_client.chat(context)
    
    return response

def analyze_transaction(
    transaction_id: str,
    transaction_data: Dict[str, Any],
    question: Optional[str] = None,
    llm_provider: str = "claude"
) -> str:
    """
    Analyze a transaction using an LLM with proper context formatting.
    
    Args:
        transaction_id: The ID of the transaction to analyze
        transaction_data: Dictionary containing transaction data
        question: Optional specific question to ask about the transaction
        llm_provider: The LLM provider to use (claude or ollama)
        
    Returns:
        str: The analysis from the LLM
    """
    # Get LLM client
    llm_client = get_llm_client(llm_provider)
    
    # Format transaction data
    tx_summary = f"Transaction ID: {transaction_id}\n"
    tx_summary += f"Block Height: {transaction_data.get('block_height', 'Unknown')}\n"
    tx_summary += f"Timestamp: {transaction_data.get('timestamp', 'Unknown')}\n"
    tx_summary += f"Size: {transaction_data.get('size', 'Unknown')} bytes\n"
    tx_summary += f"Confirmations: {transaction_data.get('confirmations', 'Unknown')}\n\n"
    
    # Inputs
    tx_summary += "INPUTS:\n"
    for input_item in transaction_data.get('inputs', []):
        tx_summary += f"  • {input_item.get('amount', 'Unknown')} {input_item.get('token', 'ERG')} "
        tx_summary += f"from {input_item.get('address', 'Unknown address')}\n"
    
    # Outputs
    tx_summary += "\nOUTPUTS:\n"
    for output in transaction_data.get('outputs', []):
        tx_summary += f"  • {output.get('amount', 'Unknown')} {output.get('token', 'ERG')} "
        tx_summary += f"to {output.get('address', 'Unknown address')}\n"
    
    # Additional data if available
    if 'fee' in transaction_data:
        tx_summary += f"\nFee: {transaction_data['fee']} ERG\n"
    
    if 'scripts' in transaction_data and transaction_data['scripts']:
        tx_summary += "\nTransaction contains scripts/contracts\n"
    
    # Create system prompt
    system_prompt = """
You are an expert blockchain analyst specializing in the Ergo blockchain. 
You provide detailed analyses of blockchain transactions, explaining their purpose and significance.
Your analyses should be data-driven, objective, and insightful, highlighting patterns and notable observations.
Focus on extracting meaningful insights from the provided transaction data, including:
- Type of transaction (simple transfer, contract interaction, etc.)
- Flow of funds and tokens
- Potential purpose of the transaction
- Any unusual or notable aspects

Respond directly to any questions asked by the user, ensuring comprehensive and informative responses.
    """
    
    # Set up the conversation context
    context = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the transaction data I'd like you to analyze:\n\n{tx_summary}"}
    ]
    
    # Add the question if provided
    if question:
        context.append({"role": "user", "content": question})
    else:
        context.append({"role": "user", "content": "Please analyze this transaction and explain what it represents in the Ergo blockchain."})
    
    # Get response from LLM
    response = llm_client.chat(context)
    
    return response

def forensic_analysis(
    data: Dict[str, Any],
    question: str,
    llm_provider: str = "claude"
) -> str:
    """
    Perform forensic analysis on blockchain data using an LLM with proper context formatting.
    
    Args:
        data: Dictionary containing relevant blockchain data for forensic analysis
        question: Specific forensic question to investigate
        llm_provider: The LLM provider to use (claude or ollama)
        
    Returns:
        str: The forensic analysis from the LLM
    """
    # Get LLM client
    llm_client = get_llm_client(llm_provider)
    
    # Format forensic data
    forensic_summary = "FORENSIC ANALYSIS DATA:\n\n"
    
    # Format wallet data if provided
    if 'wallets' in data:
        forensic_summary += "WALLET DATA:\n"
        for wallet in data['wallets']:
            forensic_summary += f"Address: {wallet['address']}\n"
            forensic_summary += f"Balance: {wallet['balance']} ERG\n"
            forensic_summary += f"Transaction Count: {wallet['tx_count']}\n"
            forensic_summary += f"First Active: {wallet.get('first_active', 'Unknown')}\n"
            forensic_summary += f"Last Active: {wallet.get('last_active', 'Unknown')}\n"
            
            if 'tags' in wallet and wallet['tags']:
                forensic_summary += "Tags: " + ", ".join(wallet['tags']) + "\n"
            
            forensic_summary += "\n"
    
    # Format transaction data if provided
    if 'transactions' in data:
        forensic_summary += "TRANSACTION DATA:\n"
        for tx in data['transactions']:
            forensic_summary += f"ID: {tx['id']}\n"
            forensic_summary += f"Timestamp: {tx.get('timestamp', 'Unknown')}\n"
            forensic_summary += f"Amount: {tx.get('amount', 'Unknown')} {tx.get('token', 'ERG')}\n"
            forensic_summary += f"From: {tx.get('from', 'Unknown')}\n"
            forensic_summary += f"To: {tx.get('to', 'Unknown')}\n"
            
            if 'note' in tx and tx['note']:
                forensic_summary += f"Note: {tx['note']}\n"
            
            forensic_summary += "\n"
    
    # Format cluster data if provided
    if 'clusters' in data:
        forensic_summary += "CLUSTER DATA:\n"
        for cluster in data['clusters']:
            forensic_summary += f"Cluster ID: {cluster['id']}\n"
            forensic_summary += f"Addresses: {', '.join(cluster['addresses'])}\n"
            forensic_summary += f"Total Value: {cluster.get('total_value', 'Unknown')} ERG\n"
            
            if 'entity' in cluster and cluster['entity']:
                forensic_summary += f"Entity: {cluster['entity']}\n"
            
            if 'risk_score' in cluster:
                forensic_summary += f"Risk Score: {cluster['risk_score']}/100\n"
            
            forensic_summary += "\n"
    
    # Format flow data if provided
    if 'flows' in data:
        forensic_summary += "FUND FLOW DATA:\n"
        for flow in data['flows']:
            forensic_summary += f"From: {flow['from']}\n"
            forensic_summary += f"To: {flow['to']}\n"
            forensic_summary += f"Amount: {flow['amount']} {flow.get('token', 'ERG')}\n"
            forensic_summary += f"Transactions: {flow['tx_count']}\n"
            forensic_summary += f"Time Period: {flow.get('time_period', 'Unknown')}\n"
            forensic_summary += "\n"
    
    # Create system prompt
    system_prompt = """
You are an expert blockchain forensic analyst specializing in the Ergo blockchain. 
You provide detailed forensic analyses of blockchain data to answer specific investigative questions.
Your analyses should be data-driven, objective, and insightful, highlighting patterns and evidence relevant to the investigation.
Focus on extracting meaningful insights from the provided blockchain data, including:
- Address clustering and entity identification
- Flow of funds analysis
- Temporal patterns and anomalies
- Potential connection to known entities or activities
- Risk assessment

Respond directly to the forensic question asked by the user, ensuring comprehensive and evidence-based responses.
    """
    
    # Set up the conversation context
    context = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the blockchain data for forensic analysis:\n\n{forensic_summary}"},
        {"role": "user", "content": f"Forensic question: {question}"}
    ]
    
    # Get response from LLM
    response = llm_client.chat(context)
    
    return response 