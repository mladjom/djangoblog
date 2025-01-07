from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import random
from datetime import datetime
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class SeleniumScraper:
    # Serbian month abbreviations mapping to English
    SERBIAN_MONTHS = {
        'јан': 'jan',
        'феб': 'feb',
        'мар': 'mar',
        'апр': 'apr',
        'мај': 'may',
        'јун': 'jun',
        'јул': 'jul',
        'авг': 'aug',
        'сеп': 'sep',
        'окт': 'oct',
        'нов': 'nov',
        'дец': 'dec'
    }

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.options = Options()
        self.options.headless = True
        self.driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=self.options)

    def parse_price(self, price_text: str) -> float:
        try:
            price = price_text.replace('РСД', '').replace('Почетна цена', '').strip()
            price = price.replace('.', '').replace(',', '.')
            return float(price)
        except ValueError as e:
            logger.error(f"Error parsing price {price_text}: {e}")
            return 0.0

    def convert_serbian_date(self, date_text: str) -> str:
        """Convert Serbian date format to a format that datetime can parse."""
        try:
            # Remove the leading text (Почетак еАукције or Крај еАукције)
            date_part = date_text.split(' ', 2)[2]
            
            # Split the date parts
            parts = date_part.split()
            
            # Convert Serbian month abbreviation to English
            month_abbr = parts[1].lower().rstrip('.')
            if month_abbr in self.SERBIAN_MONTHS:
                parts[1] = self.SERBIAN_MONTHS[month_abbr]
            
            # Reconstruct the date string
            return f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}"
            
        except Exception as e:
            logger.error(f"Error converting Serbian date '{date_text}': {e}")
            return None

    def parse_datetime(self, date_text: str) -> datetime:
        """Parse Serbian date format to datetime object."""
        try:
            # Convert Serbian date to parseable format
            converted_date = self.convert_serbian_date(date_text)
            if not converted_date:
                return None
                
            # Parse the converted date
            return datetime.strptime(converted_date, '%d. %b %Y. %H:%M')
        except ValueError as e:
            logger.error(f"Error parsing date '{date_text}' (converted to '{converted_date}'): {e}")
            return None

    def parse_auction_item(self, item) -> dict:
        try:
            code = item.select_one('.auction-list-item__code').text.strip()
            status = item.select_one('.auction-list-item__status').text.strip()
            title = item.select_one('.auction-list-item__title').text.strip()

            dates = item.select('.auction-list-item__countdown')
            start_date = self.parse_datetime(dates[0].text)
            end_date = self.parse_datetime(dates[1].text)

            price_text = item.select_one('.auction-list-item__price').text.strip()
            price = self.parse_price(price_text)

            detail_link = item.select_one('a')['href']
            auction_id = detail_link.split('/')[-1]

            return {
                'auction_id': auction_id,
                'code': code,
                'status': status,
                'title': title,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'price': price,
                'detail_url': detail_link,
            }
        except Exception as e:
            logger.error(f"Error parsing auction item: {e}")
            return None

    def scrape_page(self, page: int = 1) -> list:
        try:
            time.sleep(random.uniform(1, 3))

            url = f"{self.base_url}?page={page}"
            self.driver.get(url)
            time.sleep(2)  # Allow the page to load fully

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = soup.select('.auction-list-item')

            results = []
            for item in items:
                parsed_item = self.parse_auction_item(item)
                if parsed_item:
                    results.append(parsed_item)

            return results

        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")
            return []
    def scrape_detail_page(self, detail_url: str) -> dict:
        try:
            self.driver.get(detail_url)
            time.sleep(2)  # Allow the page to load fully
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Scrape details from the page
            auction_info = soup.select_one('.auction-info__state')
            additional_info = soup.select_one('.additional-info-wrapper')
            
            # Extract general information
            auction_id = detail_url.split('/')[-1]
            code = auction_info.select_one('.auction-list-item__code').text.strip()
            status = auction_info.select_one('.auction-list-item__status').text.strip()
            title = auction_info.select_one('.auction-item-title').text.strip()

            # Extract start and end dates
            dates = auction_info.select('.auction-list-item__countdown')
            start_date = self.parse_datetime(dates[1].text) if len(dates) > 1 else None
            end_date = self.parse_datetime(dates[2].text) if len(dates) > 2 else None
            
            price_text = auction_info.select_one('.auction-list-item__price').text.strip()
            price = self.parse_price(price_text)

            # Scrape additional info
            description = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(1) .info-label-row').text.strip()
            sale_type = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(1) .info-label-row:nth-of-type(2)').text.strip()
            municipality = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(2) .info-label-row:nth-of-type(1)').text.strip()
            location = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(2) .info-label-row:nth-of-type(2)').text.strip()
            category = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(3) .category-name').text.strip()
            tag = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(4) .category-name').text.strip()
            document_name = additional_info.select_one('.ant-tabs-tabpane:nth-of-type(5) .category-name').text.strip()

            return {
                'auction_id': auction_id,
                'code': code,
                'status': status,
                'title': title,
                'start_date': start_date.isoformat() if start_date else None,
                'end_date': end_date.isoformat() if end_date else None,
                'price': price,
                'description': description,
                'sale_type': sale_type,
                'municipality': municipality,
                'location': location,
                'category': category,
                'tag': tag,
                'document_name': document_name,
                'detail_url': detail_url,
            }
        except Exception as e:
            logger.error(f"Error scraping detail page '{detail_url}': {e}")
            return None

    def get_total_pages(self) -> int:
        try:
            self.driver.get(self.base_url)
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            pagination = soup.select_one('.pagination-pager').text.strip()
            total_pages = int(pagination.split('/')[-1])

            return total_pages
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 0