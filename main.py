import urllib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

import time

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['book_scraping']
#collection = db['books']
collection_logs = db['logs']
collection_urls = db['urls']
collection_data = db['data']

#fonction pour extraire la base de l'url
def extraire_url_de_base(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return base_url

# Function to scrape book URLs
def scrape_urls():
    #page_url = "page-1.html"

    while True:
        response = None
        try:
            url_doc = collection_urls.find_one({'status': 'to_be_scrapped'})
            if url_doc is None:
                print("there are no urls to scrap!")
                break
            scope = extraire_url_de_base(url_doc['url'])
            collection_urls.update_one({'_id': url_doc['_id']}, {'$set': {'status': 'being_scrapped'}})
            response = requests.get(url_doc['url'])
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.find_all('a'):
                absolute_url = urllib.parse.urljoin(url_doc['url'], link['href'])
                scope_scrapped = extraire_url_de_base(absolute_url)
                # Tester si l'url n'est pas encore enregistré en base, et si on est dans le même scope
                #if absolute_url.startswith(scope):
                #    collection_urls.update
                if not collection_urls.find_one({'url': absolute_url}) :
                    collection_urls.insert_one({'url': absolute_url, 'status': 'to_be_scrapped'})
            insert_one_document(response, url_doc)
            collection_urls.update_one({'_id': url_doc['_id']}, {'$set': {'status': 'scrapped'}})
        except :
            collection_urls.update_one({'_id': url_doc['_id']}, {'$set': {'status': 'error_scrapping'}})

        finally:
            if url_doc is None:
                exit(1)
            collection_logs.insert_one({'url':url_doc['url'], 'status':response.status_code,'reason':response.reason, "last_update": datetime.now()})


def insert_one_document(response,url_doc):
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('title')
    h1 = soup.find_all('h1')
    h2 = soup.find_all('h2')
    b = soup.find_all('b')
    em = soup.find_all('em')
    strong = soup.find_all("strong")
    collection_data.insert_one({'url':url_doc['url'] ,
                                'html': response.text,
                                "title":title,
                                "h1":h1,
                                "h2":h2,
                                "b":b,
                                "em":em,
                                "strong":strong})

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
