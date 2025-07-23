#!/usr/bin/env python3
"""
eToro Extractor - Main Application Entry Point

A Python backend application for extracting data from eToro.
"""

import os
from dotenv import load_dotenv

def main():
    """Main application entry point."""
    # Load environment variables
    load_dotenv()
    
    print("eToro Extractor - Starting application...")
    print(f"Python version: {os.sys.version}")
    print("Application initialized successfully!")
    
    # TODO: Add your main application logic here
    

if __name__ == "__main__":
    main()
