#!/usr/bin/env python3
"""
Simple test script to verify eToro Extractor functionality
"""

import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from etoro_extractor.config import Config
from etoro_extractor.formatters import format_portfolio_table, format_portfolio_json


class TestEToroExtractor(unittest.TestCase):
    """Basic tests for eToro Extractor functionality."""
    
    def test_config_initialization(self):
        """Test that Config class initializes correctly."""
        config = Config()
        self.assertIsInstance(config.browser_headless, bool)
        self.assertIsInstance(config.browser_timeout, int)
        self.assertIn('etoro.com', config.etoro_base_url)
    
    def test_profile_url_generation(self):
        """Test profile URL generation."""
        config = Config()
        url = config.get_profile_url('testuser')
        self.assertIn('testuser', url)
        self.assertIn('etoro.com', url)
    
    def test_portfolio_table_formatting(self):
        """Test portfolio table formatting."""
        sample_data = {
            'user': 'testuser',
            'total_assets': 2,
            'assets': [
                {'name': 'AAPL', 'percentage': '50%', 'value': '$1000'},
                {'name': 'GOOGL', 'percentage': '50%', 'value': '$1000'}
            ]
        }
        
        result = format_portfolio_table(sample_data)
        self.assertIn('testuser', result)
        self.assertIn('AAPL', result)
        self.assertIn('GOOGL', result)
    
    def test_portfolio_json_formatting(self):
        """Test portfolio JSON formatting."""
        sample_data = {
            'user': 'testuser',
            'total_assets': 1,
            'assets': [{'name': 'AAPL', 'percentage': '100%'}]
        }
        
        result = format_portfolio_json(sample_data)
        self.assertIn('"user"', result)
        self.assertIn('"AAPL"', result)
    
    def test_empty_portfolio_formatting(self):
        """Test formatting with empty portfolio."""
        empty_data = {'user': 'testuser', 'total_assets': 0, 'assets': []}
        
        table_result = format_portfolio_table(empty_data)
        self.assertIn('No assets found', table_result)


if __name__ == '__main__':
    print("Running eToro Extractor Tests...")
    print("=" * 40)
    
    # Run tests
    unittest.main(verbosity=2)
