import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# User credentials and configuration
USERNAME = "palgagan9389@gmail.com"
PASSWORD = "Gagan@9520"
CHROMEDRIVER_PATH = r"C:\Users\hp\Desktop\assignment\chromedriver-win64\chromedriver.exe"

# Amazon Best Seller URLs
CATEGORY_URLS = [
    "https://www.amazon.in/gp/bestsellers/kitchen/ref=zg_bs_nav_kitchen_0",
    "https://www.amazon.in/gp/bestsellers/shoes/ref=zg_bs_nav_shoes_0",
    "https://www.amazon.in/gp/bestsellers/computers/ref=zg_bs_nav_computers_0",
    "https://www.amazon.in/gp/bestsellers/electronics/ref=zg_bs_nav_electronics_0"
]

def setup_driver():
    """Setup ChromeDriver with options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")
    service = Service(CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    return driver

def amazon_login(driver):
    """Login to Amazon with user credentials."""
    driver.get("https://www.amazon.in/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.in%2F%3Fref_%3Dnav_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=inflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0")
    try:
        # Enter username
        email_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ap_email"))
        )
        email_field.send_keys(USERNAME)
        email_field.send_keys(Keys.RETURN)
        time.sleep(2)

        # Enter password
        password_field = WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.ID, "ap_password"))
        )
        password_field.send_keys(PASSWORD)
        password_field.send_keys(Keys.RETURN)

        # Verify login success
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, "nav-logo-sprites"))
        )
        print("Login successful!")
    except TimeoutException:
        print("Login failed! Please check your credentials or solve CAPTCHA manually.")
        driver.quit()
        exit()

def scrape_category(driver, category_url):
    """Scrape product details for a given category."""
    driver.get(category_url)
    products = []

    try:
        for i in range(1, 4):  # Loop to navigate multiple pages (adjust as needed)
            time.sleep(2 ,print(f"Scraping page {i} of category: {category_url}"))

            items = driver.find_elements(By.CSS_SELECTOR, "div.zg-grid-general-faceout")
            print(f"Found {len(items)} items on page {i}.")
            for item in items:
                try:
                    product_name = item.find_element(By.CSS_SELECTOR, "div.p13n-sc-truncated").text
                    price = item.find_element(By.CSS_SELECTOR, "span.p13n-sc-price").text
                    rating = item.find_element(By.CSS_SELECTOR, "span.a-icon-alt").text
                    discount = "50%"  # Placeholder for discount
                    num_bought = "10"  # Placeholder for number bought

                    # Append product details to the list
                    products.append({
                        "Product Name": product_name,
                        "Price": price,
                        "Discount": discount,
                        "Rating": rating,
                        "Number Bought": num_bought,
                        "Category": category_url.split("/")[-2]
                    })
                except NoSuchElementException as e:
                    print(f"Element not found: {e}")
                    continue

            # Navigate to next page if available
            next_page = driver.find_elements(By.CSS_SELECTOR, "li.a-last a")
            if next_page:
                next_page[0].click()
                time.sleep(3)
            else:
                break
    except Exception as e:
        print(f"Error occurred: {e}")
    return products

def main():
    driver = setup_driver()
    amazon_login(driver)

    all_products = []
    for url in CATEGORY_URLS:
        products = scrape_category(driver, url)
        all_products.extend(products)
        print(f"Finished scraping category: {url}")

    # Save data to CSV
    if all_products:
        df = pd.DataFrame(all_products)
        df.to_csv("amazon_best_sellers.csv", index=False)
        print("Data saved to amazon_best_sellers.csv")
    else:
        print("No products found to save.")

    driver.quit()

if __name__ == "__main__":
    main()