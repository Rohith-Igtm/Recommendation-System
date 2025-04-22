from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from datetime import datetime 
import time

def scrape_flipkart(query,pages):
        option=webdriver.ChromeOptions()
        option.add_argument("--disable-blink-features=AutomationControlled")
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)

        # Initialize MongoDB client
        client=MongoClient("mongodb://localhost:27017/")
        db=client["product_scraper"]
        collection=db["Flipkart_product_source"]
        
        total_num=0
        for page in range(1,pages+1):
            driver.get(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page={page}")
            time.sleep(5)

            # Collect product links from search results
            product_links = driver.find_elements(By.CLASS_NAME, "CGtC98")
            urls = [link.get_attribute("href") for link in product_links]
            total_num+=len(urls)
            
            for url in urls:
                try:
                        driver.get(url)
                        time.sleep(3)
                        html_source=driver.page_source

                        product_doc={
                              "product_url":url,
                              "html_source":html_source,
                              "scraped_at": datetime.utcnow().isoformat() + "Z",
                              "source": "flipkart",
                              "category": query  # for example, "mobiles" or "laptops"      
                        }
                        collection.insert_one(product_doc)
                        print(f"Inserted product data for URL: {url}")
                except Exception as e:
                        print(f"Error processing URL {url}: {e}")
                        continue
        driver.quit()
        print(f"Total items found across all pages: {total_num}")

def scrape_amazon(query,pages):
        option=webdriver.ChromeOptions()
        option.add_argument("--disable-blink-features=AutomationControlled")
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=option)

        # Initialize MongoDB client
        client=MongoClient("mongodb://localhost:27017/")
        db=client["product_scraper"]
        collection=db["Amazon_product_source"]
        
        total_num=0
        for page in range(1,pages+1):
            driver.get(f"https://www.amazon.in/s?k={query}&page={page}&xpid=1gmyaZMQ8_VPN&crid=1NN0AVEYQUO1Q&qid=1744264667&sprefix=%2Caps%2C415&ref=sr_pg_{page}")
            time.sleep(5)

            # Collect product links from search results
            product_links = driver.find_elements(By.CSS_SELECTOR, 'a.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
            urls = [link.get_attribute("href") for link in product_links if link.get_attribute("href")]
            total_num+=len(urls)
            
            for url in urls:
                try:
                        driver.get(url)
                        time.sleep(3)
                        html_source=driver.page_source

                        product_doc={
                              "product_url":url,
                              "html_source":html_source,
                              "scraped_at": datetime.utcnow().isoformat() + "Z",
                              "source": "amazon",
                              "category": query  # for example, "mobiles" or "laptops"      
                        }
                        collection.insert_one(product_doc)
                        print(f"Inserted product data for URL: {url}")
                except Exception as e:
                        print(f"Error processing URL {url}: {e}")
                        continue
        driver.quit()
        print(f"Total items found across all pages: {total_num}")

scrape_amazon("mobiles",5)
scrape_flipkart("mobiles",5)
                
        
        
