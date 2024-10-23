import requests
from bs4 import BeautifulSoup
import csv
import re

url = 'https://books.toscrape.com/catalogue/doctor-sleep-the-shining-2_686/index.html'
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

product_page_url = url
upc = soup.find('th', string='UPC').find_next_sibling('td').text
title = soup.find('h1').text
price_including_tax = soup.find('th', string='Price (incl. tax)').find_next_sibling('td').text
price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next_sibling('td').text
availability_text = soup.find('th', string='Availability').find_next_sibling('td').text
price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next_sibling('td').text
number_available = int(re.search(r'\d+', availability_text).group())
product_description = soup.find('meta', {'name': 'description'})['content'].strip()
category = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
review_rating = soup.find('p', class_='star-rating')['class'][1]
image_url = soup.find('img')['src']
image_url = image_url.replace('../../', 'http://books.toscrape.com/')

with open('product_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['product_page_url', 'universal_product_code (upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'])
    writer.writerow([product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url])
