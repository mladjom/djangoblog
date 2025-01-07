from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.webdriver.chrome.options import Options
import json

# Set up WebDriver
service = Service("/usr/bin/chromedriver")  # Adjust the path if needed
# options = Options()
# options.add_argument("--headless")
# driver = webdriver.Chrome(service=service, options=options)
driver = webdriver.Chrome(service=service)

# Function to extract auction data from the current page
def extract_data():
    auctions = []
    # Find all auction items
    auction_items = driver.find_elements(By.CLASS_NAME, "auction-list-item")
    for item in auction_items:
        try:
            code = item.find_element(By.CLASS_NAME, "auction-list-item__code").text
            status = item.find_element(By.CLASS_NAME, "auction-list-item__status").text
            title = item.find_element(By.CLASS_NAME, "auction-list-item__title").text
            countdowns = item.find_elements(By.CLASS_NAME, "auction-list-item__countdown")
            start_time = countdowns[0].text if len(countdowns) > 0 else None
            end_time = countdowns[1].text if len(countdowns) > 1 else None
            price = item.find_element(By.CLASS_NAME, "auction-list-item__price").text
            link = item.find_element(By.TAG_NAME, "a").get_attribute("href")
            
            auctions.append({
                "code": code,
                "status": status,
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "price": price,
                "link": link,
            })
        except Exception as e:
            print(f"Error extracting item: {e}")
    return auctions

# Function to handle pagination with a limit on the number of pages
def scrape_pages(start_url, max_pages=5):
    driver.get(start_url)
    all_auctions = []
    page_count = 0

    while page_count < max_pages:
        # Wait for auction items to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "auction-list-item"))
        )
        # Extract data from the current page
        auctions = extract_data()
        all_auctions.extend(auctions)

        # Check if the "Next" button is disabled or not
        try:
            next_button = driver.find_element(By.CLASS_NAME, "pagination-next")
            if "disabled" in next_button.get_attribute("class"):
                print("Reached the last page.")
                break  # Exit loop if no more pages
            else:
                next_button.click()  # Click "Next" to go to the next page
                time.sleep(2)  # Wait for the next page to load
                page_count += 1
        except Exception as e:
            print(f"Pagination error: {e}")
            break  # Break loop if pagination button is not found or error occurs

    return all_auctions

# Start scraping
try:
    url = "https://eaukcija.sud.rs"  # Replace with the actual URL of the auctions
    max_pages = 5  # Number of pages to scrape
    auction_data = scrape_pages(url, max_pages=max_pages)

    # Save the data to a JSON file
    with open("auctions.json", "w", encoding="utf-8") as file:
        json.dump(auction_data, file, ensure_ascii=False, indent=4)

    print(f"Scraped {len(auction_data)} auction items across {max_pages} page(s). Data saved to 'auctions.json'.")
finally:
    driver.quit()