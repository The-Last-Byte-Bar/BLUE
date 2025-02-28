"""
Mock wallet data provider for the demo.

This module provides mock wallet data for demonstrations,
without requiring access to the actual blockchain.
"""

import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

async def get_wallet_analysis_for_llm_mock(address: str) -> Dict[str, Any]:
    """
    Get mock wallet analysis data for LLM demos.
    
    Args:
        address: Blockchain address to analyze
        
    Returns:
        Mocked analysis data formatted for LLM use
    """
    logger.info(f"Getting mock wallet data for {address}")
    
    # Check for demo address prefix for different samples
    if address.startswith('9demo_miner'):
        return {
            'wallet_summary': {
                'address': address,
                'transaction_count': 1042,
                'current_balance': {
                    'ERG': 15230.45,
                    'SigUSD': 500.0,
                    'NETA': 1000.0
                },
                'transactions': {
                    'last_30_days': 128,
                    'outgoing': 15,
                    'incoming': 113
                },
                'creation_date': '2021-06-15',
                'last_activity': '2023-03-08',
                'classification': 'Mining Wallet',
                'common_interactions': [
                    '9demo_exchange1234567890',
                    '9demo_pool1234567890'
                ]
            },
            'human_readable': """
Wallet Address: {address}
Type: Mining Wallet

This appears to be a mining wallet that has been active since June 2021. 
It currently holds 15,230.45 ERG, 500 SigUSD, and 1,000 NETA tokens.

Transaction Activity:
- Total Transactions: 1,042
- Transactions in Last 30 Days: 128
- Mostly receiving transactions (113 incoming vs 15 outgoing)

The wallet regularly interacts with what appears to be a mining pool 
and occasionally transfers funds to an exchange wallet.
The pattern suggests consistent mining activity with periodic profit-taking.
""".format(address=address)
        }
    
    elif address.startswith('9demo_exchange'):
        return {
            'wallet_summary': {
                'address': address,
                'transaction_count': 25690,
                'current_balance': {
                    'ERG': 1250000.0,
                    'SigUSD': 85000.0,
                    'NETA': 25000.0,
                    'Other Tokens': '150+ types'
                },
                'transactions': {
                    'last_30_days': 3850,
                    'outgoing': 1920,
                    'incoming': 1930
                },
                'creation_date': '2020-07-01',
                'last_activity': '2023-03-10',
                'classification': 'Exchange Wallet',
                'common_interactions': [
                    'Multiple user wallets',
                    'Multiple other exchanges'
                ]
            },
            'human_readable': """
Wallet Address: {address}
Type: Exchange Wallet

This is a high-activity wallet with characteristics typical of an exchange hot wallet.
It currently holds approximately 1.25M ERG, 85K SigUSD, and numerous other tokens.

Transaction Activity:
- Total Transactions: 25,690
- Transactions in Last 30 Days: 3,850
- Balanced incoming/outgoing ratio (1,930 incoming, 1,920 outgoing)

The wallet shows a pattern of high-frequency, often batched transactions,
with regular interactions with other known exchange wallets.
The transaction volume and token variety strongly suggest this is an
exchange-controlled wallet used for customer deposits and withdrawals.
""".format(address=address)
        }
    
    elif address.startswith('9demo_defi'):
        return {
            'wallet_summary': {
                'address': address,
                'transaction_count': 8742,
                'current_balance': {
                    'ERG': 45000.0,
                    'SigUSD': 150000.0,
                    'SigRSV': 25000.0,
                    'LP Tokens': 'Various'
                },
                'transactions': {
                    'last_30_days': 850,
                    'outgoing': 410,
                    'incoming': 440
                },
                'creation_date': '2021-09-10',
                'last_activity': '2023-03-09',
                'classification': 'DeFi Protocol Wallet',
                'common_interactions': [
                    'Various liquidity pools',
                    'Multiple user wallets'
                ]
            },
            'human_readable': """
Wallet Address: {address}
Type: DeFi Protocol Wallet

This appears to be a wallet associated with a DeFi protocol or liquidity pool.
It currently holds 45,000 ERG, 150,000 SigUSD, 25,000 SigRSV, and various LP tokens.

Transaction Activity:
- Total Transactions: 8,742
- Transactions in Last 30 Days: 850
- Roughly balanced transaction flow (440 incoming, 410 outgoing)

The wallet shows consistent interaction with many different user wallets,
with transaction patterns consistent with liquidity provision, swaps, and yield farming.
The regular inflows and outflows of various tokens, especially ERG, SigUSD, and SigRSV,
suggest this wallet is part of an AMM or other DeFi protocol infrastructure.
""".format(address=address)
        }
    
    else:
        # Default demo wallet
        return {
            'wallet_summary': {
                'address': address,
                'transaction_count': 37,
                'current_balance': {
                    'ERG': 125.75,
                    'SigUSD': 50.0,
                    'NETA': 10.0
                },
                'transactions': {
                    'last_30_days': 5,
                    'outgoing': 12,
                    'incoming': 25
                },
                'creation_date': '2022-01-20',
                'last_activity': '2023-03-05',
                'classification': 'Personal Wallet',
                'common_interactions': [
                    '9demo_exchange1234567890'
                ]
            },
            'human_readable': """
Wallet Address: {address}
Type: Personal Wallet

This appears to be a personal wallet with moderate activity.
It currently holds 125.75 ERG, 50 SigUSD, and 10 NETA tokens.

Transaction Activity:
- Total Transactions: 37
- Transactions in Last 30 Days: 5
- More incoming than outgoing transactions (25 vs 12)

The wallet primarily interacts with what appears to be an exchange wallet,
suggesting this is likely a retail user who occasionally purchases or sells ERG and tokens.
The transaction pattern is consistent with a long-term holder who makes occasional trades.
""".format(address=address)
        } 