"""
Social media data fetchers.

This module provides components for fetching and processing data from social media
sources related to cryptocurrencies and market participants.
"""

from typing import Dict, Any, List, Optional, Union
import logging
import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta

from .processor import DataSource

logger = logging.getLogger(__name__)


class SocialDataFetcher(DataSource):
    """Fetcher for social media data."""

    def __init__(self, base_url: str, api_key: str, platforms: Optional[List[str]] = None):
        """
        Initialize the social data fetcher.

        Args:
            base_url: Base URL for the social media API
            api_key: API key for authentication
            platforms: Optional list of platforms to fetch from (defaults to all available)
        """
        self.base_url = base_url
        self.api_key = api_key
        self.platforms = platforms or ['twitter', 'reddit', 'telegram']
        self.session = None
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = timedelta(minutes=15)  # Social data updates frequently

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
        Make a request to the social media API.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response data as a dictionary
        """
        session = await self._get_session()
        headers = {
            'X-API-Key': self.api_key
        }
        
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        async with session.get(url, params=params, headers=headers) as response:
            if response.status >= 400:
                error_text = await response.text()
                raise Exception(f"Social API error ({response.status}): {error_text}")
            
            return await response.json()

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch social media data.

        Args:
            **kwargs: Parameters for the social data fetch:
                - query: Search query or hashtag
                - platforms: Optional list of platforms to fetch from (overrides init)
                - limit: Optional maximum number of posts to fetch per platform
                - start_time: Optional start time for posts
                - end_time: Optional end time for posts

        Returns:
            Dictionary of fetched social media data
        """
        query = kwargs.get('query')
        if not query:
            return {'posts': []}
        
        platforms = kwargs.get('platforms', self.platforms)
        limit = kwargs.get('limit', 50)
        start_time = kwargs.get('start_time')
        end_time = kwargs.get('end_time')
        
        cache_key = f"social_{query}_{','.join(platforms)}_{limit}_{start_time}_{end_time}"
        
        if self._is_cached(cache_key):
            return self.cache[cache_key]
        
        result = {'posts': []}
        tasks = []
        
        for platform in platforms:
            task = self._fetch_platform_data(platform, query, limit, start_time, end_time)
            tasks.append(task)
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, platform in enumerate(platforms):
            if isinstance(platform_results[i], Exception):
                logger.error(f"Error fetching data from {platform}: {str(platform_results[i])}")
            else:
                result['posts'].extend(platform_results[i])
        
        # Sort posts by timestamp
        result['posts'] = sorted(result['posts'], key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Calculate basic metrics
        result['total_posts'] = len(result['posts'])
        result['platform_distribution'] = {}
        
        for post in result['posts']:
            platform = post.get('platform')
            if platform:
                if platform not in result['platform_distribution']:
                    result['platform_distribution'][platform] = 0
                result['platform_distribution'][platform] += 1
        
        self._cache_item(cache_key, result)
        
        return result

    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the fetched social media data.

        Args:
            data: Raw social media data to process

        Returns:
            Processed social media data
        """
        posts = data.get('posts', [])
        processed = {
            'posts': posts,
            'total_posts': data.get('total_posts', 0),
            'platform_distribution': data.get('platform_distribution', {})
        }
        
        # Extract frequently mentioned assets
        asset_mentions = self._extract_asset_mentions(posts)
        processed['asset_mentions'] = asset_mentions
        
        # Extract trending hashtags
        hashtags = self._extract_hashtags(posts)
        processed['trending_hashtags'] = hashtags
        
        # Calculate post velocity (posts per hour)
        timestamps = [datetime.fromisoformat(post['timestamp'].replace('Z', '+00:00')) 
                      for post in posts if 'timestamp' in post]
        
        if timestamps:
            min_time = min(timestamps)
            max_time = max(timestamps)
            time_diff = (max_time - min_time).total_seconds()
            
            if time_diff > 0:
                hours = time_diff / 3600
                processed['post_velocity'] = round(len(timestamps) / hours, 2)
            else:
                processed['post_velocity'] = len(timestamps)
        else:
            processed['post_velocity'] = 0
        
        return processed

    async def _fetch_platform_data(self, platform: str, query: str, limit: int, start_time: Optional[str], end_time: Optional[str]) -> List[Dict[str, Any]]:
        """
        Fetch data from a specific social media platform.

        Args:
            platform: Platform to fetch from
            query: Search query or hashtag
            limit: Maximum number of posts to fetch
            start_time: Optional start time for posts
            end_time: Optional end time for posts

        Returns:
            List of posts from the platform
        """
        params = {
            'query': query,
            'limit': limit
        }
        
        if start_time:
            params['start_time'] = start_time
        
        if end_time:
            params['end_time'] = end_time
        
        data = await self._make_request(f"api/v1/{platform}/search", params)
        
        posts = []
        for item in data.get('data', []):
            if 'id' in item and 'text' in item:
                post = {
                    'id': item['id'],
                    'platform': platform,
                    'text': item['text'],
                    'username': item.get('username', 'unknown'),
                    'timestamp': item.get('created_at', datetime.now().isoformat()),
                    'likes': item.get('likes', 0),
                    'shares': item.get('shares', 0),
                    'comments': item.get('comments', 0),
                    'url': item.get('url')
                }
                posts.append(post)
        
        return posts

    def _extract_asset_mentions(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract cryptocurrency asset mentions from posts.

        Args:
            posts: List of social media posts

        Returns:
            Dictionary mapping asset symbols to mention counts
        """
        # Common cryptocurrency symbols to look for
        crypto_symbols = ['BTC', 'ETH', 'XRP', 'LTC', 'BCH', 'ADA', 'DOT', 'LINK', 'BNB', 'XLM',
                         'DOGE', 'USDT', 'USDC', 'UNI', 'AAVE', 'SOL', 'MATIC', 'ALGO', 'ERG']
        
        mentions = {}
        
        for post in posts:
            text = post.get('text', '').upper()
            
            for symbol in crypto_symbols:
                pattern = r'\b' + symbol + r'\b'
                if re.search(pattern, text):
                    if symbol not in mentions:
                        mentions[symbol] = 0
                    mentions[symbol] += 1
        
        # Sort by mention count
        return dict(sorted(mentions.items(), key=lambda x: x[1], reverse=True))

    def _extract_hashtags(self, posts: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Extract hashtags from posts.

        Args:
            posts: List of social media posts

        Returns:
            Dictionary mapping hashtags to occurrence counts
        """
        hashtags = {}
        
        for post in posts:
            text = post.get('text', '')
            # Find all hashtags in the text
            tags = re.findall(r'#(\w+)', text)
            
            for tag in tags:
                tag = tag.lower()
                if tag not in hashtags:
                    hashtags[tag] = 0
                hashtags[tag] += 1
        
        # Sort by occurrence count and take top 20
        sorted_hashtags = dict(sorted(hashtags.items(), key=lambda x: x[1], reverse=True)[:20])
        return sorted_hashtags

    def _is_cached(self, cache_key: str) -> bool:
        """
        Check if data is cached and not expired.

        Args:
            cache_key: Cache key to check

        Returns:
            True if cached and not expired, False otherwise
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
        Cache an item.

        Args:
            cache_key: Cache key
            item: Item to cache
        """
        self.cache[cache_key] = item
        self.cache_expiry[cache_key] = datetime.now() + self.cache_ttl
        
        # Limit cache size (keep most recent 50 items)
        if len(self.cache) > 50:
            oldest_key = min(self.cache_expiry.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.cache_expiry[oldest_key]


class InfluencerTracker:
    """
    Tracker for cryptocurrency influencers on social media.
    
    This class provides methods for tracking and analyzing posts from
    influential accounts in the cryptocurrency space.
    """

    def __init__(self, social_fetcher: SocialDataFetcher):
        """
        Initialize the influencer tracker.

        Args:
            social_fetcher: Social data fetcher
        """
        self.fetcher = social_fetcher
        self.influencers = {
            'twitter': [
                'elonmusk',
                'VitalikButerin',
                'cz_binance',
                'SatoshiLite',
                'APompliano',
                'adam3us',
                'aantonop',
                'PeterSchiff',
                'michaeljburry',
                'CaitlinLong_'
            ],
            'reddit': [
                'vbuterin',
                'nullc',
                'Antonop',
                'ThePiGuy'
            ]
        }

    async def track_influencers(self, platform: str, limit_per_user: int = 10) -> Dict[str, Any]:
        """
        Track recent posts from influencers on a platform.

        Args:
            platform: Platform to track (twitter, reddit)
            limit_per_user: Maximum number of posts to fetch per user

        Returns:
            Dictionary with influencer tracking data
        """
        if platform not in self.influencers:
            return {'error': f"Platform {platform} not supported"}
        
        users = self.influencers[platform]
        all_posts = []
        
        for username in users:
            try:
                posts = await self._fetch_user_posts(platform, username, limit_per_user)
                all_posts.extend(posts)
            except Exception as e:
                logger.error(f"Error fetching posts for {username} on {platform}: {str(e)}")
        
        # Sort by timestamp
        all_posts = sorted(all_posts, key=lambda x: x.get('timestamp', ''), reverse=True)
        
        result = {
            'platform': platform,
            'influencer_count': len(users),
            'total_posts': len(all_posts),
            'posts': all_posts
        }
        
        return result

    async def _fetch_user_posts(self, platform: str, username: str, limit: int) -> List[Dict[str, Any]]:
        """
        Fetch posts from a specific user.

        Args:
            platform: Platform to fetch from
            username: Username to fetch
            limit: Maximum number of posts to fetch

        Returns:
            List of posts from the user
        """
        endpoint = f"api/v1/{platform}/user/{username}"
        params = {'limit': limit}
        
        try:
            data = await self.fetcher._make_request(endpoint, params)
            
            posts = []
            for item in data.get('data', []):
                if 'id' in item and 'text' in item:
                    post = {
                        'id': item['id'],
                        'platform': platform,
                        'text': item['text'],
                        'username': username,
                        'timestamp': item.get('created_at', datetime.now().isoformat()),
                        'likes': item.get('likes', 0),
                        'shares': item.get('shares', 0),
                        'comments': item.get('comments', 0),
                        'url': item.get('url')
                    }
                    posts.append(post)
            
            return posts
        except Exception as e:
            logger.error(f"Error fetching user data for {username} on {platform}: {str(e)}")
            return [] 