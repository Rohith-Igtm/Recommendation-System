from selenium_test_flipkart import scrape_flipkart
from selenium_test_amazon import scrape_amazon

# Set the number of pages you want to scrape
pages_to_scrape = 5

# Define the queries for different product types (e.g., laptops and mobiles)
queries = ["laptops","mobiles"]

# Initialize an empty structure for the combined data
combined_data = {}

for query in queries:
    print(f"\n🔍 Scraping data for '{query}'...\n")
    # Scrape data from Flipkart and Amazon for the given query
    flipkart_data = scrape_flipkart(query, pages_to_scrape)
    amazon_data   = scrape_amazon(query, pages_to_scrape)
    
    # Combine results for this query
    combined_data[query] = {
        "flipkart": flipkart_data,
        "amazon": amazon_data
    }
    
    total = len(flipkart_data) + len(amazon_data)
    print(f"Total {total} '{query}' items found across both sources.")

# Now, you can print or further process combined_data
print("\n\nCombined Data:")
print(combined_data)
print(scrape_amazon.all_products)
