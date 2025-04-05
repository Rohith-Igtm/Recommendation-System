from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import os
import time

driver = webdriver.Chrome()
query='mobiles'
file=0
for i in range(1,5):
    driver.get(f"https://www.flipkart.com/search?q={query}&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&p%5B%5D=facets.rating%255B%255D%3D4%25E2%2598%2585%2B%2526%2Babove&page={i}")

    elems = driver.find_elements(By.CLASS_NAME, 'tUxRFH')

    print(f"{len(elems)}items found")
    for elem in elems:
        d=elem.get_attribute("outerHTML")
        with open(f"data/{query}_{file}.html","w",encoding="utf-8") as f:
            f.write(d)
            file+=1
driver.close()



# for file in os.listdir("data"):
#     with open(f'data/{file}') as f:
#         html_doc=f.read()
#     soup=BeautifulSoup(html_doc,'lxml')
# for i in soup.find_all('h2'):
#     print("Name  ",i)


