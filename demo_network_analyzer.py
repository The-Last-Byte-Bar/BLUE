#!/usr/bin/env python3
"""
A demonstration script for analyzing Ergo network statistics using Claude LLM.

This script shows how to use the blockchain analysis functions to examine 
blockchain network statistics and get LLM-generated insights.

Usage:
  python -m demo_network_analyzer [--provider {claude,ollama}]
"""

import sys
import argparse
from datetime import datetime, timedelta

# Import the fixed analysis functions
from llm.analysis_fixed import analyze_network

def parse_args():
    parser = argparse.ArgumentParser(description="Demonstrate Ergo network analysis with LLM")
    parser.add_argument(
        "-p", "--provider", 
        choices=["claude", "ollama"], 
        default="claude",
        help="LLM provider to use (default: claude)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    print("\n" + "=" * 80)
    print("ANALYZING ERGO NETWORK STATISTICS")
    print("=" * 80 + "\n")
    
    print(f"Using LLM Provider: {args.provider}")
    print("Fetching blockchain data and generating analysis...\n")
    
    # Get current date and calculate date one month ago
    current_date = datetime.now()
    one_month_ago = current_date - timedelta(days=30)
    
    # Format dates as strings
    current_date_str = current_date.strftime("%Y-%m-%d")
    one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")
    
    # Sample network statistics (in a real implementation, these would be fetched from an API)
    network_stats = {
        "timeframe": f"{one_month_ago_str} to {current_date_str}",
        "avg_hashrate": "36.2 TH/s",
        "avg_difficulty": "2.48 PH",
        "avg_block_time": "112 seconds",
        "total_blocks": "23,184",
        "total_transactions": "246,593",
        "avg_daily_transactions": "8,220",
        "peak_daily_transactions": "15,472 (on 2023-11-15)",
        "peak_hashrate": "42.1 TH/s (on 2023-11-10)",
        "current_emission": "3.15 ERG per block",
        "current_staked_erg": "1,242,583 ERG",
        "active_addresses": "18,245",
        "new_addresses": "3,412",
        "price_change": "+17.5%",
        "market_cap": "$158.7 million",
        "trading_volume_avg": "$4.2 million daily"
    }
    
    # Network events
    network_events = [
        "Nautilus wallet v2.0.0 released with enhanced features",
        "ErgoPad IDO for DarkFund launched",
        "EIP-31 (extended UTXO model improvements) passed community vote",
        "Network hashrate increased 22% following Bitcoin halving",
        "SigmaFi DEX volume exceeded $10M weekly for the first time"
    ]
    
    # Get analysis from LLM
    question = "What are the key trends and insights from this network data over the past month? This is sample data for demonstration purposes, please analyze it as if it were real data."
    analysis_result = analyze_network(
        network_stats=network_stats,
        network_events=network_events,
        question=question,
        llm_provider=args.provider
    )
    
    # Print the results
    print("NETWORK DATA SUMMARY:")
    print(f"Timeframe: {network_stats['timeframe']}")
    print(f"Average Hashrate: {network_stats['avg_hashrate']}")
    print(f"Average Difficulty: {network_stats['avg_difficulty']}")
    print(f"Average Block Time: {network_stats['avg_block_time']}")
    print(f"Total Blocks Mined: {network_stats['total_blocks']}")
    print(f"Total Transactions: {network_stats['total_transactions']}")
    print(f"Average Daily Transactions: {network_stats['avg_daily_transactions']}")
    print(f"Peak Daily Transactions: {network_stats['peak_daily_transactions']}")
    print(f"Current ERG Emission Rate: {network_stats['current_emission']}")
    print(f"Active Addresses: {network_stats['active_addresses']}")
    print(f"New Addresses: {network_stats['new_addresses']}")
    print(f"ERG Price Change: {network_stats['price_change']}")
    print(f"Market Cap: {network_stats['market_cap']}")
    print(f"Average Trading Volume: {network_stats['trading_volume_avg']}")
    
    print("\nRECENT NETWORK EVENTS:")
    for event in network_events:
        print(f"  • {event}")
    
    print("\nLLM ANALYSIS:")
    print(analysis_result)

if __name__ == "__main__":
    main() 