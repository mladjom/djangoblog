from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import time
from selenium.webdriver.chrome.options import Options
import json

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

        # Extract detail lines
        detail_lines = driver.find_elements(By.CLASS_NAME, "auction-state-info__line")
        for line in detail_lines:
            text = line.text
            if "Датум објаве" in text:
                details["publication_date"] = text.split("еАукције")[1].strip()
            elif "Почетак еАукције" in text:
                details["start_time"] = text.split("еАукције")[1].strip()
            elif "Крај еАукције" in text:
                details["end_time"] = text.split("еАукције")[1].strip()
            elif "Почетна цена" in text:
                details["starting_price"] = text.split("Почетна цена")[1].strip()
            elif "Процењена вредност" in text:
                details["estimated_value"] = text.split("Процењена вредност")[1].strip()
            elif "Лицитациони корак" in text:
                details["bidding_step"] = text.split("Лицитациони корак")[1].strip()

        # Extract tab content
        additional_info = {}
        tabs = wait_for_element_load(By.CLASS_NAME, "ant-tabs-nav").find_elements(By.CLASS_NAME, "ant-tabs-tab")
        
        for tab in tabs:
            tab_name = tab.text
            try:
                driver.execute_script("arguments[0].click();", tab)
                time.sleep(0.5)
                tab_content = wait_for_element_load(By.CLASS_NAME, "ant-tabs-tabpane-active").text
                additional_info[tab_name] = tab_content
            except Exception as e:
                print(f"Error loading tab '{tab_name}': {e}")

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
    max_pages = 5
    auction_details = scrape_pages(base_url, max_pages=max_pages)

    # Save data to JSON
    with open("auction_details.json", "w", encoding="utf-8") as file:
        json.dump(auction_details, file, ensure_ascii=False, indent=4)

    print(f"\nSuccessfully scraped {len(auction_details)} unique auctions.")
    print("Data saved to 'auction_details.json'")

finally:
    driver.quit()