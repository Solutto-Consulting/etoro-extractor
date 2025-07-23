"""
Test configuration and fixtures for eToro Extractor tests.
"""

import pytest
import os
import sys

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def sample_data():
    """Sample test data fixture."""
    return {
        "test": "data"
    }
