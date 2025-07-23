"""
CLI entry point for eToro Extractor when installed as a package.
"""

import sys
import os

def main():
    """Main entry point for the etoro command."""
    # Import the main CLI function
    from etoro_extractor.main import cli
    
    # Run the CLI
    cli()
