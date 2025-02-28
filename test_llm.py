#!/usr/bin/env python
"""
Test runner script specifically for the LLM integration module.

This script runs the unit tests for the LLM integration components.
"""

import os
import sys
import pytest


def run_tests():
    """Run all LLM-related unit tests."""
    # Add any custom test arguments here
    args = [
        "--verbose",
        "-xvs",  # Exit on first failure, verbose, don't capture output
        "--asyncio-mode=auto",  # Auto-detect the appropriate asyncio mode
        "tests/test_llm_client.py",
        "tests/test_context_builder.py",
        "tests/test_blockchain_analyzer.py",
        "tests/test_integration.py"
    ]
    
    # Run the tests and get the exit code
    exit_code = pytest.main(args)
    
    return exit_code


if __name__ == "__main__":
    # Print a header
    print("\n" + "=" * 80)
    print("RUNNING TESTS FOR LLM INTEGRATION MODULE".center(80))
    print("=" * 80 + "\n")
    
    # Run the tests
    result = run_tests()
    
    # Print a footer
    print("\n" + "=" * 80)
    if result == 0:
        print("ALL TESTS PASSED!".center(80))
    else:
        print(f"TESTS FAILED WITH EXIT CODE {result}".center(80))
    print("=" * 80 + "\n")
    
    # Exit with the appropriate code
    sys.exit(result) 