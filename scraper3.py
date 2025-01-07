from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.options import Options
from datetime import datetime
import time
import json
from json import JSONEncoder

class DateTimeEncoder(JSONEncoder):
    """Custom JSON Encoder that handles datetime objects by converting them to ISO format strings"""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Set up WebDriver
service = Service("/usr/bin/chromedriver")
options = Options()
#options.add_argument("--headless")
driver = webdriver.Chrome(service=service, options=options)
driver.maximize_window()

def wait_for_element_load(by, selector, timeout=10):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((by, selector))
    )

def wait_for_url_change(old_url):
    def url_changed(driver):
        return driver.current_url != old_url
    WebDriverWait(driver, 10).until(url_changed)

def parse_price(price_str):
    # Remove currency and extra spaces
    price_str = price_str.replace("РСД", "").strip()
    # Replace thousands separator (dot) and decimal separator (comma) with period
    price_str = price_str.replace(".", "").replace(",", ".")
    # Convert to float
    try:
        return float(price_str)
    except ValueError:
        print(f"Error converting price: {price_str}")
        return None

def parse_serbian_date(date_str):
    """
    Parse Serbian date strings into datetime objects.
    Handles formats like:
    - "16. дец. 2024."
    - "08. јан. 2025. 09:00"
    """
    # Serbian month abbreviations mapping
    serbian_months = {
        'јан': '01', 'феб': '02', 'мар': '03', 'апр': '04',
        'мај': '05', 'јун': '06', 'јул': '07', 'авг': '08',
        'сеп': '09', 'окт': '10', 'нов': '11', 'дец': '12'
    }
    
    # Clean up the input string
    date_str = date_str.strip().lower()
    
    # Remove trailing dot if present
    if date_str.endswith('.'):
        date_str = date_str[:-1]
        
    # Split into components
    parts = [p.strip() for p in date_str.split('.') if p.strip()]
    
    # Extract day, month, year, and time if present
    day = parts[0].zfill(2)
    month = serbian_months[parts[1].strip()]
    year = parts[2]
    
    # Check if time is included
    time_str = "00:00"
    if len(parts) > 3:
        time_str = parts[3]
    
    # Construct datetime string in standard format
    datetime_str = f"{year}-{month}-{day} {time_str}"
    
    # Parse and return datetime object
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M")

def clean_html_content(html_content):
    """Remove HTML tags and clean up the content"""
    # Remove common HTML elements we don't want
    unwanted_elements = [
        '<div tabindex="0" role="presentation" style="width: 0px; height: 0px; overflow: hidden; position: absolute;"></div>',
        '<div class="category-name">',
        '</div>'
    ]
    
    for element in unwanted_elements:
        html_content = html_content.replace(element, '')
    
    return html_content.strip()

def split_pdf_documents(doc_text):
    """Split concatenated PDF filenames"""
    # Split on .pdf to get individual documents, then add .pdf back
    docs = [d.strip() + '.pdf' for d in doc_text.split('.pdf') if d.strip()]
    return docs

def extract_details(auction_code):
    details = {}
    current_url = driver.current_url
    try:
        # Log the start of processing
        print(f"\nStarting to process auction {auction_code}")
        
        # Construct and navigate to the detail URL
        detail_url = f"https://eaukcija.sud.rs/#/aukcije/{auction_code}"
        print(f"Navigating to URL: {detail_url}")
        driver.get(detail_url)
        
        try:
            # Wait for content to load with longer timeout
            print("Waiting for auction-info element...")
            wait_for_element_load(By.CLASS_NAME, "auction-info", timeout=20)
            time.sleep(2)  # Increased wait time
            
            # Extract basic details with individual try-except blocks
            try:
                print("Extracting basic details...")
                details["code"] = wait_for_element_load(By.CLASS_NAME, "auction-list-item__code", timeout=10).text
                print(f"Found code: {details['code']}")
            except Exception as e:
                print(f"Error extracting code: {e}")
                details["code"] = auction_code

            try:
                details["status"] = wait_for_element_load(By.CLASS_NAME, "auction-list-item__status", timeout=10).text
                print(f"Found status: {details['status']}")
            except Exception as e:
                print(f"Error extracting status: {e}")
                details["status"] = "Unknown"

            try:
                details["title"] = wait_for_element_load(By.CLASS_NAME, "auction-item-title", timeout=10).text
                print(f"Found title: {details['title']}")
            except Exception as e:
                print(f"Error extracting title: {e}")
                details["title"] = "Unknown"

            details["url"] = detail_url

            # Extract detail lines with error handling
            print("Extracting detail lines...")
            try:
                detail_lines = driver.find_elements(By.CLASS_NAME, "auction-state-info__line")
                for line in detail_lines:
                    try:
                        text = line.text
                        if "Датум објаве" in text:
                            date_str = text.split("еАукције")[1].strip()
                            details["publication_date"] = parse_serbian_date(date_str)
                        elif "Почетак еАукције" in text:
                            date_str = text.split("еАукције")[1].strip()
                            details["start_time"] = parse_serbian_date(date_str)
                        elif "Крај еАукције" in text:
                            date_str = text.split("еАукције")[1].strip()
                            details["end_time"] = parse_serbian_date(date_str)
                        elif "Почетна цена" in text:
                            details["pricing"] = details.get("pricing", {})
                            details["pricing"]["starting_price"] = parse_price(text.split("Почетна цена")[1].strip())
                        elif "Процењена вредност" in text:
                            details["pricing"]["estimated_value"] = parse_price(text.split("Процењена вредност")[1].strip())
                        elif "Лицитациони корак" in text:
                            details["pricing"]["bidding_step"] = parse_price(text.split("Лицитациони корак")[1].strip())
                    except Exception as e:
                        print(f"Error processing detail line: {e}")
                        continue
            except Exception as e:
                print(f"Error finding detail lines: {e}")

            # Extract tab content
            print("Processing tabs...")
            additional_info = {}
            try:
                tabs = wait_for_element_load(By.CLASS_NAME, "ant-tabs-nav", timeout=10).find_elements(By.CLASS_NAME, "ant-tabs-tab")
                
                for tab in tabs:
                    try:
                        tab_name = tab.text.strip()
                        print(f"\nProcessing tab: {tab_name}")
                        
                        # Click the tab with retry
                        max_retries = 3
                        for attempt in range(max_retries):
                            try:
                                driver.execute_script("arguments[0].click();", tab)
                                time.sleep(1)  # Increased wait time
                                break
                            except Exception as e:
                                if attempt == max_retries - 1:
                                    print(f"Failed to click tab after {max_retries} attempts: {e}")
                                    raise
                                time.sleep(1)
                        
                        # Wait for and retrieve the content
                        tab_content_element = wait_for_element_load(By.CLASS_NAME, "ant-tabs-tabpane-active", timeout=10)
                        
                        if tab_name == "Детаљи":
                            detail_lines = tab_content_element.find_elements(By.CLASS_NAME, "info-label-row")
                            for line in detail_lines:
                                text = line.text.strip()
                                if "Опис:" in text:
                                    additional_info["description"] = text.replace("Опис:", "").strip()
                                elif "Продаја:" in text:
                                    additional_info["sale_number"] = text.replace("Продаја:", "").strip()
                        
                        elif tab_name == "Локација":
                            location = {}
                            location_lines = tab_content_element.find_elements(By.CLASS_NAME, "info-label-row")
                            for line in location_lines:
                                text = line.text.strip()
                                if "Општина:" in text:
                                    location["municipality"] = text.replace("Општина:", "").strip()
                                elif "Место:" in text:
                                    location["city"] = text.replace("Место:", "").strip()
                                elif "Катастарска општина:" in text:
                                    location["cadastral_municipality"] = text.replace("Катастарска општина:", "").strip()
                            additional_info["location"] = location
                        
                        elif tab_name == "Категорија":
                            try:
                                category_element = tab_content_element.find_element(By.CLASS_NAME, "category-name")
                                additional_info["categories"] = category_element.text.strip()
                            except Exception as e:
                                print(f"Error extracting category: {e}")
                                additional_info["categories"] = ""
                        
                        elif tab_name == "Тагови":
                            try:
                                tags_elements = tab_content_element.find_elements(By.CLASS_NAME, "category-name")
                                tags = [tag.text.strip() for tag in tags_elements if tag.text.strip()]
                                additional_info["tags"] = tags if tags else []
                            except Exception as e:
                                print(f"Error extracting tags: {e}")
                                additional_info["tags"] = []
                        
                        elif tab_name == "Јавни извршитељ":
                            try:
                                executor_element = tab_content_element.find_element(By.CLASS_NAME, "category-name")
                                additional_info["executor"] = executor_element.text.strip()
                            except Exception as e:
                                print(f"Error extracting executor: {e}")
                                additional_info["executor"] = ""
                        
                        elif tab_name == "Документи":
                            try:
                                document_elements = tab_content_element.find_elements(By.CLASS_NAME, "category-name")
                                doc_text = "".join([doc.text.strip() for doc in document_elements if doc.text.strip()])
                                additional_info["documents"] = split_pdf_documents(doc_text)
                            except Exception as e:
                                print(f"Error extracting documents: {e}")
                                additional_info["documents"] = []
                                
                    except Exception as e:
                        print(f"Error processing tab '{tab_name}': {e}")
                        continue
                
            except Exception as e:
                print(f"Error processing tabs: {e}")

            # Add additional info to details
            details["additional_info"] = additional_info
            
        except Exception as e:
            print(f"Error during main content extraction: {e}")
        
        finally:
            # Always try to return to the listing page
            print("Returning to listing page...")
            try:
                driver.get(current_url)
                wait_for_element_load(By.CLASS_NAME, "auction-list-item", timeout=10)
                time.sleep(1)
            except Exception as e:
                print(f"Error returning to listing page: {e}")
        
        return details
        
    except Exception as e:
        print(f"Critical error processing auction {auction_code}: {str(e)}")
        # Try to return to the listing page
        try:
            driver.get(current_url)
            wait_for_element_load(By.CLASS_NAME, "auction-list-item", timeout=10)
            time.sleep(1)
        except Exception as nav_error:
            print(f"Error navigating back after critical error: {nav_error}")
        return None


def extract_auctions_from_page():
    auctions = []
    try:
        # Wait for auction items to load
        wait_for_element_load(By.CLASS_NAME, "auction-list-item")
        time.sleep(1)
        
        # Find all auction items
        items = driver.find_elements(By.CLASS_NAME, "auction-list-item")
        
        for item in items:
            try:
                code = item.find_element(By.CLASS_NAME, "auction-list-item__code").text
                numeric_code = ''.join(filter(str.isdigit, code))
                auctions.append({"code": code, "numeric_code": numeric_code})
            except Exception as e:
                print(f"Error extracting item data: {e}")
                
        return auctions
    except Exception as e:
        print(f"Error finding auction items: {e}")
        return []

def check_page_has_content():
    try:
        wait_for_element_load(By.CLASS_NAME, "auction-list-item")
        return True
    except TimeoutException:
        return False

def navigate_to_page(base_url, page_num):
    page_url = f"{base_url}#/?stranica={page_num}"
    current_url = driver.current_url
    driver.get(page_url)
    if current_url != page_url:
        wait_for_element_load(By.CLASS_NAME, "auction-list-item")
        time.sleep(2)  # Wait for all items to load
    return page_url

def scrape_pages(base_url, max_pages=3):
    all_details = []
    processed_codes = set()

    for page_num in range(1, max_pages + 1):
        print(f"\nProcessing page {page_num}")
        
        # Navigate to page
        current_page_url = navigate_to_page(base_url, page_num)
        
        # Check if page has content
        if not check_page_has_content():
            print(f"No content found on page {page_num}")
            break
        
        # Get all auctions from current page
        page_auctions = extract_auctions_from_page()
        print(f"Found {len(page_auctions)} auctions on page {page_num}")
        
        if not page_auctions:
            print("No auctions found, ending pagination")
            break
        
        # Process each auction
        for auction in page_auctions:
            if auction["code"] not in processed_codes:
                print(f"Processing auction {auction['code']}")
                details = extract_details(auction["numeric_code"])
                if details:
                    all_details.append(details)
                    processed_codes.add(auction["code"])
                    print(f"Successfully extracted details for auction {auction['code']}")

    return all_details

def save_auction_details(auction_details, filename="auction_details.json"):
    """Save auction details to a JSON file with proper datetime handling"""
    with open(filename, "w", encoding="utf-8") as file:
        json.dump(auction_details, file, 
                 cls=DateTimeEncoder,
                 ensure_ascii=False, 
                 indent=4)

def load_auction_details(filename="auction_details.json"):
    """Load auction details from JSON file and convert date strings back to datetime objects"""
    with open(filename, "r", encoding="utf-8") as file:
        data = json.load(file)
        # Convert ISO datetime strings back to datetime objects
        for auction in data:
            if "publication_date" in auction:
                auction["publication_date"] = datetime.fromisoformat(auction["publication_date"])
            if "start_time" in auction:
                auction["start_time"] = datetime.fromisoformat(auction["start_time"])
            if "end_time" in auction:
                auction["end_time"] = datetime.fromisoformat(auction["end_time"])
        return data

# Main execution
if __name__ == "__main__":
    try:
        base_url = "https://eaukcija.sud.rs"
        max_pages = 2  # Adjust this value to scrape more pages
        auction_details = scrape_pages(base_url, max_pages=max_pages)

        # Save data using the new function
        save_auction_details(auction_details)

        print(f"\nSuccessfully scraped {len(auction_details)} unique auctions.")
        print("Data saved to 'auction_details.json'")

    finally:
        driver.quit()