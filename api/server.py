#!/usr/bin/env python3
"""
FastAPI server for BLUE blockchain analysis tools

This server exposes the blockchain analysis functionality through a REST API,
making it available to be consumed by frontend applications.
"""

import os
import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import the analysis functions
from llm.analysis_fixed import analyze_wallet, analyze_network
from llm.analysis import analyze_transaction, forensic_analysis

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BLUE - Blockchain Analysis API",
    description="API for blockchain analysis using LLM integration",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define API models
class AnalysisRequest(BaseModel):
    question: Optional[str] = None
    provider: str = "claude"

class WalletAnalysisRequest(AnalysisRequest):
    address: str

class TransactionAnalysisRequest(AnalysisRequest):
    tx_id: str

class NetworkAnalysisRequest(AnalysisRequest):
    metrics: Optional[List[str]] = None

class ForensicAnalysisRequest(AnalysisRequest):
    address: str
    depth: int = 2

# Define API endpoints
@app.get("/")
async def root():
    return {
        "message": "Welcome to the BLUE Blockchain Analysis API",
        "endpoints": [
            "/api/wallet",
            "/api/transaction",
            "/api/network",
            "/api/forensic"
        ]
    }

@app.post("/api/wallet")
async def wallet_analysis(request: WalletAnalysisRequest):
    """Analyze a blockchain wallet"""
    try:
        logger.info(f"Analyzing wallet: {request.address}")
        result = await analyze_wallet(request.address, request.question, request.provider)
        # Return only the analysis text part of the result, not the whole object
        return {"result": result['analysis']}
    except Exception as e:
        logger.error(f"Error analyzing wallet: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/transaction")
async def transaction_analysis(request: TransactionAnalysisRequest):
    """Analyze a blockchain transaction"""
    try:
        logger.info(f"Analyzing transaction: {request.tx_id}")
        result = await analyze_transaction(request.tx_id, request.question, request.provider)
        # Return only the analysis text part of the result, not the whole object
        if isinstance(result, dict) and 'analysis' in result:
            return {"result": result['analysis']}
        return {"result": result}  # If it's already a string or has a different structure
    except Exception as e:
        logger.error(f"Error analyzing transaction: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/network")
async def network_analysis(request: NetworkAnalysisRequest):
    """Analyze blockchain network metrics"""
    try:
        logger.info("Analyzing network metrics")
        
        # Create sample network stats since we don't have real-time data yet
        # Get current date and calculate date one month ago
        current_date = datetime.now()
        one_month_ago = current_date - timedelta(days=30)
        
        # Format dates as strings
        current_date_str = current_date.strftime("%Y-%m-%d")
        one_month_ago_str = one_month_ago.strftime("%Y-%m-%d")
        
        # Create network stats from requested metrics or use defaults
        network_stats = {
            "timeframe": f"{one_month_ago_str} to {current_date_str}",
        }
        
        # Add requested metrics if provided, otherwise use defaults
        if request.metrics:
            for metric in request.metrics:
                if metric == "hash_rate":
                    network_stats["avg_hashrate"] = "36.2 TH/s"
                elif metric == "difficulty":
                    network_stats["avg_difficulty"] = "2.48 PH"
                elif metric == "transaction_count":
                    network_stats["total_transactions"] = "246,593"
                    network_stats["avg_daily_transactions"] = "8,220"
                elif metric == "active_addresses":
                    network_stats["active_addresses"] = "18,245"
                    network_stats["new_addresses"] = "3,412"
                elif metric == "fee_rates":
                    network_stats["avg_fee"] = "0.00132 ERG"
        else:
            # Use all default metrics
            network_stats.update({
                "avg_hashrate": "36.2 TH/s",
                "avg_difficulty": "2.48 PH",
                "avg_block_time": "112 seconds",
                "total_blocks": "23,184",
                "total_transactions": "246,593",
                "avg_daily_transactions": "8,220",
                "active_addresses": "18,245",
                "new_addresses": "3,412",
            })
        
        # Sample network events
        network_events = [
            "Nautilus wallet v2.0.0 released with enhanced features",
            "Network hashrate increased following recent protocol upgrade",
            "Transaction volume trending upward over the last two weeks"
        ]
        
        # Call the fixed analyze_network function with the proper parameters
        analysis_text = analyze_network(
            network_stats=network_stats,
            network_events=network_events,
            question=request.question,
            llm_provider=request.provider
        )
        
        # Ensure we return a string for the result
        return {"result": analysis_text}
    except Exception as e:
        logger.error(f"Error analyzing network: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/forensic")
async def forensic_chain_analysis(request: ForensicAnalysisRequest):
    """Perform forensic analysis on a blockchain address"""
    try:
        logger.info(f"Performing forensic analysis on address: {request.address}")
        result = await forensic_analysis(request.address, request.depth, request.question, request.provider)
        # Return only the analysis text part of the result, not the whole object
        if isinstance(result, dict) and 'analysis' in result:
            return {"result": result['analysis']}
        return {"result": result}  # If it's already a string or has a different structure
    except Exception as e:
        logger.error(f"Error in forensic analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # For local development
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True) 