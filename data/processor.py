"""
Data processing core.

This module provides the core data processing functionality that integrates
different data handlers and provides methods for data aggregation and transformation.
"""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class DataSource(ABC):
    """Abstract base class for data sources."""

    @abstractmethod
    async def fetch_data(self, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from the source.

        Args:
            **kwargs: Additional arguments for the data fetch operation

        Returns:
            Dictionary of fetched data
        """
        pass

    @abstractmethod
    async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the fetched data.

        Args:
            data: Raw data to process

        Returns:
            Processed data
        """
        pass


class DataProcessor:
    """
    Core data processor that coordinates data sources and processing.
    
    This class manages multiple data sources, fetches and processes data,
    and provides methods for data aggregation and transformation.
    """

    def __init__(self):
        """Initialize the data processor."""
        self.data_sources: Dict[str, DataSource] = {}

    def register_data_source(self, name: str, source: DataSource) -> None:
        """
        Register a data source.

        Args:
            name: Name of the data source
            source: Data source instance
        """
        self.data_sources[name] = source
        logger.info(f"Registered data source: {name}")

    def unregister_data_source(self, name: str) -> None:
        """
        Unregister a data source.

        Args:
            name: Name of the data source to unregister
        """
        if name in self.data_sources:
            del self.data_sources[name]
            logger.info(f"Unregistered data source: {name}")
        else:
            logger.warning(f"Data source not found: {name}")

    async def fetch_from_source(self, source_name: str, **kwargs) -> Dict[str, Any]:
        """
        Fetch data from a specific source.

        Args:
            source_name: Name of the data source
            **kwargs: Additional arguments for the data fetch operation

        Returns:
            Dictionary of fetched data
        
        Raises:
            KeyError: If the data source is not registered
        """
        if source_name not in self.data_sources:
            raise KeyError(f"Data source not found: {source_name}")

        source = self.data_sources[source_name]
        logger.debug(f"Fetching data from source: {source_name}")
        
        try:
            data = await source.fetch_data(**kwargs)
            processed_data = await source.process_data(data)
            return processed_data
        except Exception as e:
            logger.error(f"Error fetching data from {source_name}: {str(e)}")
            raise

    async def fetch_all(self, **kwargs) -> Dict[str, Dict[str, Any]]:
        """
        Fetch data from all registered sources.

        Args:
            **kwargs: Additional arguments for the data fetch operation

        Returns:
            Dictionary mapping source names to their fetched data
        """
        tasks = []
        for name, source in self.data_sources.items():
            tasks.append(self.fetch_from_source(name, **kwargs))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Map source names to results
        data = {}
        for i, (name, _) in enumerate(self.data_sources.items()):
            if isinstance(results[i], Exception):
                logger.error(f"Error fetching data from {name}: {str(results[i])}")
                data[name] = None
            else:
                data[name] = results[i]
        
        return data

    def aggregate_data(self, data: Dict[str, Dict[str, Any]], aggregation_func: Callable) -> Dict[str, Any]:
        """
        Aggregate data from multiple sources.

        Args:
            data: Dictionary mapping source names to their data
            aggregation_func: Function to aggregate data

        Returns:
            Aggregated data
        """
        return aggregation_func(data)

    def transform_data(self, data: Dict[str, Any], transformation_func: Callable) -> Dict[str, Any]:
        """
        Transform data using a transformation function.

        Args:
            data: Data to transform
            transformation_func: Function to transform data

        Returns:
            Transformed data
        """
        return transformation_func(data) 