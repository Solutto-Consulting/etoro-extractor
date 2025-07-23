"""
Web scraper module for extracting data from eToro using Selenium.
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

from .config import Config

logger = logging.getLogger(__name__)


class EToroScraper:
    """Web scraper for eToro public profiles."""
    
    def __init__(self, config: Config):
        self.config = config
        self.driver = None
    
    def _setup_driver(self):
        """Set up Chrome WebDriver with appropriate options."""
        chrome_options = Options()
        
        if self.config.browser_headless:
            chrome_options.add_argument("--headless=new")
        
        # Essential arguments for headless Chrome in various environments
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-ipc-flooding-protection")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        # Note: Don't disable JavaScript as eToro needs it
        chrome_options.add_argument("--remote-debugging-port=0")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Set additional preferences
        prefs = {
            "profile.default_content_setting_values": {
                "notifications": 2,
                "media_stream": 2,
            },
            "profile.managed_default_content_settings": {
                "images": 2
            }
        }
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        
        try:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.implicitly_wait(10)
        except Exception as e:
            logger.error(f"Failed to setup Chrome driver: {e}")
            
            # Try alternative approaches
            logger.info("Trying alternative Chrome setup...")
            
            # Try with different Chrome binary locations
            chrome_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable", 
                "/usr/bin/chromium-browser",
                "/usr/bin/chromium",
                "/snap/bin/chromium"
            ]
            
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    logger.info(f"Trying Chrome binary at: {chrome_path}")
                    chrome_options.binary_location = chrome_path
                    try:
                        service = Service(ChromeDriverManager().install())
                        self.driver = webdriver.Chrome(service=service, options=chrome_options)
                        self.driver.implicitly_wait(10)
                        logger.info(f"Successfully started Chrome with binary: {chrome_path}")
                        return
                    except Exception as inner_e:
                        logger.warning(f"Failed with {chrome_path}: {inner_e}")
                        continue
            
            # If all else fails, try with minimal options
            logger.info("Trying minimal Chrome options...")
            minimal_options = Options()
            minimal_options.add_argument("--headless=new")
            minimal_options.add_argument("--no-sandbox")
            minimal_options.add_argument("--disable-dev-shm-usage")
            
            try:
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=minimal_options)
                self.driver.implicitly_wait(10)
                logger.info("Successfully started Chrome with minimal options")
                return
            except Exception as final_e:
                logger.error(f"All Chrome setup attempts failed: {final_e}")
                raise RuntimeError("Could not start Chrome browser. Please ensure Chrome/Chromium is properly installed.")
    
    def __enter__(self):
        """Context manager entry."""
        self._setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self.driver:
            self.driver.quit()
    
    def get_portfolio_data(self, username: str) -> Optional[Dict[str, Any]]:
        """
        Extract portfolio data from a user's public profile.
        
        Args:
            username: eToro username
            
        Returns:
            Dictionary containing portfolio data or None if extraction fails
        """
        if not self.driver:
            raise RuntimeError("WebDriver not initialized. Use as context manager.")
        
        profile_url = self.config.get_profile_url(username)
        logger.info(f"Extracting portfolio data for {username} from {profile_url}")
        
        try:
            # Navigate to profile page
            self.driver.get(profile_url)
            
            # Wait for page to load and check if profile exists
            try:
                WebDriverWait(self.driver, self.config.browser_timeout).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
            except TimeoutException:
                logger.error(f"Timeout waiting for profile page to load: {profile_url}")
                return None
            
            # Check if profile is accessible (not private or doesn't exist)
            if "profile not found" in self.driver.page_source.lower() or \
               "private profile" in self.driver.page_source.lower():
                logger.warning(f"Profile {username} not found or is private")
                return None
            
            # Try to find and click portfolio tab
            try:
                # Wait a bit for the page to fully load
                time.sleep(5)
                
                # Check if there's a CAPTCHA present
                captcha_selectors = [
                    "iframe[src*='captcha']",
                    ".captcha",
                    "#captcha",
                    "[class*='captcha']"
                ]
                
                captcha_present = False
                for selector in captcha_selectors:
                    try:
                        captcha_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                        if captcha_element.is_displayed():
                            logger.warning("CAPTCHA detected on the page. Portfolio extraction may be limited.")
                            captcha_present = True
                            break
                    except:
                        continue
                
                if captcha_present:
                    logger.info("Attempting to extract data despite CAPTCHA presence...")
                    # Try to wait for CAPTCHA to disappear or timeout
                    for i in range(6):  # Wait up to 30 seconds
                        time.sleep(5)
                        try:
                            # Check if CAPTCHA is still present
                            still_present = False
                            for selector in captcha_selectors:
                                try:
                                    captcha_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                                    if captcha_element.is_displayed():
                                        still_present = True
                                        break
                                except:
                                    continue
                            
                            if not still_present:
                                logger.info("CAPTCHA appears to have cleared")
                                break
                        except:
                            break
                    
                # Look for portfolio tab/section - try multiple approaches
                portfolio_selectors = [
                    "a[href*='portfolio']",
                    "[data-etoro-automation-id='portfolio-tab']",
                    "button[aria-label*='Portfolio']",
                    ".portfolio-tab",
                    "[class*='portfolio']",
                    "a[automation-id*='portfolio']",
                    ".et-tab[href*='portfolio']"
                ]
                
                portfolio_element = None
                for selector in portfolio_selectors:
                    try:
                        elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for element in elements:
                            if element.is_displayed() and element.is_enabled():
                                portfolio_element = element
                                logger.info(f"Found portfolio element with selector: {selector}")
                                break
                        if portfolio_element:
                            break
                    except Exception as e:
                        logger.debug(f"Selector {selector} failed: {e}")
                        continue
                
                if portfolio_element:
                    try:
                        # Scroll to element first
                        self.driver.execute_script("arguments[0].scrollIntoView(true);", portfolio_element)
                        time.sleep(2)
                        
                        # Try to click
                        portfolio_element.click()
                        logger.info("Successfully clicked portfolio tab")
                        time.sleep(5)  # Wait for portfolio content to load
                    except Exception as click_error:
                        logger.warning(f"Could not click portfolio tab: {click_error}")
                        # Try JavaScript click as fallback
                        try:
                            self.driver.execute_script("arguments[0].click();", portfolio_element)
                            logger.info("Successfully clicked portfolio tab using JavaScript")
                            time.sleep(5)
                        except Exception as js_error:
                            logger.warning(f"JavaScript click also failed: {js_error}")
                else:
                    logger.warning("No portfolio tab found, will try to extract from current page")
                
            except Exception as e:
                logger.warning(f"Error handling portfolio tab: {e}")
            
            # Extract portfolio data from the page
            return self._extract_portfolio_from_page()
            
        except WebDriverException as e:
            logger.error(f"WebDriver error while extracting portfolio: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error while extracting portfolio: {e}")
            return None
    
    def _extract_portfolio_from_page(self) -> Dict[str, Any]:
        """
        Extract portfolio information from the current page.
        
        Returns:
            Dictionary containing extracted portfolio data
        """
        portfolio_data = {
            "user": None,
            "last_updated": None,
            "total_assets": 0,
            "assets": []
        }
        
        try:
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract username from page
            username_selectors = [
                ".username",
                "[data-etoro-automation-id='people-avatar-name']",
                ".people-header h1",
                "h1"
            ]
            
            for selector in username_selectors:
                username_element = soup.select_one(selector)
                if username_element:
                    portfolio_data["user"] = username_element.get_text(strip=True)
                    break
            
            # Look for portfolio items/assets
            asset_selectors = [
                ".portfolio-item",
                ".investment-item",
                "[class*='portfolio'] [class*='item']",
                ".table-row",
                "tr[data-etoro-automation-id*='portfolio']"
            ]
            
            assets = []
            for selector in asset_selectors:
                asset_elements = soup.select(selector)
                if asset_elements:
                    for element in asset_elements:
                        asset_info = self._extract_asset_info(element)
                        if asset_info:
                            assets.append(asset_info)
                    break
            
            # If no assets found with specific selectors, try to find any investment-related content
            if not assets:
                # Look for any text that might indicate assets/investments
                text_content = soup.get_text()
                if any(term in text_content.lower() for term in ['invested', 'portfolio', 'assets', 'stocks']):
                    # Try to extract basic information from visible text
                    assets = self._extract_assets_from_text(text_content)
            
            portfolio_data["assets"] = assets
            portfolio_data["total_assets"] = len(assets)
            
            # Try to find last updated information
            update_selectors = [
                ".last-updated",
                "[class*='update']",
                ".timestamp"
            ]
            
            for selector in update_selectors:
                update_element = soup.select_one(selector)
                if update_element:
                    portfolio_data["last_updated"] = update_element.get_text(strip=True)
                    break
            
            logger.info(f"Extracted {len(assets)} assets from portfolio")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error extracting portfolio data: {e}")
            return portfolio_data
    
    def _extract_asset_info(self, element) -> Optional[Dict[str, Any]]:
        """
        Extract asset information from a single portfolio item element.
        
        Args:
            element: BeautifulSoup element containing asset information
            
        Returns:
            Dictionary with asset information or None
        """
        try:
            asset_info = {}
            
            # Extract asset name/symbol
            name_selectors = [".asset-name", ".symbol", ".instrument-name", "h3", "h4", ".name"]
            for selector in name_selectors:
                name_element = element.select_one(selector)
                if name_element:
                    asset_info["name"] = name_element.get_text(strip=True)
                    break
            
            # Extract percentage/allocation
            percentage_selectors = [".percentage", ".allocation", "[class*='percent']"]
            for selector in percentage_selectors:
                pct_element = element.select_one(selector)
                if pct_element:
                    asset_info["percentage"] = pct_element.get_text(strip=True)
                    break
            
            # Extract value if available
            value_selectors = [".value", ".amount", "[class*='value']", "[class*='amount']"]
            for selector in value_selectors:
                value_element = element.select_one(selector)
                if value_element:
                    asset_info["value"] = value_element.get_text(strip=True)
                    break
            
            # Extract P/L if available
            pl_selectors = [".profit-loss", ".pl", "[class*='profit']", "[class*='loss']"]
            for selector in pl_selectors:
                pl_element = element.select_one(selector)
                if pl_element:
                    asset_info["profit_loss"] = pl_element.get_text(strip=True)
                    break
            
            # Only return if we have at least a name
            return asset_info if asset_info.get("name") else None
            
        except Exception as e:
            logger.error(f"Error extracting asset info: {e}")
            return None
    
    def _extract_assets_from_text(self, text_content: str) -> list:
        """
        Fallback method to extract basic asset information from page text.
        
        Args:
            text_content: Full text content of the page
            
        Returns:
            List of basic asset information
        """
        # This is a fallback method - implementation would depend on 
        # the actual structure of the eToro pages
        assets = []
        
        # Look for common asset patterns in text
        import re
        
        # Simple pattern matching for potential asset names
        lines = text_content.split('\n')
        for line in lines:
            line = line.strip()
            if line and len(line) < 50:  # Reasonable asset name length
                # Look for percentage patterns
                if '%' in line or 'invested' in line.lower():
                    assets.append({
                        "name": line,
                        "extracted_from": "text_fallback"
                    })
        
        return assets[:10]  # Limit to first 10 potential matches
