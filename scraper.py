from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from selenium.webdriver.chrome.options import Options
import json
from datetime import datetime

# Set up WebDriver
service = Service("/usr/bin/chromedriver")
options = Options()
# options.add_argument("--headless")
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
    
    Args:
        date_str (str): Serbian date string to parse
    
    Returns:
        datetime: Parsed datetime object
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

# Example usage with your data:
dates = {
    "publication_date": "16. дец. 2024.",
    "start_time": "08. јан. 2025. 09:00",
    "end_time": "08. јан. 2025. 13:00"
}

parsed_dates = {
    key: parse_serbian_date(value) for key, value in dates.items()
}


def extract_details(auction_code):
    details = {}
    current_url = driver.current_url
    try:
        # Construct and navigate to the detail URL
        detail_url = f"https://eaukcija.sud.rs/#/aukcije/{auction_code}"
        driver.get(detail_url)
        
        # Wait for content to load
        wait_for_element_load(By.CLASS_NAME, "auction-info")
        time.sleep(1)  # Additional wait for dynamic content
        
        # Extract basic details
        details["code"] = wait_for_element_load(By.CLASS_NAME, "auction-list-item__code").text
        details["status"] = wait_for_element_load(By.CLASS_NAME, "auction-list-item__status").text
        details["title"] = wait_for_element_load(By.CLASS_NAME, "auction-item-title").text
        details["url"] = detail_url

        # Extract detail lines (for publication date, start time, end time, prices)
        detail_lines = driver.find_elements(By.CLASS_NAME, "auction-state-info__line")
        for line in detail_lines:
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
        

        # Extract tab content for additional information (category, executor, description, sale number, tags)
        additional_info = {}
        tabs = wait_for_element_load(By.CLASS_NAME, "ant-tabs-nav").find_elements(By.CLASS_NAME, "ant-tabs-tab")
        
        for tab in tabs:
            tab_name = tab.text.strip()
            try:
                # Click the tab
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(0.5)
                
                # Wait for and retrieve the content of the active tab
                tab_content_element = wait_for_element_load(By.CLASS_NAME, "ant-tabs-tabpane-active")
                tab_content = tab_content_element.get_attribute("innerHTML").strip()
                
                # Parse tab content based on the tab name
                if tab_name == "Детаљи":
                    # Extract description and sale number
                    detail_lines = tab_content_element.find_elements(By.CLASS_NAME, "info-label-row")
                    for line in detail_lines:
                        text = line.text.strip()
                        if "Опис:" in text:
                            additional_info["description"] = text.replace("Опис:", "").strip()
                        elif "Продаја:" in text:
                            additional_info["sale_number"] = text.replace("Продаја:", "").strip()
                
                elif tab_name == "Локација":
                    # Extract location details
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
                    # Extract category name
                    category_element = tab_content_element.find_element(By.CLASS_NAME, "category-name")
                    additional_info["categories"] = category_element.text.strip()
                
                elif tab_name == "Тагови":
                    # Extract tags
                    additional_info["tags"] = tab_content
                
                elif tab_name == "Јавни извршитељ":
                    # Extract executor
                    additional_info["executor"] = tab_content
                
                elif tab_name == "Документи":
                    # Extract document names
                    document_elements = tab_content_element.find_elements(By.CLASS_NAME, "category-name")
                    additional_info["documents"] = [doc.text.strip() for doc in document_elements if doc.text.strip()]
            
            except Exception as e:
                print(f"Error processing tab '{tab_name}': {e}")


        # Add additional info to details
        details["additional_info"] = additional_info
        
        # Return to the listing page
        driver.get(current_url)
        wait_for_element_load(By.CLASS_NAME, "auction-list-item")
        time.sleep(1)
        
        return details
        
    except Exception as e:
        print(f"Error extracting details for auction {auction_code}: {e}")
        # Return to the listing page on error
        driver.get(current_url)
        wait_for_element_load(By.CLASS_NAME, "auction-list-item")
        time.sleep(1)
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

# Start scraping
try:
    base_url = "https://eaukcija.sud.rs"
    max_pages = 1
    auction_details = scrape_pages(base_url, max_pages=max_pages)

    # Save data to JSON
    with open("auction_details.json", "w", encoding="utf-8") as file:
        json.dump(auction_details, file, ensure_ascii=False, indent=4)

    print(f"\nSuccessfully scraped {len(auction_details)} unique auctions.")
    print("Data saved to 'auction_details.json'")

finally:
    driver.quit()
