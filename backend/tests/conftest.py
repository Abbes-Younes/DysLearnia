"""
tests/conftest.py — Shared pytest configuration.

Sets pytest-asyncio mode to "auto" so all async test functions are
discovered and run without needing the @pytest.mark.asyncio decorator.
"""
import sys
import os

# Ensure backend/ is on the Python path for all tests
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
