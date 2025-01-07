from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
from urllib.parse import urljoin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuctionScraper:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-dev-shm-usage')
        self.driver = webdriver.Chrome(service=Service("/usr/bin/chromedriver"), options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

    def parse_tab_content(self, soup):
        """Parse all tabs content from the additional info wrapper."""
        tabs_data = {}

        tab_titles = [tab.text.strip() for tab in soup.select('.ant-tabs-tab')]
        tab_panes = soup.select('.ant-tabs-tabpane')

        for title, pane in zip(tab_titles, tab_panes):
            if title == "Детаљи":
                details = {}
                for row in pane.select('.info-label-row'):
                    text = row.text.strip()
                    if ':' in text:
                        key, value = text.split(':', 1)
                        details[key.strip()] = value.strip()
                tabs_data['details'] = details
            if title == "Локација":
                location = {}
                for row in pane.select('.info-label-row'):
                    if ':' in row.text:
                        key, value = row.text.split(':', 1)
                        location[key.strip()] = value.strip()
                tabs_data['location'] = location
            elif title == "Категорија":
                category = pane.select_one('.category-name')
                if category:
                    tabs_data['category'] = category.text.strip()

            elif title == "Тагови":
                tags = []
                tag_elements = pane.select('.category-name')
                for tag in tag_elements:
                    tags.append(tag.text.strip())
                tabs_data['tags'] = tags

            elif title == "Јавни извршитељ":
                executor = pane.select_one('.category-name')
                if executor:
                    tabs_data['executor'] = executor.text.strip()

            elif title == "Документи":
                documents = [button.text.strip() for button in pane.select('.auction-form__download-button')]
                tabs_data['documents'] = documents

        return tabs_data

    def parse_detail_page(self, url):
        try:
            # Handle fragment URLs
            full_url = urljoin(self.base_url, url.split('#')[0])  # Remove fragments
            logger.info(f"Parsing detail page: {full_url}")
            
            # Navigate to the base URL and then simulate clicking to the detail page
            self.driver.get(full_url)
            if '#' in url:
                fragment = url.split('#')[-1]
                self.driver.execute_script(f"window.location.hash='{fragment}'")
            
            # Wait for content to load
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "content-with-side__main")))
            
            # Parse the page source with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            auction_info = {}

            # Extract code and status
            info_row = soup.select_one('.auction-list-item__info-row')
            if info_row:
                code_elem = info_row.select_one('.auction-list-item__code')
                status_elem = info_row.select_one('.auction-list-item__status')
                if code_elem:
                    auction_info['code'] = code_elem.text.strip()
                if status_elem:
                    auction_info['status'] = status_elem.text.strip()

            # Extract title
            title_elem = soup.select_one('.auction-item-title')
            if title_elem:
                auction_info['title'] = title_elem.text.strip()

            # Extract dates and prices
            for info_line in soup.select('.auction-state-info__line'):
                text = info_line.text.strip()
                if 'Почетна цена' in text:
                    auction_info['initial_price'] = text.replace('Почетна цена', '').replace('РСД', '').strip()
                elif 'Процењена вредност' in text:
                    auction_info['estimated_value'] = text.replace('Процењена вредност', '').replace('РСД', '').strip()
                elif 'Лицитациони корак' in text:
                    auction_info['bid_step'] = text.replace('Лицитациони корак', '').replace('РСД', '').strip()
                elif 'Датум објаве' in text:
                    auction_info['publication_date'] = text.replace('Датум објаве еАукције', '').strip()
                elif 'Почетак еАукције' in text:
                    auction_info['start_date'] = text.replace('Почетак еАукције', '').strip()
                elif 'Крај еАукције' in text:
                    auction_info['end_date'] = text.replace('Крај еАукције', '').strip()

            # Parse additional info tabs
            additional_info = self.parse_tab_content(soup.select_one('.additional-info-wrapper'))
            auction_info.update(additional_info)

            auction_info['url'] = full_url
            return auction_info

        except Exception as e:
            logger.error(f"Error parsing detail page {url}: {e}")
            return None

    def get_total_pages(self):
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "auction-list-item")))
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            pagination = soup.select('.pagination-pager a')
            pages = [int(page.text) for page in pagination if page.text.strip().isdigit()]
            return max(pages) if pages else 1
        except Exception as e:
            logger.error(f"Error determining total pages: {e}")
            return 1

    def scrape_page(self, page_num):
        try:
            url = f"{self.base_url}?page={page_num}"
            logger.info(f"Scraping page: {url}")

            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.CLASS_NAME, "auction-list-item")))

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            items = soup.select('.auction-list-item')

            results = []
            for item in items:
                link = item.select_one('a')
                if link and link.get('href'):
                    detail_data = self.parse_detail_page(link['href'])
                    if detail_data:
                        results.append(detail_data)

            return results
        except Exception as e:
            logger.error(f"Error scraping page {page_num}: {e}")
            return []

    def scrape_all(self):
        all_results = []
        total_pages = self.get_total_pages()
        logger.info(f"Total pages to scrape: {total_pages}")

        for page in range(1, total_pages + 1):
            logger.info(f"Scraping page {page}/{total_pages}")
            page_results = self.scrape_page(page)
            all_results.extend(page_results)

        return all_results

    def save_results(self, results, filename):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

    def close(self):
        self.driver.quit()


def main():
    base_url = "https://eaukcija.sud.rs"
    output_file = "auction_data.json"

    scraper = AuctionScraper(base_url)
    try:
        results = scraper.scrape_all()
        scraper.save_results(results, output_file)
        logger.info(f"Scraping completed. Data saved to {output_file}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
