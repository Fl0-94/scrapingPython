import os
import re
import csv
from bs4 import BeautifulSoup
import requests



def get_category_urls(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    category_urls = ['http://books.toscrape.com/' + a['href'] for a in soup.select('.side_categories a')[1:]]
    return category_urls

def get_book_urls(category_url):
    book_urls = []
    page_number = 1
    while True:
        paginated_url = category_url.replace('index.html', f'page-{page_number}.html')
        response = requests.get(paginated_url)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.content, 'html.parser')
        product_containers = soup.find_all('article', class_='product_pod')
        if not product_containers:
            break
        for container in product_containers:
            book_urls.append('http://books.toscrape.com/catalogue/' + container.find('h3').find('a')['href'][9:])
        page_number += 1
    return book_urls

def get_book_data(book_url):
    response = requests.get(book_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    product_page_url = book_url
    
    upc_element = soup.find('th', string='UPC')
    upc = upc_element.find_next_sibling('td').text if upc_element else 'UPC non trouvé'
    
    title_element = soup.find('h1')
    title = title_element.text if title_element else 'Titre non trouvé'
    
    price_including_tax_element = soup.find('th', string='Price (incl. tax)')
    price_including_tax = price_including_tax_element.find_next_sibling('td').text if price_including_tax_element else 'N/A'
    
    price_excluding_tax_element = soup.find('th', string='Price (excl. tax)')
    price_excluding_tax = price_excluding_tax_element.find_next_sibling('td').text if price_excluding_tax_element else 'N/A'
    
    availability_element = soup.find('th', string='Availability')
    availability_text = availability_element.find_next_sibling('td').text if availability_element else 'N/A'
    number_available = int(re.search(r'\d+', availability_text).group()) if availability_element else 0
    
    product_description_element = soup.find('meta', {'name': 'description'})
    product_description = product_description_element['content'].strip() if product_description_element else 'N/A'
    
    category_element = soup.find('ul', class_='breadcrumb')
    category = category_element.find_all('li')[2].text.strip() if category_element else 'N/A'
    
    review_rating_element = soup.find('p', class_='star-rating')
    review_rating = review_rating_element['class'][1] if review_rating_element else 'N/A'
    
    image_element = soup.find('img')
    image_url = image_element['src'].replace('../../', 'http://books.toscrape.com/') if image_element else 'N/A'
    
    return [product_page_url, upc, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, image_url]

def download_image(image_url, title, category):
    if image_url == 'N/A':
        return
    response = requests.get(image_url)
    image_name = title.replace(' ', '_').replace('/', '_') + '.jpg'
    category_folder = os.path.join('images', category)
    if not os.path.exists(category_folder):
        os.makedirs(category_folder)
    with open(os.path.join(category_folder, image_name), 'wb') as file:
        file.write(response.content)

def create_csv_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)

def main():
    base_url = 'https://books.toscrape.com/index.html'
    category_urls = get_category_urls(base_url)

    if not os.path.exists('images'):
        os.makedirs('images')
    
    csv_directory = 'csv_files'
    create_csv_directory(csv_directory)

    for category_url in category_urls:
        category_name = category_url.split('/')[-2]
        book_urls = get_book_urls(category_url)
        csv_filename = os.path.join(csv_directory, f'{category_name}_books_data.csv')
        with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['product_page_url', 'universal_product_code (upc)', 'title', 'price_including_tax', 'price_excluding_tax', 'number_available', 'product_description', 'category', 'review_rating', 'image_url'])
            for book_url in book_urls:
                book_data = get_book_data(book_url)
                writer.writerow(book_data)
                if book_data[-1] != 'N/A':
                    download_image(book_data[-1], book_data[2], category_name)

if __name__ == '__main__':
    main()