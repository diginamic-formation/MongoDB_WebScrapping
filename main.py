import urllib
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime, timedelta
import time



# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['book_scraping']
collection_logs = db['logs']
collection_urls = db['urls']
collection_data = db['data']


# Function to scrape book URLs
def scrape_urls():
    # page_url = "page-1.html"
    still_scrapping = True
    print("Start scrapping !")
    counter = 0
    while still_scrapping:
        response = None
        try:
            url_doc = get_url_to_scrap()
            if url_doc:
                scope = url_doc['scope']
                if counter == 0:
                    print("Scope to scrap : ", scope)
                counter += 1
                print("scrapping : ", url_doc['url'])
                response = requests.get(url_doc['url'])
                soup = BeautifulSoup(response.content, 'html.parser')
                # insert all urls found int the html page scrapped
                insert_new_urls(url_doc, scope, soup)
                # insert the page web content and differents important fields
                insert_one_document(url_doc, response, soup)
                # upadte the status of the url => set it on "scrapped"
                collection_urls.update_one({'_id': url_doc['_id']},
                                           {'$set': {'status': 'scrapped', 'last_update': datetime.now()}})
            else:
                still_scrapping = False
        except Exception as e:
            print(f"Une erreur s'est produite : {e}")
            collection_urls.update_one({'_id': url_doc['_id']}, {
                '$set': {'status': 'error_scrapping', 'last_update': datetime.now(),
                         'next_scrap_date': datetime.now() + timedelta(minutes=10)}},
                                       {"$inc": {"nombre_de_trentative": 1}})
        finally:
            if url_doc:
                collection_logs.insert_one(
                    {'url': url_doc['url'], 'status': response.status_code, 'reason': response.reason,
                     "last_update": datetime.now()})


def get_url_to_scrap():
    wait = True
    while wait:

        # possible_urls, to check if there is a possible urls to scrap in case of there is no url_doc available immediately
        possible_urls = collection_urls.find_one({"$or": [{'status': 'to_be_scrapped'},
                                                          {'status': 'error_scrapping','nombre_de_trentative': {"$lt": 10}},
                                                          {'status': 'being_scrapped'}]})

        # url_doc, contains the url to scrap, it is selected with the strategy :
        # all the urls with status "to_be_scrapped", (never scrapped)
        # urls with errors but it is possible to scrap it again ( next_scrap_date is reached)
        # urls being scrapped by another scrapper but il took more than 10 minutes (we consider there is some trouble with the other scrapper)
        url_doc = collection_urls.find_one_and_update({"$or": [{'status': 'to_be_scrapped'},
                                                               {'status': 'error_scrapping','next_scrap_date': {"$lt": datetime.now()},'nombre_de_trentative': {"$lt": 10}},
                                                               {'status': 'being_scrapped', 'last_update': {"$lt": datetime.now() - timedelta(minutes=10)}}]},
                                                      {'$set': {'status': 'being_scrapped',"last_update": datetime.now()}})

        # if we foud an url, we stop waiting and strat scraping this url
        if url_doc:
            wait = False

        # if there is no possible url to scrap, it is time to stop the scrapper
        if url_doc is None and possible_urls is None:
            wait = False

        # if the is no url to scrap immediately but there is possible ones, we can wait 10 seconds and retry again
        if url_doc is None and possible_urls:
            print("Waiting 10 seconds for possible urls")
            time.sleep(10)

    return url_doc


def insert_one_document(url_doc, response, soup):
    title = soup.find('title').text
    h1 = soup.find('h1').text
    h2 = list(map(lambda x: x.text, soup.find_all('h2')))
    b = list(map(lambda x: x.text, soup.find_all('b')))
    em = list(map(lambda x: x.text, soup.find_all('em')))
    strong = list(map(lambda x: x.text, soup.find_all('strong')))
    collection_data.insert_one(
        {'url': url_doc['url'], 'html': response.text, "title": title, "h1": h1, "h2": h2, "b": b, "em": em,
         "strong": strong, "last_update": datetime.now()})


def insert_new_urls(url_doc, scope, soup):
    for link in soup.find_all('a'):
        absolute_url = urllib.parse.urljoin(url_doc['url'], link['href'])
        # Tester si l'url n'est pas encore enregistré en base, et si on est dans le même scope
        if absolute_url.startswith(scope):
            collection_urls.update_one(
                {'url': absolute_url},
                {"$setOnInsert": {'url': absolute_url, 'status': 'to_be_scrapped', 'scope': scope}},
                upsert=True
            )


# Main execution
if __name__ == "__main__":
    scrape_urls()
