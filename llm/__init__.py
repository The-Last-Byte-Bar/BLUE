"""
LLM integration package for the BLUE project.

This package provides functionality for integrating blockchain data
with language models to enable natural language interaction with
blockchain analytics.
"""

__version__ = '0.1.0'

# Import client classes
from .client import LLMClient, ClaudeClient, OllamaClient, LLMClientFactory

# Import sync wrapper
from .llm import get_llm_client, SyncLLMClient

# Import wallet insights (legacy)
from .wallet_insights import get_wallet_insights, answer_wallet_question

# Import blockchain analysis
from .analysis import (
    BlockchainAnalyzer, 
    ContextBuilder,
    analyze_wallet,
    analyze_transaction,
    analyze_network,
    forensic_analysis
) 