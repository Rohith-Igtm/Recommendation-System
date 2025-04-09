from selenium import webdriver
from selenium.webdriver.common.by import By
import time

# Initialize Chrome driver
driver = webdriver.Chrome()
query = "laptops"

driver.get(f"https://www.flipkart.com/search?q={query}")
time.sleep(5)  # Wait for page to load

# Collect product links from search results using the specified class
product_links = driver.find_elements(By.CLASS_NAME, "CGtC98")
urls = [link.get_attribute("href") for link in product_links]

print(len(urls), "items found")

for url in urls:
    try:
        driver.get(url)
        time.sleep(3)  # Allow the product page to load
        
        # Click the "Read More" button if it exists to load full description
        try:
            read_more_button = driver.find_element(By.XPATH, "//button[contains(text(),'View all features')]")
            driver.execute_script("arguments[0].click();", read_more_button)
            time.sleep(2)  # Wait for the content to expand
        except Exception as e:
            # If no read more button, skip
            print("No 'Read More' button found for this product.")
        
        # Extract product name
        Name = driver.find_elements(By.CLASS_NAME, "_6EBuvT")
        name = Name[0].text if Name else "N/A"
        
        # Extract product price
        price = driver.find_elements(By.CLASS_NAME, "Nx9bqj.CxhGGd.yKS4la")
        price_val = price[0].text if price else "N/A"
        
        # Extract image URL using CSS selectors for the image tag
        img_element = driver.find_element(By.CSS_SELECTOR, "img.DByuf4.IZexXJ.jLEJ7H")
        img_src = img_element.get_attribute("src")
        
        # Extract all short descriptions and filter out empty strings
        short_desc_elems = driver.find_elements(By.CLASS_NAME, "_9GQWrZ")
        base_desc_list = [elem.text for elem in short_desc_elems if elem.text.strip()]
        base_desc = base_desc_list[0] if base_desc_list else "N/A"
        
        # Extract all full descriptions and filter out empty strings
        full_desc_elems = driver.find_elements(By.CLASS_NAME, "AoD2-N")
        full_desc_list = [elem.text for elem in full_desc_elems if elem.text.strip()]
        
        # Format the full description with only non-empty elements
        if full_desc_list:
            full_desc = "\n\n".join(full_desc_list)
        else:
            full_desc = "N/A"
        
        # Extract "Best For" details:
        # Using class 'NTiEl0' for aspects and '_2DdnFS' for the corresponding rating
        best_for_elems = driver.find_elements(By.CLASS_NAME, "NTiEl0")
        best_rating_elems = driver.find_elements(By.CLASS_NAME, "_2DdnFS")
        best_for_dict = {}
        if best_for_elems and best_rating_elems:
            for aspect, rating in zip(best_for_elems, best_rating_elems):
                best_for_dict[aspect.text] = rating.text
        else:
            best_for_dict = "N/A"
        
        # Extract overall rating
        Overall = driver.find_elements(By.CLASS_NAME, "ipqd2A")
        overall_rating = Overall[0].text if Overall else "N/A"
        
        # Extract and make star rating dictionary:
        star_values = driver.find_elements(By.CLASS_NAME, "BArk-j")
        star_dict = {}
        stars = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
        for i in range(len(star_values)):
            if i < len(stars):
                star_dict[stars[i]] = star_values[i].text
        
        # Print all extracted info
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
