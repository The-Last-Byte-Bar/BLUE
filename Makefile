.PHONY: test test-llm lint format clean docs help

# Default target
help:
	@echo "Available commands:"
	@echo "  make test       - Run all tests"
	@echo "  make test-llm   - Run only LLM-related tests"
	@echo "  make lint       - Run linting checks"
	@echo "  make format     - Format code with black"
	@echo "  make clean      - Clean up build artifacts"
	@echo "  make docs       - Build documentation"

# Run all tests
test:
	@echo "Running all tests..."
	python simple_test_runner.py

# Run only LLM-related tests
test-llm:
	@echo "Running LLM integration tests..."
	python simple_test_runner.py

# Run linting
lint:
	@echo "Running linters..."
	flake8 llm/ tests/
	isort --check llm/ tests/

# Format code
format:
	@echo "Formatting code..."
	isort llm/ tests/
	black llm/ tests/

# Clean up build artifacts
clean:
	@echo "Cleaning up build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf docs/_build/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Build documentation
docs:
	@echo "Building documentation..."
	cd docs && make html 