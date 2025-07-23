"""
Configuration module for eToro Extractor.
"""

import os
from typing import Optional


class Config:
    """Configuration class for eToro Extractor."""
    
    def __init__(self):
        self.debug = os.getenv('DEBUG', 'False').lower() == 'true'
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.default_username = os.getenv('ETORO_DEFAULT_USERNAME')
        
        # Browser settings
        self.browser_headless = os.getenv('BROWSER_HEADLESS', 'True').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', '30'))
        
        # eToro settings
        self.etoro_base_url = "https://www.etoro.com"
        self.etoro_public_profile_url = f"{self.etoro_base_url}/people/{{username}}"
    
    def get_profile_url(self, username: str) -> str:
        """Get the full profile URL for a given username."""
        return self.etoro_public_profile_url.format(username=username)
