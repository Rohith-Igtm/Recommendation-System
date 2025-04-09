from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Setup driver
options = webdriver.ChromeOptions()
options.add_argument("--disable-blink-features=AutomationControlled")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

query = "laptops"
driver.get(f"https://www.amazon.in/s?k={query}")
time.sleep(5)

product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
urls = [link.get_attribute("href") for link in product_links if link.get_attribute("href")]

print(f"{len(urls)} items found")

all_products = []

for url in urls:
    try:
        driver.get(url)
        time.sleep(3)

        # Product Name
        try:
            name = driver.find_element(By.CSS_SELECTOR, ".a-size-large.product-title-word-break").text.strip()
        except:
            name = "N/A"

        # Product Price
        try:
            price_whole = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]/span[2]').text.strip()
            price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text.strip()
            price_val = f"₹{price_whole}.{price_fraction}"
        except:
            price_val = "N/A"

        # Product Description
        try:
            ul = driver.find_element(By.CSS_SELECTOR, "ul.a-unordered-list.a-vertical.a-spacing-mini")
            li_elements = ul.find_elements(By.TAG_NAME, "li")
            base_desc_list = [li.text.strip() for li in li_elements if li.text.strip()]
        except:
            base_desc_list = []

        # Image URL
        try:
            img_element = driver.find_element(By.ID, "landingImage")
            img_src = img_element.get_attribute("src") or img_element.get_attribute("data-old-hires")
        except:
            img_src = "N/A"

        # Overall Rating
        try:
            rating_span = driver.find_element(By.CSS_SELECTOR, "span.a-icon-alt")
            overall_rating = rating_span.get_attribute("innerHTML").split(" ")[0]
        except:
            overall_rating = "N/A"

        # Star Ratings Breakdown
        star_dict = {}
        stars = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
        try:
            histogram_items = driver.find_elements(By.CSS_SELECTOR, "#histogramTable li")
            for i in range(5):
                if i < len(histogram_items):
                    lines = histogram_items[i].text.strip().split("\n")
                    percent = lines[1] if len(lines) > 1 else "N/A"
                    star_dict[stars[i]] = percent
                else:
                    star_dict[stars[i]] = "N/A"
        except:
            star_dict = {star: "N/A" for star in stars}

        # Store product
        product = {
            "name": name,
            "price": price_val,
            "image": img_src,
            "short_desc": base_desc_list,
            "overall_rating": overall_rating,
            "star_ratings": star_dict,
            "link": url
        }
        all_products.append(product)

        # Print summary
        print(f"✅ Scraped: {name} | Price: {price_val}")
        print("-----------------------------------------------------")

    except Exception as e:
        print(f"❌ Error at {url} — {e}")
        continue

driver.quit()

# Optional: Print all scraped data
print("\n\nAll scraped products:")
for p in all_products:
    print(p)
    print("-----------------------------------------------------")
