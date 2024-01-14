import urllib

import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
import time

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['book_scraping']
#collection = db['books']
collection_logs = db['logs']
collection_urls = db['urls']
collection_data = db['data']



# Function to scrape book URLs
def scrape_urls():
    #page_url = "page-1.html"

    while True:
        url_doc = collection_urls.find_one({'status': 'to_be_scrapped'})
        if url_doc is None:
            break
        collection_urls.update_one({'_id': url_doc['_id']}, {'$set': {'status': 'being_scrapped'}})
        print(url_doc)
        response = requests.get(url_doc['url'])
        soup = BeautifulSoup(response.content, 'html.parser')

        for link in soup.find_all('a'):
            absolute_url = urllib.parse.urljoin(url_doc['url'], link['href'])
            if not collection_urls.find_one({'url': absolute_url}):
                collection_urls.insert_one({'url': absolute_url, 'status': 'to_be_scrapped'})
        collection_data.insert_one({'html': response.text})
        collection_urls.update_one({'_id': url_doc['_id']}, {'$set': {'status': 'scrapped'}})




# Function to scrape book details
def scrape_book_details():
    #books_to_scrape = collection.find({'status': 'to_be_scrapped'})
    books_to_scrape = collection_urls.find({'status': 'to_be_scrapped'})

    for book in books_to_scrape:
        url = book['url']
        collection_urls.update_one({'_id': book['_id']}, {'$set': {'status': 'being_scrapped'}})
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        title = soup.find('h1').text
        price = soup.find('p', class_='price_color').text
        rating = soup.find('p', class_='star-rating')['class'][1]
        genre = soup.find('ul', class_='breadcrumb').find_all('li')[2].text.strip()

        collection_urls.update_one({'_id': book['_id']}, {'$set': {'status': 'scrapped'}})
        collection_data.insert_one({
            'url': url,
            'page': response.text,
            'title': title,
            'price': price,
            'rating': rating,
            'genre': genre,
        })

# Main execution
if __name__ == "__main__":
    # Scrape URLs
    scrape_urls()

    # Scrape book details
    #scrape_book_details()
