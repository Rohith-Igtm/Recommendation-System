from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# ✅ Initialize WebDriver
driver = webdriver.Chrome()
query = "mobiles"

# ✅ Open Flipkart search page
driver.get(f"https://www.flipkart.com/search?q={query}")
time.sleep(5)  # Wait for page to load

# ✅ Find all product links (from <a> tag with class CGtC98)
product_links = driver.find_elements(By.CLASS_NAME, "CGtC98")

# ✅ Extract URLs from 'href' attribute
urls = [link.get_attribute("href") for link in product_links]

print(len(urls), "items found")  # Print number of items found

# ✅ Print all extracted URLs
for url in urls:
    print(url)

# ✅ Open the first product page for reviews
if urls:
    driver.get(urls[0])  # Open first product link
    time.sleep(5)  # Wait for page to load
    print("✅ Opened the first product page!")

# ✅ Close driver after execution
driver.quit()


        