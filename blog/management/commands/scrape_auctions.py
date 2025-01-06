# auctions/management/commands/scrape_auctions.py
from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
import logging
from datetime import datetime
from typing import List, Dict
import time
import random
from django.utils.html import strip_tags
import json

# Assuming you'll create this model in your models.py
#from blog.models.auction_model import Auction

logger = logging.getLogger(__name__)

class AuctionScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def parse_price(self, price_text: str) -> float:
        """Extract numerical price value from price text."""
        try:
            # Remove 'РСД' and 'Почетна цена', then convert to float
            price = price_text.replace('РСД', '').replace('Почетна цена', '').strip()
            price = price.replace('.', '').replace(',', '.')  # Handle Serbian number format
            return float(price)
        except ValueError as e:
            logger.error(f"Error parsing price {price_text}: {e}")
            return 0.0

    def parse_datetime(self, date_text: str) -> datetime:
        """Parse Serbian date format to datetime object."""
        try:
            # Remove leading text and convert Serbian month abbreviations if needed
            date_part = date_text.split(' ', 1)[1]  # Remove "Почетак еАукције" or "Крај еАукције"
            return datetime.strptime(date_part, '%d. %b. %Y. %H:%M')
        except ValueError as e:
            logger.error(f"Error parsing date {date_text}: {e}")
            return None

    def parse_auction_item(self, item) -> Dict:
        """Parse single auction item HTML into dictionary."""
        try:
            # Find all required elements
            code = item.select_one('.auction-list-item__code').text.strip()
            status = item.select_one('.auction-list-item__status').text.strip()
            title = item.select_one('.auction-list-item__title').text.strip()
            
            # Handle dates
            dates = item.select('.auction-list-item__countdown')
            start_date = self.parse_datetime(dates[0].text)
            end_date = self.parse_datetime(dates[1].text)
            
            # Handle price
            price_text = item.select_one('.auction-list-item__price').text.strip()
            price = self.parse_price(price_text)
            
            # Get detail URL
            detail_link = item.select_one('a')['href']
            auction_id = detail_link.split('/')[-1]

            return {
                'auction_id': auction_id,
                'code': code,
                'status': status,
                'title': strip_tags(title),
                'start_date': start_date,
                'end_date': end_date,
                'price': price,
                'detail_url': detail_link,
            }
        except Exception as e:
            logger.error(f"Error parsing auction item: {e}")
            return None

    def scrape_page(self, page: int = 1) -> List[Dict]:
        """Scrape a single page of auction listings."""
        try:
            # Add random delay between requests
            time.sleep(random.uniform(1, 3))
            
            url = f"{self.base_url}?page={page}"
            response = self.session.get(url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
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

    def get_total_pages(self) -> int:
        """Get total number of pages from pagination."""
        try:
            response = self.session.get(self.base_url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            pagination = soup.select_one('.pagination-pager').text
            total_pages = int(pagination.split('/')[-1])
            
            return total_pages
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 0

class Command(BaseCommand):
    help = 'Scrapes auction website and updates database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--pages',
            type=int,
            help='Number of pages to scrape (default: all)',
        )
        parser.add_argument(
            '--base-url',
            type=str,
            default='https://your-auction-site.com',
            help='Base URL of the auction website',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='auctions.json',
            help='Output file for scraped data (default: auctions.json)',
        )        

    def save_to_json(self, data, output_file):
        """Save the scraped auction data to a JSON file."""
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                # Write the data as a JSON array
                json.dump(data, f, ensure_ascii=False, indent=4)
                f.write('\n')  # Ensure that each page data is on a new line
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")

    def handle(self, *args, **options):
        scraper = AuctionScraper(options['base_url'])
        
        # Determine number of pages to scrape
        total_pages = scraper.get_total_pages()
        pages_to_scrape = options['pages'] or total_pages
        output_file = options['output']
        
        self.stdout.write(f"Starting to scrape {pages_to_scrape} pages...")
        
        all_auctions = []  # This will hold all auction data to be saved in JSON
        
        for page in range(1, pages_to_scrape + 1):
            self.stdout.write(f"Scraping page {page}/{pages_to_scrape}")
            
            auctions = scraper.scrape_page(page)
            all_auctions.extend(auctions)  # Add the auctions from this page
            
            self.stdout.write(self.style.SUCCESS(f"Successfully processed page {page}"))
        
        # Save all scraped data to a JSON file
        self.save_to_json(all_auctions, output_file)
        
        self.stdout.write(self.style.SUCCESS(f'Scraping completed successfully. Data saved to {output_file}'))
    # def handle(self, *args, **options):
    #     scraper = AuctionScraper(options['base_url'])
        
    #     # Determine number of pages to scrape
    #     total_pages = scraper.get_total_pages()
    #     pages_to_scrape = options['pages'] or total_pages
        
    #     self.stdout.write(f"Starting to scrape {pages_to_scrape} pages...")
        
    #     for page in range(1, pages_to_scrape + 1):
    #         self.stdout.write(f"Scraping page {page}/{pages_to_scrape}")
            
    #         auctions = scraper.scrape_page(page)
    #         for auction_data in auctions:
    #             try:
    #                 # Update or create auction in database
    #                 Auction.objects.update_or_create(
    #                     auction_id=auction_data['auction_id'],
    #                     defaults={
    #                         'code': auction_data['code'],
    #                         'status': auction_data['status'],
    #                         'title': auction_data['title'],
    #                         'start_date': auction_data['start_date'],
    #                         'end_date': auction_data['end_date'],
    #                         'price': auction_data['price'],
    #                         'detail_url': auction_data['detail_url'],
    #                     }
    #                 )
    #             except Exception as e:
    #                 logger.error(f"Error saving auction {auction_data['auction_id']}: {e}")
    #                 continue
            
    #         self.stdout.write(self.style.SUCCESS(f"Successfully processed page {page}"))
        
    #     self.stdout.write(self.style.SUCCESS('Scraping completed successfully'))