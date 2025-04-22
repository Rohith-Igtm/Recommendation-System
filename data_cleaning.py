from pymongo import MongoClient
from bs4 import BeautifulSoup
import json

def amazon_structured_data(limit=None):
    print("🔍 Structuring Amazon products...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["product_scraper"]
    source_collection = db["Amazon_product_source"]
    structured_collection = db["Amazon_structured_products"]
    count = 0

    for i, doc in enumerate(source_collection.find({"category": "mobiles"})):
        if limit and i >= limit:
            break

        soup = BeautifulSoup(doc["html_source"], "html.parser")

        try:
            name_tag = soup.find("title")
            price_tag = soup.find("span", {"class": "a-price-whole"})
            overall_rating_tag = soup.find("span", {"class": "a-icon-alt"})
            short_desc_tags = soup.find_all("li", {"class": "a-spacing-mini"})
            star_container = soup.find("div", class_="a-section a-spacing-none a-text-right aok-nowrap")
            script_tag = soup.find("script", {"type": "a-state", "data-a-state": '{"key":"desktop-landing-image-data"}'})

            name = name_tag.text.strip() if name_tag else "N/A"
            price = price_tag.text.strip().replace("₹", "").replace(",", "") if price_tag else "N/A"
            rating = overall_rating_tag.text.strip() if overall_rating_tag else "N/A"

            structured_desc = {}
            short_desc = [desc.text.strip() for desc in short_desc_tags if desc.text.strip()] if short_desc_tags else "N/A"
            for item in short_desc:
                if "】" in item:
                    title, detail = item.split("】", 1)
                    structured_desc[title.strip("【 ")] = detail.strip()

            star_dic = {}
            star_labels = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
            if star_container:
                star_spans = star_container.find_all("span", class_="_cr-ratings-histogram_style_histogram-column-space__RKUAd")
                if len(star_spans) >= 5:
                    for i in range(5):
                        star_dic[star_labels[i]] = star_spans[i].text.strip()
                else:
                    star_dic = "N/A"
            else:
                star_dic = "N/A"

            try:
                if script_tag:
                    data_json = json.loads(script_tag.string)
                    image_url = data_json.get("landingImageUrl", "N/A")
                else:
                    image_url = "N/A"
            except Exception as e:
                print(f"⚠️ Error extracting image URL: {e}")
                image_url = "N/A"

            structured_collection.insert_one({
                "name": name,
                "price": price,
                "rating": rating,
                "image_url": image_url,
                "product_url": doc['product_url'],
                "source": doc['source'],
                "category": doc['category'],
                "scraped_at": doc['scraped_at'],
                "description": structured_desc,
                "star_ratings": star_dic
            })

            count += 1
        except Exception as e:
            print(f"⚠️ Error parsing Amazon document: {e}")
            continue

    print(f"✅ Completed structuring {count} Amazon products.\n")

def flipkart_structured_data(limit=None):
    print("🔍 Structuring Flipkart products...")
    client = MongoClient("mongodb://localhost:27017/")
    db = client["product_scraper"]
    source_collection = db["Flipkart_product_source"]
    structured_collection = db["Flipkart_structured_products"]
    count = 0

    for i, doc in enumerate(source_collection.find({"category": "mobiles"})):
        if limit and i >= limit:
            break

        soup = BeautifulSoup(doc["html_source"], "html.parser")

        try:
            name_tag = soup.find("span", {"class": "VU-ZEz"})
            price_tag = soup.find("div", {"class": "Nx9bqj CxhGGd"})
            overall_rating_tag = soup.find("div", {"class": "ipqd2A"})
            short_desc_tags = soup.find_all("div", {"class": "_9GQWrZ"})
            base_desc_tags = soup.find_all("div", {"class": "AoD2-N"})
            best_for_tags = soup.find_all("div", {"class": "NTiEl0"})
            best_rating_tags = soup.find_all("text", {"class": "_2DdnFS"})
            star_rating_tags = soup.find_all("div", {"class": "BArk-j"})
            image_tag = soup.find("img", {"class": "DByuf4 IZexXJ jLEJ7H"})

            name = name_tag.text.strip() if name_tag else "N/A"
            price = price_tag.text.strip().replace("₹", "").replace(",", "") if price_tag else "N/A"
            rating = overall_rating_tag.text.strip() if overall_rating_tag else "N/A"

            desc_dict = {}
            short_desc_list = [desc.text.strip() for desc in short_desc_tags if desc.text.strip()] if short_desc_tags else "N/A"
            base_desc_list = [desc.text.strip() for desc in base_desc_tags if desc.text.strip()]
            if short_desc_list and base_desc_list and len(short_desc_list) == len(base_desc_list):
                desc_dict = dict(zip(short_desc_list, base_desc_list))
            else:
                desc_dict = "N/A"

            try:
                if best_for_tags and best_rating_tags and len(best_for_tags) == len(best_rating_tags):
                    best_for = {
                        label.text.strip(): rating.text.strip()
                        for label, rating in zip(best_for_tags, best_rating_tags)
                    }
                else:
                    best_for = {}
                    print("ℹ️ 'Best For' info not found or mismatched.")
            except Exception as e:
                print(f"⚠️ Error extracting 'Best For': {e}")
                best_for = {}

            star_dic = {}
            star_labels = ["5 Star", "4 Star", "3 Star", "2 Star", "1 Star"]
            star_rating = [tag.text.strip() for tag in star_rating_tags] if star_rating_tags else "N/A"
            for i in range(len(star_rating_tags)):
                star_dic[star_labels[i]] = star_rating_tags[i].text.strip()

            image_url = image_tag["src"] if image_tag and "src" in image_tag.attrs else "N/A"

            structured_collection.insert_one({
                "name": name,
                "price": price,
                "rating": rating,
                "image_url": image_url,
                "product_url": doc['product_url'],
                "source": doc['source'],
                "category": doc['category'],
                "scraped_at": doc['scraped_at'],
                "description": desc_dict,
                "best_for": best_for,
                "star_ratings": star_dic
            })

            count += 1
        except Exception as e:
            print(f"⚠️ Error parsing Flipkart document: {e}")
            continue

    print(f"✅ Completed structuring {count} Flipkart products.\n")

# Run both functions
amazon_structured_data()
flipkart_structured_data()


