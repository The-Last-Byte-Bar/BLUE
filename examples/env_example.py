"""
Example demonstrating how to use environment variables from the .env file.
"""

import logging
import sys
from utils.env_loader import load_env_vars, get_api_key, get_env_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

def main():
    # Load environment variables from .env file
    load_env_vars()
    
    # Get environment configuration
    env_config = get_env_config()
    logger.info(f"Running in {env_config['environment']} environment")
    logger.info(f"Debug mode: {env_config['debug']}")
    logger.info(f"Log level: {env_config['log_level']}")
    
    # Example of getting API keys
    try:
        # Get required API key (will raise ValueError if not found)
        openai_api_key = get_api_key("OPENAI_API_KEY")
        logger.info("Successfully loaded OpenAI API key")
        
        # Get optional API key (returns None if not found)
        twitter_api_key = get_api_key("TWITTER_API_KEY", required=False)
        if twitter_api_key:
            logger.info("Successfully loaded Twitter API key")
        else:
            logger.info("Twitter API key not found, social features will be disabled")
            
    except ValueError as e:
        logger.error(f"Error loading API keys: {e}")
        return
    
    # Your application code that uses the API keys would go here
    logger.info("Application running with proper API key configuration")

if __name__ == "__main__":
    main() 