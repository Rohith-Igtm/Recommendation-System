from bs4 import BeautifulSoup
import requests

product_name=input("Enter the Product Name :")

source=requests.get(f'https://www.flipkart.com/search?q={product_name}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove').text

soup=BeautifulSoup(source,'lxml')


def landscape(soup):
    names = []
    ratings = []
    base_prices = []

    # Extract base prices
    for div in soup.find_all('div', class_='Nx9bqj _4b5DiR'):
        base_prices.append(div.text.strip())

    # Extract product names
    for div in soup.find_all('div', class_='KzDlHZ'):
        names.append(div.text.strip())

    # Extract ratings
    for span in soup.find_all('span', class_='Wphh3N'):
        ratings.append(span.text.strip())

    # Ensure all lists have the same length
    min_length = min(len(names), len(base_prices), len(ratings))
    names = names[:min_length]
    base_prices = base_prices[:min_length]
    ratings = ratings[:min_length]

    # Print and store the results
    results = []
    for i in range(min_length):
        product_info = {
            "Model": names[i],
            "Price": base_prices[i],
            "Rating": ratings[i]
        }
        results.append(product_info)
        print(f"Model - {names[i]}")
        print(f"Price - {base_prices[i]}")
        print(f"Rating - {ratings[i]}")
        print()

    return results


def potrait(soup):

    names = []
    ratings = []
    base_prices = []

    for div in soup.find_all('div', class_='Nx9bqj'):
        base_prices.append(div.text.strip())

    for div in soup.find_all('div', class_='syl9yP'):
        names.append(div.text.strip())


    for span in soup.find_all('div', class_='UkUFwK'):
        ratings.append(span.text.strip())


    min_length = min(len(names), len(base_prices), len(ratings))
    names = names[:min_length]
    base_prices = base_prices[:min_length]
    ratings = ratings[:min_length]


    results = []
    for i in range(min_length):
        product_info = {
            "Model": names[i],
            "Price": base_prices[i],
            "offers": ratings[i]
        }
        results.append(product_info)
        print(f"Model - {names[i]}")
        print(f"Price - {base_prices[i]}")
        print(f"offers - {ratings[i]}")
        print()

    return results

if soup.find('div','tUxRFH'):
    print(landscape(soup))
else:
    print(potrait(soup))