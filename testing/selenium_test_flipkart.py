from selenium import webdriver
from selenium.webdriver.common.by import By
import time

def scrape_flipkart(query,p):
        # Initialize Chrome driver
        driver = webdriver.Chrome()
        driver.maximize_window()
        all_products = []
        tottal_items = 0

        for i in range(1,p+1):
            driver.get(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={i}")
            time.sleep(5)  # Wait for page to load

            # Collect product links from search results
            product_links = driver.find_elements(By.CLASS_NAME, "CGtC98")
            urls = [link.get_attribute("href") for link in product_links]

            print(len(urls), "items found in Flipkart")


            for url in urls:
                try:
                    driver.get(url)
                    time.sleep(3)

                    try:
                        read_more_button = driver.find_element(By.XPATH, "//button[contains(text(),'View all features')]")
                        driver.execute_script("arguments[0].click();", read_more_button)
                        time.sleep(2)
                    except:
                        print("No 'Read More' button found.")

                    # Extract product name
                    try:
                        name_elem = driver.find_element(By.CLASS_NAME, "_6EBuvT")
                        name = name_elem.text.strip()
                    except:
                        name = "N/A"

                    # Price
                    try:
                        price_elem = driver.find_element(By.CSS_SELECTOR, ".hl05eU .Nx9bqj ")
                        price_val = price_elem.text.strip()
                    except:
                        price_val = "N/A"

                    # Image URL
                    try:
                        img_elem = driver.find_element(By.CSS_SELECTOR, "img.DByuf4.IZexXJ.jLEJ7H")
                        img_src = img_elem.get_attribute("src")
                    except:
                        img_src = "N/A"

                    # Short description
                    try:
                        short_desc_elems = driver.find_elements(By.CLASS_NAME, "_9GQWrZ")
                        base_desc_list = [elem.text for elem in short_desc_elems if elem.text.strip()]
                    except:
                        base_desc_list = []
                    base_desc = base_desc_list[0] if base_desc_list else "N/A"

                    # Full description
                    try:
                        full_desc_elems = driver.find_elements(By.CLASS_NAME, "AoD2-N")
                        full_desc_list = [elem.text for elem in full_desc_elems if elem.text.strip()]
                        full_desc = "\n\n".join(full_desc_list) if full_desc_list else "N/A"
                    except:
                        full_desc_list = []
                        full_desc = "N/A"

                    # Best for and ratings
                    try:
                        best_for_elems = driver.find_elements(By.CLASS_NAME, "NTiEl0")
                        best_rating_elems = driver.find_elements(By.CLASS_NAME, "_2DdnFS")
                        best_for_dict = {
                            aspect.text: rating.text
                            for aspect, rating in zip(best_for_elems, best_rating_elems)
                        } if best_for_elems and best_rating_elems else "N/A"
                    except:
                        best_for_dict = "N/A"

                    # Overall rating
                    try:
                        Overall = driver.find_elements(By.CLASS_NAME, "ipqd2A")
                        overall_rating = Overall[0].text if Overall else "N/A"
                    except:
                        overall_rating = "N/A"

                    # Star ratings
                    try:
                        star_values = driver.find_elements(By.CLASS_NAME, "BArk-j")
                        stars = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
                        star_dict = {
                            stars[i]: star_values[i].text
                            for i in range(min(len(star_values), len(stars)))
                        }
                    except:
                        star_dict = {}

                    # Store product data
                    product_data = {
                        "name": name,
                        "price": price_val,
                        "image": img_src,
                        "short_desc": base_desc_list,
                        "full_desc": full_desc,
                        "best_for": best_for_dict,
                        "overall_rating": overall_rating,
                        "star_ratings": star_dict,
                        "link": url
                    }

                    all_products.append(product_data)

                    # Print summary
                    print(f"✅ Scraped: {name} | Price: {price_val}")
                    print("-----------------------------------------------------")

                except Exception as e:
                    print(f"❌ Error at {url} — {e}")
                    continue

        driver.quit()
        return all_products




