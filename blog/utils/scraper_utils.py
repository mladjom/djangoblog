import requests
from bs4 import BeautifulSoup
from typing import Optional, List, Dict
import time
import logging
from urllib.parse import urljoin
import random
from requests.exceptions import RequestException

class WebScraper:
    def __init__(self, base_url: str, headers: Optional[Dict] = None):
        """
        Initialize the scraper with base URL and optional headers.
        
        Args:
            base_url: The base URL for the website to scrape
            headers: Optional custom headers for requests
        """
        self.base_url = base_url
        self.headers = headers or {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def get_soup(self, url: str, delay: float = 1.0) -> Optional[BeautifulSoup]:
        """
        Fetch a page and return its BeautifulSoup object with error handling and rate limiting.
        
        Args:
            url: The URL to scrape
            delay: Time to wait between requests in seconds
        
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            # Add random delay for politeness
            time.sleep(delay + random.uniform(0.1, 0.5))
            
            # Make the request
            response = self.session.get(url)
            response.raise_for_status()
            
            # Parse with BS4
            soup = BeautifulSoup(response.text, 'html.parser')
            self.logger.info(f"Successfully fetched {url}")
            return soup
            
        except RequestException as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def extract_data(self, soup: BeautifulSoup, selectors: Dict[str, str]) -> Dict[str, str]:
        """
        Extract data from a soup object using provided CSS selectors.
        
        Args:
            soup: BeautifulSoup object
            selectors: Dictionary mapping data keys to CSS selectors
        
        Returns:
            Dictionary of extracted data
        """
        data = {}
        for key, selector in selectors.items():
            try:
                element = soup.select_one(selector)
                data[key] = element.text.strip() if element else None
            except Exception as e:
                self.logger.error(f"Error extracting {key}: {str(e)}")
                data[key] = None
        return data
    
    def scrape_pagination(self, start_url: str, next_page_selector: str, max_pages: int = 5) -> List[str]:
        """
        Scrape paginated content with limits and error handling.
        
        Args:
            start_url: URL of the first page
            next_page_selector: CSS selector for next page link
            max_pages: Maximum number of pages to scrape
        
        Returns:
            List of page URLs
        """
        pages = []
        current_url = start_url
        
        for page in range(max_pages):
            soup = self.get_soup(current_url)
            if not soup:
                break
                
            pages.append(current_url)
            
            # Find next page link
            next_link = soup.select_one(next_page_selector)
            if not next_link or not next_link.get('href'):
                break
                
            current_url = urljoin(self.base_url, next_link['href'])
            
        return pages

    def save_to_file(self, data: List[Dict], filename: str):
        """
        Save scraped data to a file with error handling.
        
        Args:
            data: List of dictionaries containing scraped data
            filename: Name of file to save to
        """
        try:
            import json
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Successfully saved data to {filename}")
        except Exception as e:
            self.logger.error(f"Error saving to file: {str(e)}")