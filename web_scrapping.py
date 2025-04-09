# Import necessary libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

# Function to scrape Amazon product data
def scrape_amazon_products(query):
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(f"https://www.amazon.in/s?k={query}")
    time.sleep(5)

    product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
    urls = [link.get_attribute("href") for link in product_links if link.get_attribute("href")]

    print(f"{len(urls)} items found on Amazon")

    for url in urls:
        try:
            driver.get(url)
            time.sleep(3)

            try:
                name = driver.find_element(By.CSS_SELECTOR, ".a-size-large.product-title-word-break").text.strip()
            except:
                name = "N/A"

            try:
                price_whole = driver.find_element(By.XPATH, '//*[@id="corePriceDisplay_desktop_feature_div"]/div[1]/span[3]/span[2]/span[2]').text.strip()
                price_fraction = driver.find_element(By.CLASS_NAME, "a-price-fraction").text.strip()
                price_val = f"₹{price_whole}.{price_fraction}"
            except:
                price_val = "N/A"

            try:
                ul = driver.find_element(By.CSS_SELECTOR, "ul.a-unordered-list.a-vertical.a-spacing-mini")
                li_elements = ul.find_elements(By.TAG_NAME, "li")
                base_desc_list = [li.text.strip() for li in li_elements if li.text.strip()]
            except Exception as e:
                base_desc_list = "N/A"

            try:
                img_element = driver.find_element(By.ID, "landingImage")
                img_src = img_element.get_attribute("src") or img_element.get_attribute("data-old-hires")
            except:
                img_src = "N/A"

            try:
                rating_span = driver.find_element(By.CSS_SELECTOR, "span.a-icon-alt")
                overall_rating = rating_span.get_attribute("innerHTML").split(" ")[0]
            except:
                overall_rating = "N/A"

            star_dict = {}
            try:
                histogram_items = driver.find_elements(By.CSS_SELECTOR, "#histogramTable li")
                stars = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]

                for i in range(5):
                    if i < len(histogram_items):
                        lines = histogram_items[i].text.strip().split("\n")
                        percent = lines[1] if len(lines) > 1 else "N/A"
                        star_dict[stars[i]] = percent
                    else:
                        star_dict[stars[i]] = "N/A"
            except Exception as e:
                star_dict = {star: "N/A" for star in stars}

            print(f"Name: {name}")
            print(f"Price: {price_val}")
            print(f"Image URL: {img_src}")
            print(f"Short Descriptions (List): {base_desc_list}")
            print(f"Overall Rating: {overall_rating}")
            print(f"Star Ratings Breakdown: {star_dict}")
            print(f"Product Link :{url}")
            print("-----------------------------------------------------")

        except Exception as e:
            print(f"Error at {url} — {e}")
            continue

    driver.quit()


# Function to scrape Flipkart product data
def scrape_flipkart_products(query):
    driver = webdriver.Chrome()

    driver.get(f"https://www.flipkart.com/search?q={query}")
    time.sleep(5)

    product_links = driver.find_elements(By.CLASS_NAME, "CGtC98")
    urls = [link.get_attribute("href") for link in product_links]

    print(f"{len(urls)} items found on Flipkart")

    for url in urls:
        try:
            driver.get(url)
            time.sleep(3)

            try:
                read_more_button = driver.find_element(By.XPATH, "//button[contains(text(),'View all features')]")
                driver.execute_script("arguments[0].click();", read_more_button)
                time.sleep(2)
            except:
                print("No 'Read More' button found for this product.")

            Name = driver.find_elements(By.CLASS_NAME, "_6EBuvT")
            name = Name[0].text if Name else "N/A"

            price_element = driver.find_element(By.CSS_SELECTOR, ".Nx9bqj.CxhGGd.yKS4la")
            price_val = price_element.text.strip() if price_element else "N/A"

            img_element = driver.find_element(By.CSS_SELECTOR, "img.DByuf4.IZexXJ.jLEJ7H")
            img_src = img_element.get_attribute("src")

            short_desc_elems = driver.find_elements(By.CLASS_NAME, "_9GQWrZ")
            base_desc_list = [elem.text for elem in short_desc_elems if elem.text.strip()]
            base_desc = base_desc_list[0] if base_desc_list else "N/A"

            full_desc_elems = driver.find_elements(By.CLASS_NAME, "AoD2-N")
            full_desc_list = [elem.text for elem in full_desc_elems if elem.text.strip()]
            full_desc = "\n\n".join(full_desc_list) if full_desc_list else "N/A"

            best_for_elems = driver.find_elements(By.CLASS_NAME, "NTiEl0")
            best_rating_elems = driver.find_elements(By.CLASS_NAME, "_2DdnFS")
            best_for_dict = {}
            if best_for_elems and best_rating_elems:
                for aspect, rating in zip(best_for_elems, best_rating_elems):
                    best_for_dict[aspect.text] = rating.text
            else:
                best_for_dict = "N/A"

            Overall = driver.find_elements(By.CLASS_NAME, "ipqd2A")
            overall_rating = Overall[0].text if Overall else "N/A"

            star_values = driver.find_elements(By.CLASS_NAME, "BArk-j")
            star_dict = {}
            stars = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
            for i in range(len(star_values)):
                if i < len(stars):
                    star_dict[stars[i]] = star_values[i].text

            print(f"Name: {name}")
            print(f"Price: {price_val}")
            print(f"Image URL: {img_src}")
            print(f"Short Descriptions (List): {base_desc_list}")
            print(f"Short Description (First): {base_desc}")
            print("Full Descriptions (All):")
            for i, desc in enumerate(full_desc_list):
                print(f"  Description {i+1}: {desc}")
            print(f"Full Description (Combined): {full_desc}")
            print(f"Best For (Features & Ratings): {best_for_dict}")
            print(f"Overall Rating: {overall_rating}")
            print(f"Star Ratings Breakdown: {star_dict}")
            print(f"Product Link :{url}")
            print("-----------------------------------------------------")

        except Exception as e:
            print(f"Error at {url} — {e}")
            continue

    driver.quit()

# scrape_amazon_products("laptop")
scrape_flipkart_products("laptop")
