#!/usr/bin/env python
"""
Test runner script for the LLM integration module.

This script runs the unit tests for all components of the LLM integration module.
"""

import os
import sys
import pytest


def main():
    """Run all unit tests."""
    # Ensure we're starting from the project root directory
    if os.path.exists('tests') and os.path.isdir('tests'):
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Add any custom test arguments here
    args = [
        "--verbose",  # Show more detailed output
        "-xvs",       # Exit on first failure, verbose, don't capture output
        "--asyncio-mode=auto",  # Auto-detect the appropriate asyncio mode
        "tests"       # Test directory to run
    ]
    
    # Run all the tests and get the exit code
    exit_code = pytest.main(args)
    
    # Exit with the appropriate code
    return exit_code


if __name__ == "__main__":
    sys.exit(main()) 