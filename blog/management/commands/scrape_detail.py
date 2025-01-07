from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import random
import json
import logging
from datetime import datetime
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)

class ScrapeDetail:
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
        try:
            date_part = date_text.split(' ', 2)[2]
            parts = date_part.split()
            month_abbr = parts[1].lower().rstrip('.')
            if month_abbr in self.SERBIAN_MONTHS:
                parts[1] = self.SERBIAN_MONTHS[month_abbr]
            return f"{parts[0]} {parts[1]} {parts[2]} {parts[3]}"
        except Exception as e:
            logger.error(f"Error converting Serbian date '{date_text}': {e}")
            return None

    def parse_datetime(self, date_text: str) -> datetime:
        try:
            converted_date = self.convert_serbian_date(date_text)
            return datetime.strptime(converted_date, '%d. %b %Y. %H:%M')
        except Exception as e:
            logger.error(f"Error parsing date '{date_text}': {e}")
            return None

    def parse_detail_page(self, detail_url: str) -> dict:
        try:
            self.driver.get(detail_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".content-with-side__main"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            main_content = soup.select_one('.content-with-side__main')

            # Extract details
            title = main_content.select_one('.auction-item-title').text.strip()
            status = main_content.select_one('.auction-list-item__status').text.strip()
            start_date = self.parse_datetime(
                main_content.select_one('.start_date').text.strip())
            end_date = self.parse_datetime(
                main_content.select_one('.end_date').text.strip())
            initial_price = self.parse_price(
                main_content.select_one('.auction-state-info__line .auction-list-item__price').text.strip())

            # Extract additional information
            additional_info = {}
            additional_sections = main_content.select('.info-label-row')
            for section in additional_sections:
                key_value = section.text.split(':', 1)
                if len(key_value) == 2:
                    additional_info[key_value[0].strip()] = key_value[1].strip()

            return {
                "title": title,
                "status": status,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "initial_price": initial_price,
                "additional_info": additional_info,
                "url": detail_url,
            }
        except Exception as e:
            logger.error(f"Error parsing detail page '{detail_url}': {e}")
            return {}

    def scrape_page(self, page: int) -> list:
        try:
            url = f"{self.base_url}?page={page}"
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".auction-list-item"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = soup.select('.auction-list-item')

            results = []
            for item in items:
                detail_url = item.select_one('a')['href']
                detail_data = self.parse_detail_page(detail_url)
                if detail_data:
                    results.append(detail_data)

            return results
        except Exception as e:
            logger.error(f"Error scraping page {page}: {e}")
            return []

    def get_total_pages(self) -> int:
        try:
            self.driver.get(self.base_url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".pagination-pager"))
            )
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            pagination_links = soup.select('.pagination-pager a')
            return max(int(link.text.strip()) for link in pagination_links if link.text.strip().isdigit())
        except Exception as e:
            logger.error(f"Error getting total pages: {e}")
            return 1

    def scrape_all_pages(self) -> list:
        try:
            total_pages = self.get_total_pages()
            logger.info(f"Total pages: {total_pages}")
            all_results = []
            for page in range(1, total_pages + 1):
                logger.info(f"Scraping page {page}/{total_pages}")
                page_results = self.scrape_page(page)
                all_results.extend(page_results)
            return all_results
        except Exception as e:
            logger.error(f"Error scraping all pages: {e}")
            return []

    def save_results(self, results, output_file: str):
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logger.error(f"Error saving results: {e}")

if __name__ == "__main__":
    BASE_URL = "https://eaukcija.sud.rs"
    OUTPUT_FILE = "auction_details.json"

    scraper = ScrapeDetail(base_url=BASE_URL)
    all_data = scraper.scrape_all_pages()
    scraper.save_results(all_data, OUTPUT_FILE)
    logger.info(f"Scraping completed. Data saved to {OUTPUT_FILE}")
    scraper.driver.quit()

class Command(BaseCommand):
    help = "Scrape auction site data, including detail pages, and save the results."

    def add_arguments(self, parser):
        parser.add_argument(
            '--base-url',
            type=str,
            default='https://eaukcija.sud.rs',
            help='Base URL of the auction website (default: https://eaukcija.sud.rs)',
        )
        parser.add_argument(
            '--output',
            type=str,
            default='auction_details.json',
            help='Output file for saving scraped data (default: auction_details.json)',
        )
        parser.add_argument(
            '--pages',
            type=int,
            help='Number of pages to scrape. If omitted, all pages will be scraped.',
        )

    def handle(self, *args, **options):
        base_url = options['base_url']
        output_file = options['output']
        pages_to_scrape = options.get('pages', None)

        self.stdout.write(self.style.NOTICE(f"Starting to scrape data from {base_url}..."))

        try:
            scraper = ScrapeDetail(base_url=base_url)
            if pages_to_scrape:
                self.stdout.write(self.style.NOTICE(f"Scraping {pages_to_scrape} page(s)..."))
                results = []
                for page in range(1, pages_to_scrape + 1):
                    self.stdout.write(self.style.NOTICE(f"Scraping page {page}/{pages_to_scrape}..."))
                    results.extend(scraper.scrape_page(page))
            else:
                self.stdout.write(self.style.NOTICE("Scraping all available pages..."))
                results = scraper.scrape_all_pages()

            # Save results to file
            scraper.save_results(results, output_file)
            self.stdout.write(self.style.SUCCESS(f"Scraping completed. Data saved to {output_file}."))

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.stderr.write(self.style.ERROR(f"An error occurred: {e}"))

        finally:
            scraper.driver.quit()