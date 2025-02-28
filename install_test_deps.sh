#!/bin/bash
# Script to install necessary dependencies for running the tests without relying on conda

echo "Installing test dependencies for LLM module..."

# Install test dependencies
pip install pytest==7.3.1 pytest-asyncio==0.21.0 pytest-cov

# Install specific versions of Flask and Werkzeug to avoid compatibility issues
pip install werkzeug==2.0.3 flask==2.0.3

# Install other dependencies that might be needed
pip install aiohttp python-dotenv pydantic anthropic

echo "Dependencies installed. You can now run tests with:"
echo "  ./run_with_conda.sh"
echo "or"
echo "  python simple_test_runner.py" 