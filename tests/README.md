# LLM Integration Module Testing

This directory contains tests for the LLM integration module, which provides natural language interfaces for blockchain data analysis.

## Test Files

- **test_llm_client.py**: Tests for the LLM client classes (`ClaudeClient`, `OllamaClient`, `LLMClientFactory`)
- **test_context_builder.py**: Tests for the `ContextBuilder` class that manages conversation context
- **test_blockchain_analyzer.py**: Tests for the `BlockchainAnalyzer` class and its analysis methods
- **test_integration.py**: Integration tests that verify the proper interaction between components

## Running Tests

There are several ways to run the tests:

### 1. Using the run_tests.sh script (Recommended)

This script creates a temporary virtual environment with all the necessary dependencies and runs the tests:

```bash
./run_tests.sh
```

### 2. Using the run_with_conda.sh script

If you have conda installed, you can use this script to run the tests in a conda environment:

```bash
./run_with_conda.sh [environment_name]
```

If no environment name is provided, it defaults to 'pool'.

### 3. Using the simple_test_runner.py script

This script runs the tests directly using pytest's API:

```bash
python simple_test_runner.py
```

### 4. Using pytest directly

If you have pytest and all dependencies installed, you can run the tests directly:

```bash
python -m pytest tests/
```

## Environment Variables

The tests use mock environment variables for testing, but if you want to run tests against real APIs, you can set:

- `ANTHROPIC_API_KEY`: API key for Claude
- `OLLAMA_API_URL`: URL for Ollama API (default: http://localhost:11434)

## Adding New Tests

When adding new tests:

1. Use the appropriate test file based on what you're testing
2. For async tests, use the `@pytest.mark.asyncio` decorator
3. Use the `mock_env_variables` fixture for tests that need environment variables
4. Use mocks for external dependencies to avoid actual API calls

## Test Dependencies

The tests require:

- pytest
- pytest-asyncio
- pytest-cov (for coverage reports)
- aiohttp
- anthropic
- pydantic

You can install these with:

```bash
pip install pytest pytest-asyncio pytest-cov aiohttp anthropic pydantic
``` 