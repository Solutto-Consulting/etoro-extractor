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
        # Don't disable images as we need to see portfolio avatars and data
        # chrome_options.add_argument("--disable-images")
        # Don't disable JavaScript as eToro is a SPA that requires JS
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
        Extract portfolio information from the current page using eToro-specific selectors.
        
        Returns:
            Dictionary containing extracted portfolio data
        """
        portfolio_data = {
            "user": None,
            "last_updated": None,
            "total_assets": 0,
            "assets": [],
            "balance_percentage": None
        }
        
        try:
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Extract username from URL or page elements
            current_url = self.driver.current_url
            if '/people/' in current_url:
                username_match = current_url.split('/people/')[1].split('/')[0]
                portfolio_data["user"] = username_match
            
            # Look for last updated date
            update_element = soup.select_one("[sub-head] .et-color-dark-grey")
            if update_element:
                update_text = update_element.get_text(strip=True)
                if "Last updated on:" in update_text:
                    portfolio_data["last_updated"] = update_text.replace("Last updated on:", "").strip()
            
            # Extract portfolio items using eToro-specific selectors
            portfolio_rows = soup.select(".et-table-row.clickable-row")
            assets = []
            
            logger.info(f"Found {len(portfolio_rows)} portfolio rows")
            
            for row in portfolio_rows:
                try:
                    asset_info = self._extract_etoro_asset_info(row)
                    if asset_info:
                        assets.append(asset_info)
                        logger.debug(f"Extracted asset: {asset_info.get('name', 'Unknown')}")
                except Exception as e:
                    logger.warning(f"Error extracting asset from row: {e}")
                    continue
            
            portfolio_data["assets"] = assets
            portfolio_data["total_assets"] = len(assets)
            
            # Extract balance percentage
            balance_element = soup.select_one("[automation-id='cd-public-portfolio-list-balance-label']")
            if balance_element:
                balance_parent = balance_element.find_parent()
                if balance_parent:
                    balance_value = balance_parent.select_one(".et-font-s")
                    if balance_value:
                        portfolio_data["balance_percentage"] = balance_value.get_text(strip=True)
            
            logger.info(f"Successfully extracted {len(assets)} assets from portfolio")
            return portfolio_data
            
        except Exception as e:
            logger.error(f"Error extracting portfolio data: {e}")
            return portfolio_data
    
    def _extract_etoro_asset_info(self, row_element) -> Optional[Dict[str, Any]]:
        """
        Extract asset information from a single eToro portfolio row element.
        
        Args:
            row_element: BeautifulSoup element containing the portfolio row
            
        Returns:
            Dictionary with asset information or None
        """
        try:
            asset_info = {}
            
            # Extract asset name from automation-id selector
            name_element = row_element.select_one("[automation-id='cd-public-portfolio-table-item-title']")
            if name_element:
                asset_info["name"] = name_element.get_text(strip=True)
            else:
                # Fallback to other selectors
                name_element = row_element.select_one(".et-bold-font.ellipsis")
                if name_element:
                    asset_info["name"] = name_element.get_text(strip=True)
            
            # Extract description/company name
            desc_element = row_element.select_one(".et-color-dark-grey.ellipsis")
            if desc_element:
                asset_info["description"] = desc_element.get_text(strip=True)
            
            # Extract direction (Long/Short) - in the first data cell
            direction_cell = row_element.select(".et-table-cell")[0] if row_element.select(".et-table-cell") else None
            if direction_cell:
                direction_element = direction_cell.select_one(".et-font-weight-normal")
                if direction_element:
                    direction = direction_element.get_text(strip=True)
                    if direction:
                        asset_info["direction"] = direction
            
            # Extract table cells for the data columns
            table_cells = row_element.select(".et-table-cell")
            
            if len(table_cells) >= 4:
                # Invested percentage (2nd column after direction)
                invested_cell = table_cells[1]
                invested_element = invested_cell.select_one(".et-font-weight-normal")
                if invested_element:
                    asset_info["invested_percentage"] = invested_element.get_text(strip=True)
                
                # P/L percentage (3rd column)
                pl_cell = table_cells[2] 
                pl_element = pl_cell.select_one(".et-font-weight-normal")
                if pl_element:
                    pl_value = pl_element.get_text(strip=True)
                    asset_info["profit_loss_percentage"] = pl_value
                    
                    # Determine if it's positive or negative based on class
                    if "et-positive" in pl_element.get("class", []):
                        asset_info["profit_loss_status"] = "positive"
                    elif "et-negative" in pl_element.get("class", []):
                        asset_info["profit_loss_status"] = "negative"
                
                # Value percentage (4th column)
                value_cell = table_cells[3]
                value_element = value_cell.select_one(".et-font-weight-normal")
                if value_element:
                    asset_info["value_percentage"] = value_element.get_text(strip=True)
                
                # Extract buy/sell prices if available (last columns)
                if len(table_cells) >= 6:
                    # Sell price
                    sell_cell = table_cells[4]
                    sell_price_element = sell_cell.select_one("[automation-id='buy-sell-button-rate-value']")
                    if sell_price_element:
                        asset_info["sell_price"] = sell_price_element.get_text(strip=True)
                    
                    # Buy price
                    buy_cell = table_cells[5]
                    buy_price_element = buy_cell.select_one("[automation-id='buy-sell-button-rate-value']")
                    if buy_price_element:
                        asset_info["buy_price"] = buy_price_element.get_text(strip=True)
            
            # Extract avatar/logo URL if present
            avatar_element = row_element.select_one("img[automation-id='trade-item-avatar']")
            if avatar_element and avatar_element.get("src"):
                asset_info["avatar_url"] = avatar_element["src"]
                asset_info["alt_text"] = avatar_element.get("alt", "")
            
            # Only return if we have at least a name
            return asset_info if asset_info.get("name") else None
            
        except Exception as e:
            logger.error(f"Error extracting eToro asset info: {e}")
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
    
    def _extract_available_data(self) -> Dict[str, Any]:
        """
        Extract whatever data is available when full access is restricted.
        
        Returns:
            Dictionary with limited available data
        """
        basic_data = {
            "user": None,
            "last_updated": None,
            "total_assets": 0,
            "assets": [],
            "access_restricted": True,
            "message": "Access may be restricted by CAPTCHA or anti-bot measures"
        }
        
        try:
            # Extract username from URL
            current_url = self.driver.current_url
            if '/people/' in current_url:
                username_match = current_url.split('/people/')[1].split('/')[0]
                basic_data["user"] = username_match
            
            # Try to extract any visible text that might indicate assets
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Look for any portfolio-related content
            text_content = soup.get_text()
            if 'portfolio' in text_content.lower():
                basic_data["message"] = "Portfolio page detected but content extraction was limited"
            
            return basic_data
            
        except Exception as e:
            logger.error(f"Error extracting basic data: {e}")
            return basic_data
