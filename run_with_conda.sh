#!/bin/bash
# Script to run tests with proper conda environment activation

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Define environment name (use the one passed as argument or default to 'pool')
ENV_NAME=${1:-pool}

# Determine conda location - try several common paths
CONDA_PATHS=(
  "$HOME/miniconda3/etc/profile.d/conda.sh"
  "$HOME/anaconda3/etc/profile.d/conda.sh"
  "/opt/conda/etc/profile.d/conda.sh"
  "/usr/local/anaconda/etc/profile.d/conda.sh"
)

CONDA_FOUND=0
for path in "${CONDA_PATHS[@]}"; do
  if [ -f "$path" ]; then
    echo "Found conda at $path"
    source "$path"
    CONDA_FOUND=1
    break
  fi
done

if [ $CONDA_FOUND -eq 0 ]; then
  echo "Could not find conda. Using system Python."
else
  # List available environments
  echo "Available conda environments:"
  conda env list
  
  # Activate the conda environment
  echo "Activating conda environment '$ENV_NAME'..."
  conda activate $ENV_NAME
  if [ $? -ne 0 ]; then
    echo "Error activating conda environment '$ENV_NAME'. Check if it exists."
    echo "Would you like to:"
    echo "1) Create the '$ENV_NAME' environment"
    echo "2) Continue with system Python"
    echo "3) Exit"
    read -p "Choose an option (1-3): " option
    
    case $option in
      1)
        echo "Creating conda environment '$ENV_NAME'..."
        conda create -y -n $ENV_NAME python=3.10
        conda activate $ENV_NAME
        ;;
      2)
        echo "Continuing with system Python..."
        ;;
      3)
        echo "Exiting."
        exit 1
        ;;
      *)
        echo "Invalid option. Continuing with system Python..."
        ;;
    esac
  fi
fi

# Set mock environment variables for testing
export ANTHROPIC_API_KEY="mock-api-key-for-testing"
export OLLAMA_API_URL="http://mock-ollama:11434"

# Make sure pytest and pytest-asyncio are installed
echo "Checking for pytest and pytest-asyncio..."
python -c "import pytest; import pytest_asyncio" 2>/dev/null
if [ $? -ne 0 ]; then
  echo "Installing pytest and pytest-asyncio..."
  pip install pytest pytest-asyncio
fi

# Run the tests directly if simple_test_runner.py doesn't exist
if [ -f "simple_test_runner.py" ]; then
  echo "Running tests via simple_test_runner.py..."
  python simple_test_runner.py
else
  echo "Running tests directly with pytest..."
  python -m pytest tests/test_llm_client.py tests/test_context_builder.py tests/test_blockchain_analyzer.py tests/test_integration.py -v
fi

# Return the exit code from the test runner
EXIT_CODE=$?
echo "Tests completed with exit code $EXIT_CODE"

# Clean up
unset ANTHROPIC_API_KEY
unset OLLAMA_API_URL

exit $EXIT_CODE 