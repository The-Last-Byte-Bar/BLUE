"""
Market data fetchers.

This module provides components for fetching and processing market data
from various sources such as crypto exchanges and market data providers.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

from .processor import DataSource

logger = logging.getLogger(__name__)


class MarketDataFetcher(DataSource):
    """Fetcher for cryptocurrency market data."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """
        Initialize the market data fetcher.

        Args:
            base_url: Base URL for the market data API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url
        self.api_key = api_key
        self.session = None
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = timedelta(minutes=5)

    async def __aenter__(self):
        """Set up the HTTP session when used as an async context manager."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the HTTP session when exiting the async context manager."""
        if self.session:
            await self.session.close()
            self.session = None

    async def _get_session(self):
        """Get or create an HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession()
        return self.session

    async def _make_request(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Make a request to the market data API.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response data as a dictionary
        """
        session = await self._get_session()
        headers = {}
        
        if self.api_key:
            headers['X-API-Key'] = self.api_key
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with session.get(url, params=params, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Market API error ({response.status}): {error_text}")
            
            return await response.json()

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch market data.

        Args:
            **kwargs: Parameters for the market data fetch:
                - symbols: Optional list of symbols to fetch
                - exchange: Optional exchange to fetch data from
                - interval: Optional time interval for OHLCV data
                - start_time: Optional start time for time-series data
                - end_time: Optional end time for time-series data

        Returns:
            Dictionary of fetched market data
        """
        result = {}
        
        # Fetch price data
        symbols = kwargs.get('symbols', [])
        if not symbols:
            # Default to top cryptocurrencies if none specified
            symbols = ['BTC', 'ETH', 'XRP', 'ADA', 'DOT']
        
        exchange = kwargs.get('exchange', 'binance')
        
        # Build cache key
        cache_key = f"prices_{exchange}_{','.join(symbols)}"
        
        if self._is_cached(cache_key):
            result['prices'] = self.cache[cache_key]
        else:
            try:
                prices = await self._fetch_prices(symbols, exchange)
                result['prices'] = prices
                self._cache_item(cache_key, prices)
            except Exception as e:
                logger.error(f"Error fetching prices: {str(e)}")
        
        # Fetch OHLCV data if interval is specified
        interval = kwargs.get('interval')
        if interval:
            start_time = kwargs.get('start_time')
            end_time = kwargs.get('end_time')
            
            for symbol in symbols:
                ohlcv_cache_key = f"ohlcv_{exchange}_{symbol}_{interval}_{start_time}_{end_time}"
                
                if self._is_cached(ohlcv_cache_key):
                    if 'ohlcv' not in result:
                        result['ohlcv'] = {}
                    result['ohlcv'][symbol] = self.cache[ohlcv_cache_key]
                else:
                    try:
                        ohlcv = await self._fetch_ohlcv(symbol, exchange, interval, start_time, end_time)
                        if 'ohlcv' not in result:
                            result['ohlcv'] = {}
                        result['ohlcv'][symbol] = ohlcv
                        self._cache_item(ohlcv_cache_key, ohlcv)
                    except Exception as e:
                        logger.error(f"Error fetching OHLCV for {symbol}: {str(e)}")
        
        # Fetch market stats
        market_stats_cache_key = f"market_stats_{exchange}"
        if self._is_cached(market_stats_cache_key):
            result['market_stats'] = self.cache[market_stats_cache_key]
        else:
            try:
                market_stats = await self._fetch_market_stats(exchange)
                result['market_stats'] = market_stats
                self._cache_item(market_stats_cache_key, market_stats)
            except Exception as e:
                logger.error(f"Error fetching market stats: {str(e)}")
        
        return result

    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the fetched market data.

        Args:
            data: Raw market data to process

        Returns:
            Processed market data
        """
        processed = {}
        
        # Process price data
        if 'prices' in data:
            processed['prices'] = {}
            for symbol, price_data in data['prices'].items():
                try:
                    price = float(price_data['price'])
                    change_24h = float(price_data.get('change_24h', 0))
                    
                    processed['prices'][symbol] = {
                        'price': price,
                        'change_24h': change_24h,
                        'change_pct_24h': round((change_24h / (price - change_24h)) * 100, 2) if price != change_24h else 0,
                        'timestamp': price_data.get('timestamp', datetime.now().isoformat())
                    }
                except (ValueError, TypeError):
                    processed['prices'][symbol] = price_data
        
        # Process OHLCV data
        if 'ohlcv' in data:
            processed['ohlcv'] = {}
            for symbol, ohlcv_data in data['ohlcv'].items():
                processed['ohlcv'][symbol] = self._process_ohlcv(ohlcv_data)
        
        # Process market stats
        if 'market_stats' in data:
            processed['market_stats'] = data['market_stats']
            
            # Add derived metrics if possible
            if 'total_market_cap' in processed['market_stats'] and 'total_volume_24h' in processed['market_stats']:
                try:
                    market_cap = float(processed['market_stats']['total_market_cap'])
                    volume = float(processed['market_stats']['total_volume_24h'])
                    processed['market_stats']['volume_to_mcap_ratio'] = round(volume / market_cap, 4) if market_cap > 0 else 0
                except (ValueError, TypeError):
                    pass
        
        return processed

    async def _fetch_prices(self, symbols: List[str], exchange: str) -> Dict[str, Dict[str, Any]]:
        """
        Fetch current prices for symbols.

        Args:
            symbols: List of symbols to fetch prices for
            exchange: Exchange to fetch prices from

        Returns:
            Dictionary mapping symbols to price data
        """
        symbols_param = ','.join(symbols)
        data = await self._make_request('api/v1/prices', {'symbols': symbols_param, 'exchange': exchange})
        
        result = {}
        for item in data.get('data', []):
            symbol = item.get('symbol')
            if symbol:
                result[symbol] = item
        
        return result

    async def _fetch_ohlcv(self, symbol: str, exchange: str, interval: str, start_time: Optional[str] = None, end_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Fetch OHLCV (Open, High, Low, Close, Volume) data.

        Args:
            symbol: Symbol to fetch OHLCV data for
            exchange: Exchange to fetch data from
            interval: Time interval (e.g. '1h', '1d')
            start_time: Optional start time
            end_time: Optional end time

        Returns:
            List of OHLCV data points
        """
        params = {
            'symbol': symbol,
            'exchange': exchange,
            'interval': interval
        }
        
        if start_time:
            params['start_time'] = start_time
        
        if end_time:
            params['end_time'] = end_time
        
        data = await self._make_request('api/v1/ohlcv', params)
        
        return data.get('data', [])

    async def _fetch_market_stats(self, exchange: str) -> Dict[str, Any]:
        """
        Fetch market statistics.

        Args:
            exchange: Exchange to fetch stats from

        Returns:
            Dictionary of market statistics
        """
        data = await self._make_request('api/v1/market-stats', {'exchange': exchange})
        
        return data.get('data', {})

    def _process_ohlcv(self, ohlcv_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process OHLCV data.

        Args:
            ohlcv_data: Raw OHLCV data

        Returns:
            Processed OHLCV data
        """
        processed = []
        
        for item in ohlcv_data:
            try:
                processed.append({
                    'timestamp': item.get('timestamp'),
                    'open': float(item.get('open', 0)),
                    'high': float(item.get('high', 0)),
                    'low': float(item.get('low', 0)),
                    'close': float(item.get('close', 0)),
                    'volume': float(item.get('volume', 0)),
                    'date': datetime.fromisoformat(item.get('timestamp').replace('Z', '+00:00')).strftime('%Y-%m-%d %H:%M:%S') if 'timestamp' in item else None
                })
            except (ValueError, TypeError, AttributeError):
                processed.append(item)
        
        return processed

    def _is_cached(self, cache_key: str) -> bool:
        """
        Check if data is in the cache and not expired.

        Args:
            cache_key: Cache key to check

        Returns:
            True if the data is cached and not expired, False otherwise
        """
        if cache_key in self.cache:
            expiry = self.cache_expiry.get(cache_key)
            if expiry and datetime.now() < expiry:
                return True
            # Remove expired item
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.cache_expiry:
                del self.cache_expiry[cache_key]
        return False

    def _cache_item(self, cache_key: str, item: Any) -> None:
        """
        Cache data.

        Args:
            cache_key: Cache key to store the data under
            item: Data to cache
        """
        self.cache[cache_key] = item
        self.cache_expiry[cache_key] = datetime.now() + self.cache_ttl
        
        # Limit cache size (keep most recent 100 items)
        if len(self.cache) > 100:
            oldest_key = min(self.cache_expiry.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.cache_expiry[oldest_key]


class MarketAnalyzer:
    """
    Utility for analyzing market data.
    
    This class provides methods for analyzing market data and extracting
    insights such as price trends, correlations, etc.
    """

    def __init__(self):
        """Initialize the market analyzer."""
        pass
    
    def calculate_metrics(self, ohlcv_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate market metrics from OHLCV data.

        Args:
            ohlcv_data: OHLCV data points

        Returns:
            Dictionary of calculated metrics
        """
        if not ohlcv_data:
            return {}
        
        closes = [item['close'] for item in ohlcv_data if 'close' in item]
        volumes = [item['volume'] for item in ohlcv_data if 'volume' in item]
        
        if not closes:
            return {}
        
        current_price = closes[-1]
        max_price = max(closes)
        min_price = min(closes)
        avg_price = sum(closes) / len(closes)
        
        result = {
            'current_price': current_price,
            'max_price': max_price,
            'min_price': min_price,
            'avg_price': avg_price,
            'price_range': max_price - min_price,
            'price_volatility': (max_price - min_price) / avg_price if avg_price > 0 else 0
        }
        
        if len(closes) > 1:
            result['price_change'] = closes[-1] - closes[0]
            result['price_change_pct'] = (result['price_change'] / closes[0]) * 100 if closes[0] > 0 else 0
        
        if volumes:
            result['avg_volume'] = sum(volumes) / len(volumes)
            result['max_volume'] = max(volumes)
        
        return result
    
    def detect_trends(self, ohlcv_data: List[Dict[str, Any]], window: int = 14) -> Dict[str, Any]:
        """
        Detect trends in OHLCV data.

        Args:
            ohlcv_data: OHLCV data points
            window: Window size for moving averages

        Returns:
            Dictionary with trend information
        """
        if not ohlcv_data or len(ohlcv_data) < window:
            return {'trend': 'unknown', 'confidence': 0}
        
        closes = [item['close'] for item in ohlcv_data if 'close' in item]
        
        if len(closes) < window:
            return {'trend': 'unknown', 'confidence': 0}
        
        # Calculate simple moving average
        sma = []
        for i in range(len(closes) - window + 1):
            sma.append(sum(closes[i:i+window]) / window)
        
        # Determine trend based on SMA slope
        trend = 'sideways'
        confidence = 0
        
        if len(sma) >= 2:
            slope = (sma[-1] - sma[0]) / len(sma)
            
            if slope > 0:
                trend = 'bullish'
                confidence = min(abs(slope) / sma[0] * 100, 100) if sma[0] > 0 else 50
            elif slope < 0:
                trend = 'bearish'
                confidence = min(abs(slope) / sma[0] * 100, 100) if sma[0] > 0 else 50
            else:
                confidence = 50
        
        return {
            'trend': trend,
            'confidence': round(confidence, 2),
            'sma': sma[-1] if sma else None,
            'current_price': closes[-1] if closes else None,
            'price_to_sma_ratio': round(closes[-1] / sma[-1], 4) if sma and closes else None
        } 