#!/usr/bin/env python
"""
Simplified test runner for the LLM integration module.

This script runs the unit tests directly using pytest's API but with minimal plugin loading.
"""

import os
import sys
import subprocess
import importlib.util


def ensure_pytest_asyncio():
    """Ensure pytest-asyncio is installed."""
    try:
        import pytest_asyncio
        print("pytest-asyncio is already installed.")
        return True
    except ImportError:
        print("pytest-asyncio is not installed. Installing now...")
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", "pytest-asyncio"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            print(result.stdout)
            if result.stderr:
                print("Warnings/Errors:", result.stderr)
            
            # Verify installation
            try:
                import pytest_asyncio
                print("pytest-asyncio successfully installed.")
                return True
            except ImportError:
                print("Failed to import pytest-asyncio after installation.")
                return False
        except subprocess.CalledProcessError as e:
            print(f"Failed to install pytest-asyncio: {e}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            return False


def create_pytest_ini():
    """Create a pytest.ini file to properly configure asyncio."""
    ini_content = """
[pytest]
asyncio_mode = auto
markers =
    asyncio: mark a test as an asyncio coroutine
"""
    
    with open("pytest.ini", "w") as f:
        f.write(ini_content.strip())
    print("Created pytest.ini with asyncio configuration.")


def run_tests():
    """Run tests using direct subprocess call to avoid plugin loading issues."""
    # Get the directory of this script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project root directory
    os.chdir(script_dir)
    
    # Print a header
    print("\n" + "=" * 80)
    print("RUNNING TESTS FOR LLM INTEGRATION MODULE".center(80))
    print("=" * 80 + "\n")
    
    # Make sure we have the asyncio plugin
    asyncio_installed = ensure_pytest_asyncio()
    
    # Create pytest.ini if it doesn't exist
    if not os.path.exists("pytest.ini"):
        create_pytest_ini()
    
    # Run pytest directly with subprocess
    # Note: Command line arguments to pytest are different from pytest.main() args
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_llm_client.py",
        "tests/test_context_builder.py", 
        "tests/test_blockchain_analyzer.py",
        "tests/test_integration.py",
        "-v",  # Verbose output
        "--no-header",  # No header
        "-p", "no:dash",  # Disable dash plugin
    ]
    
    # Add asyncio mode if the plugin is installed
    if asyncio_installed:
        cmd.append("--asyncio-mode=auto")
    
    print("Running command:", " ".join(cmd))
    result = subprocess.run(cmd, env=os.environ.copy())
    
    # Print a footer
    print("\n" + "=" * 80)
    if result.returncode == 0:
        print("ALL TESTS PASSED!".center(80))
    else:
        print(f"TESTS FAILED WITH EXIT CODE {result.returncode}".center(80))
    print("=" * 80 + "\n")
    
    return result.returncode


if __name__ == "__main__":
    sys.exit(run_tests()) 