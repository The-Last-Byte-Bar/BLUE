#!/bin/bash
# Script to run tests with proper setup

echo "=== LLM Integration Module Test Runner ==="
echo

# Set mock environment variables for testing
export ANTHROPIC_API_KEY="mock-api-key-for-testing"
export OLLAMA_API_URL="http://mock-ollama:11434"

# Create a temporary virtual environment for testing
echo "Creating a temporary virtual environment for testing..."
python -m venv .test_venv

# Activate the virtual environment
echo "Activating virtual environment..."
source ./.test_venv/bin/activate

# Install dependencies
echo "Installing test dependencies..."
pip install pytest==7.3.1 pytest-asyncio==0.21.0 pytest-cov
pip install werkzeug==2.0.3 flask==2.0.3
pip install aiohttp python-dotenv pydantic anthropic

# Create pytest.ini if it doesn't exist
if [ ! -f pytest.ini ]; then
  echo "Creating pytest.ini..."
  cat > pytest.ini << EOL
[pytest]
asyncio_mode = auto
markers =
    asyncio: mark a test as an asyncio coroutine
EOL
fi

# Run the tests
echo "Running tests..."
python -m pytest tests/test_llm_client.py tests/test_context_builder.py tests/test_blockchain_analyzer.py tests/test_integration.py -v

# Check the result
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
  echo
  echo "=== All tests passed! ==="
else
  echo
  echo "=== Some tests failed ==="
fi

# Deactivate virtual environment
deactivate

# Clean up environment variables
unset ANTHROPIC_API_KEY
unset OLLAMA_API_URL

# Optionally remove the temporary virtual environment
read -p "Remove temporary virtual environment? (y/n): " remove_venv
if [ "$remove_venv" == "y" ]; then
  echo "Removing temporary virtual environment..."
  rm -rf .test_venv
  echo "Virtual environment removed."
else
  echo "Virtual environment kept at ./.test_venv"
fi

exit $EXIT_CODE 