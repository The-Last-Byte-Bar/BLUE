"""
Environment variable loader utility.

This module provides functions to load environment variables from a .env file
using the python-dotenv package.
"""

import os
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

def load_env_vars(env_file_path: Optional[str] = None) -> None:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file_path: Optional path to the .env file. If not provided,
                      it will look for a .env file in the project root.
    """
    # If no path is provided, look for .env in the project root
    if env_file_path is None:
        # Get the project root directory (assumes this file is in utils/ directory)
        project_root = Path(__file__).parent.parent
        env_file_path = project_root / ".env"
    
    # Load the environment variables from the .env file
    if os.path.exists(env_file_path):
        load_dotenv(env_file_path)
        logger.info(f"Loaded environment variables from {env_file_path}")
    else:
        logger.warning(f".env file not found at {env_file_path}. Using system environment variables.")

def get_api_key(key_name: str, required: bool = True) -> Optional[str]:
    """
    Get an API key from environment variables.
    
    Args:
        key_name: The name of the environment variable containing the API key.
        required: Whether the API key is required. If True and the key is not found,
                 a ValueError will be raised.
    
    Returns:
        The API key value if found, None otherwise.
        
    Raises:
        ValueError: If the API key is required but not found.
    """
    api_key = os.environ.get(key_name)
    
    if api_key is None or api_key.startswith("your_") or api_key == "":
        if required:
            raise ValueError(f"Required API key '{key_name}' not found in environment variables. "
                           f"Please add it to your .env file or set it as an environment variable.")
        return None
    
    return api_key

def get_env_config() -> Dict[str, Any]:
    """
    Get environment configuration values.
    
    Returns:
        A dictionary containing environment configuration values.
    """
    return {
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "debug": os.environ.get("DEBUG", "True").lower() in ("true", "1", "yes"),
        "log_level": os.environ.get("LOG_LEVEL", "INFO"),
    } 