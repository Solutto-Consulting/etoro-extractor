"""
Portfolio extraction module for eToro Extractor.
"""

import logging
from typing import Dict, Any, Optional

from .scraper import EToroScraper
from .config import Config

logger = logging.getLogger(__name__)


def get_portfolio(username: str, config: Config) -> Optional[Dict[str, Any]]:
    """
    Extract portfolio information for a given eToro username.
    
    Args:
        username: eToro username to extract portfolio from
        config: Configuration object
        
    Returns:
        Dictionary containing portfolio data or None if extraction fails
    """
    logger.info(f"Starting portfolio extraction for user: {username}")
    
    try:
        with EToroScraper(config) as scraper:
            portfolio_data = scraper.get_portfolio_data(username)
            
            if portfolio_data:
                logger.info(f"Successfully extracted portfolio with {portfolio_data['total_assets']} assets")
                return portfolio_data
            else:
                logger.warning(f"Failed to extract portfolio data for {username}")
                return None
                
    except Exception as e:
        logger.error(f"Error during portfolio extraction: {e}")
        raise
