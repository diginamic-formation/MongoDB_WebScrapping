from pymongo import MongoClient

# MongoDB setup
client = MongoClient('localhost', 27017)
db = client['book_scraping']
collection = db['books']

# Function to read and display data
def display_data():
    # Fetch all documents in the collection
    books = collection.find()

    for book in books:
        print(f"Title: {book.get('title', 'N/A')}")
        print(f"Genre: {book.get('genre', 'N/A')}")
        print(f"Price: {book.get('price', 'N/A')}")
        print(f"Rating: {book.get('rating', 'N/A')}")
        print(f"URL: {book.get('url', 'N/A')}")
        print(f"Status: {book.get('status', 'N/A')}")
        print("-" * 50)

# Run the display function
if __name__ == "__main__":
    display_data()
