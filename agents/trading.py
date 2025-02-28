"""
Trading agent.

This module provides the trading agent class that analyzes market data
and makes trading decisions.
"""

from typing import Dict, Any, List, Optional, Tuple, Union
import logging
import asyncio
from datetime import datetime

from .agent import Agent
from .framework import AgentConfig
from ..data.market_data import MarketDataFetcher, MarketAnalyzer
from ..decision.engine import DecisionEngine
from ..decision.strategy import Strategy
from ..execution.engine import ExecutionEngine

logger = logging.getLogger(__name__)


class TradingAgent(Agent):
    """
    Agent for trading cryptocurrencies.
    
    This agent fetches market data, analyzes it using strategies,
    makes trading decisions, and executes trades.
    """
    
    def __init__(self, 
                 config: AgentConfig,
                 market_fetcher: MarketDataFetcher,
                 decision_engine: DecisionEngine,
                 execution_engine: ExecutionEngine):
        """
        Initialize a trading agent.
        
        Args:
            config: Agent configuration
            market_fetcher: Market data fetcher
            decision_engine: Decision engine
            execution_engine: Execution engine
        """
        super().__init__(config)
        self.market_fetcher = market_fetcher
        self.decision_engine = decision_engine
        self.execution_engine = execution_engine
        self.market_analyzer = MarketAnalyzer()
        
        # Initialize state
        self.state.update({
            'active_symbols': [],
            'last_analysis': {},
            'decisions': [],
            'executions': [],
            'portfolio_value': 0.0,
            'trading_enabled': False
        })
        
        # Get active symbols from config
        self.state['active_symbols'] = config.params.get('symbols', ['BTC', 'ETH'])
        self.state['trading_enabled'] = config.params.get('trading_enabled', False)
    
    async def _run(self) -> None:
        """Implement the trading agent's logic."""
        logger.info(f"Trading agent {self.config.name} starting run")
        
        # Step 1: Fetch market data
        active_symbols = self.state.get('active_symbols', [])
        
        if not active_symbols:
            logger.warning("No active symbols configured, nothing to trade")
            return
        
        market_data = await self._fetch_market_data(active_symbols)
        
        # Step 2: Analyze market data
        analysis_results = self._analyze_market_data(market_data)
        
        # Update state with analysis results
        self.state['last_analysis'] = {
            'timestamp': datetime.now().isoformat(),
            'results': analysis_results
        }
        
        # Step 3: Make trading decisions
        decisions = await self._make_trading_decisions(market_data, analysis_results)
        
        # Update state with decisions
        self.state['decisions'] = decisions
        
        # Step 4: Execute trades if trading is enabled
        if self.state.get('trading_enabled', False):
            executions = await self._execute_trades(decisions)
            
            # Update state with executions
            self.state['executions'] = executions
            
            # Get updated portfolio value
            portfolio_value = await self._get_portfolio_value()
            self.state['portfolio_value'] = portfolio_value
            
            logger.info(f"Trading agent {self.config.name} executed {len(executions)} trades")
            
            # Publish execution event
            if executions:
                event = self.create_event(
                    event_type="trade_executed",
                    data={
                        'executions': executions,
                        'portfolio_value': portfolio_value
                    }
                )
                self.publish_event(event)
        else:
            logger.info(f"Trading agent {self.config.name} trading is disabled, not executing trades")
            
            # Publish simulation event
            if decisions:
                event = self.create_event(
                    event_type="trade_simulated",
                    data={
                        'decisions': decisions
                    }
                )
                self.publish_event(event)
        
        logger.info(f"Trading agent {self.config.name} completed run")
    
    async def _fetch_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetch market data for symbols.
        
        Args:
            symbols: List of symbols to fetch data for
            
        Returns:
            Dictionary of market data
        """
        logger.debug(f"Fetching market data for {len(symbols)} symbols")
        
        # Get parameters from config
        exchange = self.config.params.get('exchange', 'binance')
        interval = self.config.params.get('interval', '1h')
        limit = self.config.params.get('ohlcv_limit', 100)
        
        # Fetch market data
        market_data = await self.market_fetcher.fetch_data(
            symbols=symbols,
            exchange=exchange,
            interval=interval,
            limit=limit
        )
        
        # Process the data
        processed_data = await self.market_fetcher.process_data(market_data)
        
        logger.debug(f"Fetched market data for {len(symbols)} symbols")
        return processed_data
    
    def _analyze_market_data(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data.
        
        Args:
            market_data: Market data to analyze
            
        Returns:
            Analysis results
        """
        logger.debug("Analyzing market data")
        
        analysis_results = {}
        
        # Analyze each symbol
        if 'ohlcv' in market_data:
            for symbol, ohlcv_data in market_data['ohlcv'].items():
                # Calculate metrics
                metrics = self.market_analyzer.calculate_metrics(ohlcv_data)
                
                # Detect trends
                trend_data = self.market_analyzer.detect_trends(ohlcv_data)
                
                analysis_results[symbol] = {
                    'metrics': metrics,
                    'trend': trend_data
                }
        
        # Analyze prices
        if 'prices' in market_data:
            analysis_results['prices'] = market_data['prices']
        
        # Analyze market stats
        if 'market_stats' in market_data:
            analysis_results['market_stats'] = market_data['market_stats']
        
        logger.debug(f"Analyzed market data for {len(analysis_results.keys())} symbols")
        return analysis_results
    
    async def _make_trading_decisions(self, market_data: Dict[str, Any], analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Make trading decisions based on market data and analysis.
        
        Args:
            market_data: Market data
            analysis_results: Analysis results
            
        Returns:
            List of trading decisions
        """
        logger.debug("Making trading decisions")
        
        decisions = []
        
        # Get active symbols from state
        active_symbols = self.state.get('active_symbols', [])
        
        # Make decisions for each symbol
        for symbol in active_symbols:
            if symbol in analysis_results:
                symbol_analysis = analysis_results[symbol]
                
                # Get current price
                current_price = None
                if 'prices' in market_data and symbol in market_data['prices']:
                    current_price = market_data['prices'][symbol].get('price')
                
                if current_price is None and 'metrics' in symbol_analysis:
                    current_price = symbol_analysis['metrics'].get('current_price')
                
                if current_price is None:
                    logger.warning(f"Could not determine current price for {symbol}, skipping decision")
                    continue
                
                # Make decision using decision engine
                decision = await self.decision_engine.make_decision(
                    symbol=symbol,
                    price=current_price,
                    analysis=symbol_analysis,
                    market_data=market_data
                )
                
                if decision:
                    decisions.append(decision)
        
        logger.debug(f"Made {len(decisions)} trading decisions")
        return decisions
    
    async def _execute_trades(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Execute trades based on decisions.
        
        Args:
            decisions: List of trading decisions
            
        Returns:
            List of execution results
        """
        logger.debug(f"Executing {len(decisions)} trades")
        
        executions = []
        
        # Execute each decision
        for decision in decisions:
            execution_result = await self.execution_engine.execute_decision(decision)
            
            if execution_result:
                executions.append(execution_result)
        
        logger.debug(f"Executed {len(executions)} trades")
        return executions
    
    async def _get_portfolio_value(self) -> float:
        """
        Get the current portfolio value.
        
        Returns:
            Current portfolio value
        """
        portfolio = await self.execution_engine.get_portfolio()
        
        if 'total_value' in portfolio:
            return portfolio['total_value']
        
        return 0.0
    
    def enable_trading(self) -> None:
        """Enable live trading."""
        self.state['trading_enabled'] = True
        logger.info(f"Trading agent {self.config.name} trading enabled")
    
    def disable_trading(self) -> None:
        """Disable live trading."""
        self.state['trading_enabled'] = False
        logger.info(f"Trading agent {self.config.name} trading disabled")
    
    def add_symbol(self, symbol: str) -> None:
        """
        Add a symbol to the active symbols list.
        
        Args:
            symbol: Symbol to add
        """
        active_symbols = self.state.get('active_symbols', [])
        
        if symbol not in active_symbols:
            active_symbols.append(symbol)
            self.state['active_symbols'] = active_symbols
            logger.info(f"Trading agent {self.config.name} added symbol {symbol}")
    
    def remove_symbol(self, symbol: str) -> None:
        """
        Remove a symbol from the active symbols list.
        
        Args:
            symbol: Symbol to remove
        """
        active_symbols = self.state.get('active_symbols', [])
        
        if symbol in active_symbols:
            active_symbols.remove(symbol)
            self.state['active_symbols'] = active_symbols
            logger.info(f"Trading agent {self.config.name} removed symbol {symbol}")
    
    def get_active_symbols(self) -> List[str]:
        """
        Get the list of active symbols.
        
        Returns:
            List of active symbols
        """
        return self.state.get('active_symbols', []) 