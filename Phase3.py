import os
import requests
import csv
from bs4 import BeautifulSoup
import re

def get_book_urls(category_url):
    book_urls = []
    while category_url:
        response = requests.get(category_url)
        soup = BeautifulSoup(response.content, 'html.parser')
        for h3 in soup.find_all('h3'):
            book_urls.append('http://books.toscrape.com/catalogue' + h3.find('a')['href'][8:])
        next_button = soup.find('li', class_='next')
        category_url = 'http://books.toscrape.com/catalogue/' + next_button.find('a')['href'] if next_button else None
    return book_urls

def get_book_data(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    product_page_url = book_url
    upc = soup.find('th', string='UPC').find_next_sibling('td').text
    title = soup.find('h1').text
    price_including_tax = soup.find('th', string='Price (incl. tax)').find_next_sibling('td').text
    price_excluding_tax = soup.find('th', string='Price (excl. tax)').find_next_sibling('td').text
    availability_text = soup.find('th', string='Availability').find_next_sibling('td').text
    number_available = int(re.search(r'\d+', availability_text).group())
    product_description = soup.find('meta', {'name': 'description'})['content'].strip()
    category = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()
    review_rating = soup.find('p', class_='star-rating')['class'][1]
    image_url = soup.find('img')['src']
    image_url = image_url.replace('../../', 'http://books.toscrape.com/')
    return [product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

def download_image(image_url, title):
    response = requests.get(image_url)
    image_name = title.replace(' ', '_').replace('/', '_') + '.jpg'
    with open(os.path.join('images', image_name), 'wb') as file:
        file.write(response.content)

category_url = 'https://books.toscrape.com/catalogue/category/books/horror_31/index.html'
book_urls = get_book_urls(category_url)

if not os.path.exists('images'):
    os.makedirs('images')

with open('category_books_data.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['product_page_url', 'universal_product_code (upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'])
    for book_url in book_urls:
        book_data = get_book_data(book_url)
        writer.writerow(book_data)
        download_image(book_data[-1], book_data[2])