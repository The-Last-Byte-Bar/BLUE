"""
Sentiment analysis module.

This module provides components for analyzing sentiment in text data
related to cryptocurrencies and market participants.
"""

from typing import Dict, Any, List, Optional, Union, Tuple
import logging
import re
import asyncio
from datetime import datetime, timedelta

from data.processor import DataSource
from llm.client import LLMClient

logger = logging.getLogger(__name__)


class SentimentAnalyzer(DataSource):
    """Analyzer for sentiment in text data."""

    def __init__(self, llm_client: LLMClient):
        """
        Initialize the sentiment analyzer.

        Args:
            llm_client: LLM client for sentiment analysis
        """
        self.llm_client = llm_client
        self.cache = {}
        self.cache_expiry = {}
        self.cache_ttl = timedelta(hours=1)

    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch sentiment data.

        Args:
            **kwargs: Parameters for the sentiment analysis:
                - texts: List of texts to analyze
                - source: Optional source of the texts
                - asset: Optional asset the texts are related to

        Returns:
            Dictionary of sentiment data
        """
        texts = kwargs.get('texts', [])
        source = kwargs.get('source', 'unknown')
        asset = kwargs.get('asset')
        
        if not texts:
            return {'results': []}
        
        results = []
        batch_size = 5  # Process in batches to avoid overloading the LLM
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            batch_results = await self._analyze_batch(batch, source, asset)
            results.extend(batch_results)
        
        return {'results': results}

    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the sentiment data.

        Args:
            data: Raw sentiment data to process

        Returns:
            Processed sentiment data
        """
        results = data.get('results', [])
        
        if not results:
            return {
                'overall_sentiment': 'neutral',
                'sentiment_score': 0.0,
                'confidence': 0.0,
                'results': []
            }
        
        # Calculate average sentiment
        total_score = 0.0
        total_confidence = 0.0
        sentiment_counts = {'positive': 0, 'neutral': 0, 'negative': 0}
        
        for result in results:
            score = result.get('sentiment_score', 0.0)
            confidence = result.get('confidence', 0.5)
            sentiment = result.get('sentiment', 'neutral')
            
            total_score += score * confidence  # Weight by confidence
            total_confidence += confidence
            
            if sentiment in sentiment_counts:
                sentiment_counts[sentiment] += 1
        
        if total_confidence > 0:
            avg_score = total_score / total_confidence
        else:
            avg_score = 0.0
        
        # Determine overall sentiment
        overall_sentiment = 'neutral'
        max_count = max(sentiment_counts.values())
        for sentiment, count in sentiment_counts.items():
            if count == max_count:
                overall_sentiment = sentiment
                break
        
        # Overall confidence based on agreement
        total_items = len(results)
        if total_items > 0:
            agreement_confidence = max_count / total_items
        else:
            agreement_confidence = 0.0
        
        return {
            'overall_sentiment': overall_sentiment,
            'sentiment_score': round(avg_score, 2),
            'confidence': round(agreement_confidence, 2),
            'sentiment_distribution': sentiment_counts,
            'results': results
        }

    async def _analyze_batch(self, texts: List[str], source: str, asset: Optional[str]) -> List[Dict[str, Any]]:
        """
        Analyze a batch of texts.

        Args:
            texts: List of texts to analyze
            source: Source of the texts
            asset: Optional asset the texts are related to

        Returns:
            List of sentiment analysis results
        """
        results = []
        
        for text in texts:
            if not text or not text.strip():
                continue
            
            # Generate cache key
            cache_key = f"sentiment_{hash(text)}"
            
            if self._is_cached(cache_key):
                result = self.cache[cache_key]
            else:
                try:
                    sentiment, score, confidence = await self._analyze_text(text, asset)
                    
                    result = {
                        'text': text[:100] + ('...' if len(text) > 100 else ''),
                        'sentiment': sentiment,
                        'sentiment_score': score,
                        'confidence': confidence,
                        'source': source,
                        'asset': asset,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    self._cache_item(cache_key, result)
                except Exception as e:
                    logger.error(f"Error analyzing sentiment: {str(e)}")
                    result = {
                        'text': text[:100] + ('...' if len(text) > 100 else ''),
                        'sentiment': 'neutral',
                        'sentiment_score': 0.0,
                        'confidence': 0.0,
                        'source': source,
                        'asset': asset,
                        'timestamp': datetime.now().isoformat(),
                        'error': str(e)
                    }
            
            results.append(result)
        
        return results

    async def _analyze_text(self, text: str, asset: Optional[str] = None) -> Tuple[str, float, float]:
        """
        Analyze sentiment in a single text.

        Args:
            text: Text to analyze
            asset: Optional asset the text is related to

        Returns:
            Tuple of (sentiment, score, confidence)
        """
        # Default simple regex-based analysis for fallback
        simple_result = self._simple_sentiment_analysis(text)
        
        # Use LLM for deeper analysis if available
        try:
            prompt = self._create_sentiment_prompt(text, asset)
            response = await self.llm_client.generate(prompt)
            
            # Parse LLM response
            sentiment, score, confidence = self._parse_sentiment_response(response)
            
            return sentiment, score, confidence
        except Exception as e:
            logger.warning(f"Error using LLM for sentiment analysis, falling back to simple analysis: {str(e)}")
            return simple_result

    def _simple_sentiment_analysis(self, text: str) -> Tuple[str, float, float]:
        """
        Perform simple regex-based sentiment analysis.

        Args:
            text: Text to analyze

        Returns:
            Tuple of (sentiment, score, confidence)
        """
        text = text.lower()
        
        # Simple keyword matching
        positive_words = ['bullish', 'buy', 'moon', 'up', 'gain', 'profit', 'good', 'great', 
                         'excellent', 'positive', 'success', 'win', 'winning', 'growth']
        
        negative_words = ['bearish', 'sell', 'dump', 'down', 'loss', 'crash', 'bad', 'terrible', 
                          'poor', 'negative', 'fail', 'failure', 'scam', 'fear']
        
        positive_count = sum(1 for word in positive_words if re.search(r'\b' + word + r'\b', text))
        negative_count = sum(1 for word in negative_words if re.search(r'\b' + word + r'\b', text))
        
        total_count = positive_count + negative_count
        
        if total_count == 0:
            return 'neutral', 0.0, 0.5
        
        score = (positive_count - negative_count) / total_count
        
        if score > 0.2:
            sentiment = 'positive'
        elif score < -0.2:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Confidence based on keyword density
        confidence = min(0.3 + (total_count / len(text.split())) * 2, 0.7)  # Cap at 0.7 for simple analysis
        
        return sentiment, score, confidence

    def _create_sentiment_prompt(self, text: str, asset: Optional[str] = None) -> str:
        """
        Create a prompt for the LLM to analyze sentiment.

        Args:
            text: Text to analyze
            asset: Optional asset the text is related to

        Returns:
            Prompt for the LLM
        """
        asset_context = f" about {asset}" if asset else ""
        
        prompt = f"""
        Analyze the sentiment of the following text{asset_context}. 
        Determine if the sentiment is positive, neutral, or negative.
        Provide a sentiment score from -1.0 (extremely negative) to 1.0 (extremely positive).
        Also provide a confidence score from 0.0 to 1.0 indicating how confident you are in your assessment.
        
        Text to analyze: "{text}"
        
        Format your response exactly as follows:
        Sentiment: [positive/neutral/negative]
        Score: [score between -1.0 and 1.0]
        Confidence: [confidence between 0.0 and 1.0]
        """
        
        return prompt

    def _parse_sentiment_response(self, response: str) -> Tuple[str, float, float]:
        """
        Parse the LLM response for sentiment analysis.

        Args:
            response: LLM response

        Returns:
            Tuple of (sentiment, score, confidence)
        """
        # Default values
        sentiment = 'neutral'
        score = 0.0
        confidence = 0.5
        
        # Extract sentiment
        sentiment_match = re.search(r'Sentiment:\s*(positive|neutral|negative)', response, re.IGNORECASE)
        if sentiment_match:
            sentiment = sentiment_match.group(1).lower()
        
        # Extract score
        score_match = re.search(r'Score:\s*([-+]?\d*\.\d+|\d+)', response)
        if score_match:
            try:
                score = float(score_match.group(1))
                score = max(-1.0, min(1.0, score))  # Ensure it's in range
            except ValueError:
                pass
        
        # Extract confidence
        confidence_match = re.search(r'Confidence:\s*([-+]?\d*\.\d+|\d+)', response)
        if confidence_match:
            try:
                confidence = float(confidence_match.group(1))
                confidence = max(0.0, min(1.0, confidence))  # Ensure it's in range
            except ValueError:
                pass
        
        return sentiment, score, confidence

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
        
        # Limit cache size (keep most recent 1000 items)
        if len(self.cache) > 1000:
            oldest_key = min(self.cache_expiry.items(), key=lambda x: x[1])[0]
            del self.cache[oldest_key]
            del self.cache_expiry[oldest_key] 