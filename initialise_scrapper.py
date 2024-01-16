import sys
from pymongo import MongoClient
import time

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['book_scraping']
collection_urls = db['urls']



#lecture des paramêtres

if len(sys.argv) < 3:
    print("Vous devez fournir une URL à scrapper et le scope du scrapper !")
    exit(1)
url_to_scrap = sys.argv[1]
scope = sys.argv[2]

print("Url à scrapper : ",url_to_scrap)
print("Scope : ",scope)

# Enregistrement de l'url dans la collection URLs

collection_urls.insert_one({'url': url_to_scrap,'status': 'to_be_scrapped','scope':scope})
